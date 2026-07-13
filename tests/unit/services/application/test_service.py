from __future__ import annotations

import pytest

from boc_mcp.models.common import ListResult
from boc_mcp.services.application.models import ApplicationSummary
from boc_mcp.services.application.service import ApplicationService


class FakeClient:
    def __init__(self) -> None:
        self.calls: list[tuple[str, str, dict | None]] = []
        self._payload: dict = {}

    def seed(self, key: str, resp) -> None:
        self._payload[key] = resp

    async def get(self, path: str, *, params: dict | None = None):
        self.calls.append(("get", path, params))
        for k, v in self._payload.items():
            if k in path:
                return v
        return {}

    async def post(self, path: str, *, json: dict | None = None):
        self.calls.append(("post", path, json))
        return {}


@pytest.mark.asyncio
async def test_get_app_returns_data():
    c = FakeClient()
    c.seed("/applications/42", {"data": {"id": 42, "name": "myapp"}})
    svc = ApplicationService(c)
    r = await svc.get(42)
    assert r["id"] == 42
    assert r["name"] == "myapp"
    method, path, params = c.calls[-1]
    assert method == "get"
    assert path == "/applications/42"
    assert params is None


@pytest.mark.asyncio
async def test_get_app_returns_raw_when_no_data_key():
    c = FakeClient()
    c.seed("/applications/7", {"id": 7, "name": "raw"})
    svc = ApplicationService(c)
    r = await svc.get(7)
    assert r["id"] == 7


@pytest.mark.asyncio
async def test_list_apps_legacy_pagination():
    c = FakeClient()
    c.seed(
        "/bocApplication/projects/list",
        {
            "rows": [{"id": 1, "name": "a1"}, {"id": 2, "name": "a2"}],
            "totalCount": 2,
            "currPageNum": 1,
            "pageSize": 20,
            "pageCount": 1,
        },
    )
    svc = ApplicationService(c)
    r = await svc.list()
    assert isinstance(r, ListResult)
    assert r.total == 2
    assert len(r.items) == 2
    assert isinstance(r.items[0], ApplicationSummary)
    assert r.items[0].id == 1


@pytest.mark.asyncio
async def test_list_apps_direct_data_list():
    c = FakeClient()
    c.seed("/bocApplication/projects/list", {"data": [{"id": 9, "name": "x"}]})
    svc = ApplicationService(c)
    r = await svc.list()
    assert len(r.items) == 1
    assert r.items[0].id == 9


@pytest.mark.asyncio
async def test_list_apps_passes_params():
    c = FakeClient()
    c.seed(
        "/bocApplication/projects/list",
        {"rows": [], "totalCount": 0, "currPageNum": 2, "pageSize": 10, "pageCount": 0},
    )
    svc = ApplicationService(c)
    await svc.list(cluster_id="c-1", project_name="demo", page=2, page_size=10)
    _method, _path, params = c.calls[-1]
    assert params is not None
    assert params["clusterId"] == "c-1"
    assert params["projectName"] == "demo"
    assert params["currPageNum"] == 2
    assert params["pageSize"] == 10


@pytest.mark.asyncio
async def test_list_apps_skips_none_filters():
    c = FakeClient()
    c.seed("/bocApplication/projects/list", {"rows": [], "totalCount": 0})
    svc = ApplicationService(c)
    await svc.list()
    _method, _path, params = c.calls[-1]
    assert params is not None
    assert "clusterId" not in params
    assert "projectName" not in params
