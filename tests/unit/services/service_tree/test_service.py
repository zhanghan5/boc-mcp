from __future__ import annotations

import pytest

from boc_mcp.services.service_tree.models import ServiceTreeNode
from boc_mcp.services.service_tree.service import ServiceTreeService


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
async def test_get_tree():
    c = FakeClient()
    c.seed("/service-tree", {"data": [{"id": 1, "name": "root", "hasChildren": True}]})
    svc = ServiceTreeService(c)
    r = await svc.get_tree()
    assert isinstance(r, list)
    assert len(r) == 1
    assert isinstance(r[0], ServiceTreeNode)
    assert r[0].id == 1
    assert r[0].name == "root"


@pytest.mark.asyncio
async def test_get_tree_direct_list_response():
    c = FakeClient()
    c.seed("/service-tree", [{"id": 2, "name": "n2"}])
    svc = ServiceTreeService(c)
    r = await svc.get_tree()
    assert len(r) == 1
    assert r[0].id == 2


@pytest.mark.asyncio
async def test_get_tree_with_params():
    c = FakeClient()
    c.seed("/service-tree", {"data": [{"id": 3, "name": "child"}]})
    svc = ServiceTreeService(c)
    await svc.get_tree(p_type="cluster", pid=1, type_="node")
    _method, _path, params = c.calls[-1]
    assert params is not None
    assert params["pType"] == "cluster"
    assert params["pid"] == 1
    assert params["type"] == "node"


@pytest.mark.asyncio
async def test_get_tree_skips_none_params():
    c = FakeClient()
    c.seed("/service-tree", {"data": []})
    svc = ServiceTreeService(c)
    await svc.get_tree()
    _method, _path, params = c.calls[-1]
    assert params == {}
