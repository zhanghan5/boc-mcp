import pytest

from boc_mcp.models.common import ListResult
from boc_mcp.services.scan.models import ScanReport, ScanStrategy
from boc_mcp.services.scan.service import ScanService


class FakeClient:
    def __init__(self):
        self.calls = []
        self.payloads = {}

    def seed(self, key, resp):
        self.payloads[key] = resp

    async def get(self, path, *, params=None):
        self.calls.append(("get", path, params))
        for k, v in self.payloads.items():
            if k in path:
                return v
        return {}

    async def post(self, path, *, json=None):
        self.calls.append(("post", path, json))
        for k, v in self.payloads.items():
            if k in path:
                return v
        return {"rows": [], "totalCount": 0, "currPageNum": 1, "pageSize": 20, "pageCount": 0}


@pytest.mark.asyncio
async def test_list_strategies():
    c = FakeClient()
    c.seed(
        "/strategy/v3.3/list",
        {
            "rows": [{"id": 1, "name": "s1"}, {"id": 2, "name": "s2"}],
            "totalCount": 2,
            "currPageNum": 1,
            "pageSize": 20,
            "pageCount": 1,
        },
    )
    svc = ScanService(c)
    r = await svc.list_strategies()
    assert isinstance(r, ListResult)
    assert r.total == 2
    assert len(r.items) == 2
    assert isinstance(r.items[0], ScanStrategy)
    assert r.items[0].name == "s1"


@pytest.mark.asyncio
async def test_list_strategies_empty():
    c = FakeClient()
    svc = ScanService(c)
    r = await svc.list_strategies()
    assert r.total == 0
    assert r.items == []


@pytest.mark.asyncio
async def test_list_strategies_pagination_body():
    c = FakeClient()
    c.seed(
        "/strategy/v3.3/list",
        {
            "rows": [],
            "totalCount": 0,
            "currPageNum": 3,
            "pageSize": 50,
            "pageCount": 0,
        },
    )
    svc = ScanService(c)
    await svc.list_strategies(page=3, page_size=50)
    body = c.calls[-1][2]
    assert body["currPageNum"] == 3
    assert body["pageSize"] == 50


@pytest.mark.asyncio
async def test_get_report():
    c = FakeClient()
    c.seed("/report/v3.3/detail/42", {"data": {"id": 42, "name": "r1", "high": 3}})
    svc = ScanService(c)
    r = await svc.get_report(42)
    assert r["id"] == 42
    assert r["name"] == "r1"


@pytest.mark.asyncio
async def test_get_report_no_data_key():
    c = FakeClient()
    c.seed("/report/v3.3/detail/99", {"id": 99, "name": "raw"})
    svc = ScanService(c)
    r = await svc.get_report(99)
    assert r["id"] == 99


@pytest.mark.asyncio
async def test_list_reports():
    c = FakeClient()
    c.seed(
        "/report/v3.3/list",
        {
            "rows": [{"id": 1, "name": "r1"}, {"id": 2, "name": "r2"}],
            "totalCount": 2,
            "currPageNum": 1,
            "pageSize": 20,
            "pageCount": 1,
        },
    )
    svc = ScanService(c)
    r = await svc.list_reports()
    assert isinstance(r, ListResult)
    assert r.total == 2
    assert len(r.items) == 2
    assert isinstance(r.items[0], ScanReport)


@pytest.mark.asyncio
async def test_list_reports_empty():
    c = FakeClient()
    svc = ScanService(c)
    r = await svc.list_reports()
    assert r.total == 0
    assert r.items == []


@pytest.mark.asyncio
async def test_list_reports_direct_data_array():
    c = FakeClient()
    c.seed("/report/v3.3/list", {"data": [{"id": 1, "name": "d1"}]})
    svc = ScanService(c)
    r = await svc.list_reports()
    assert len(r.items) == 1
    assert r.items[0].id == 1
    assert r.total == 1


@pytest.mark.asyncio
async def test_list_strategies_direct_data_array():
    c = FakeClient()
    c.seed("/strategy/v3.3/list", {"data": [{"id": 5, "name": "d1"}]})
    svc = ScanService(c)
    r = await svc.list_strategies()
    assert len(r.items) == 1
    assert r.items[0].id == 5


@pytest.mark.asyncio
async def test_list_reports_pagination_body():
    c = FakeClient()
    c.seed("/report/v3.3/list", {"rows": [], "totalCount": 0})
    svc = ScanService(c)
    await svc.list_reports(page=2, page_size=10)
    body = c.calls[-1][2]
    assert body["currPageNum"] == 2
    assert body["pageSize"] == 10
