from __future__ import annotations

import pytest

from boc_mcp.services.monitor.service import MonitorService, _merge


class _FakeClient:
    def __init__(self, data_response):
        self._data = data_response
        self.calls: list[tuple[str, dict]] = []

    async def get(self, path, *, params=None):
        return {"state": "success", "data": self._data}

    async def post(self, path, *, json=None):
        self.calls.append((path, json or {}))
        return {"state": "success", "data": self._data}


@pytest.mark.asyncio
async def test_monitor_methods_return_dict():
    client = _FakeClient({"metrics": [1, 2, 3]})
    svc = MonitorService(client)
    assert await svc.get_project_status() == {"metrics": [1, 2, 3]}
    assert await svc.batch_project() == {"metrics": [1, 2, 3]}
    assert await svc.batch_project_status() == {"metrics": [1, 2, 3]}
    assert await svc.get_app() == {"metrics": [1, 2, 3]}
    assert await svc.batch_app() == {"metrics": [1, 2, 3]}
    assert await svc.get_pod() == {"metrics": [1, 2, 3]}
    assert await svc.batch_container() == {"metrics": [1, 2, 3]}
    assert await svc.batch_pod() == {"metrics": [1, 2, 3]}
    assert len(client.calls) == 8


@pytest.mark.asyncio
async def test_monitor_returns_empty_dict_when_data_not_dict():
    client = _FakeClient("not a dict")
    svc = MonitorService(client)
    result = await svc.get_project_status(cluster_id=1)
    assert result == {}


def test_merge_excludes_none_and_overrides():
    merged = _merge({"a": 1, "b": None}, {"c": 3, "d": None})
    assert merged == {"a": 1, "c": 3}
