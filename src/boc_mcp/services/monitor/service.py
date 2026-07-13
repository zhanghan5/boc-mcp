from __future__ import annotations

from typing import Any

from boc_mcp.services.base import BaseService


class MonitorService(BaseService):
    async def get_project_status(
        self,
        application_id: int | None = None,
        cluster_id: int | None = None,
        project_id: int | None = None,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        body = _merge(
            {"applicationId": application_id, "clusterId": cluster_id, "projectId": project_id},
            params,
        )
        resp = await self._post("/query/v1.8/queryProjectStatus", json=body)
        data = resp.get("data")
        return data if isinstance(data, dict) else {}

    async def batch_project(self, params: dict[str, Any] | None = None) -> dict[str, Any]:
        body = dict(params) if params else {}
        resp = await self._post("/query/v1.8/queryBatchProjectMonitor", json=body)
        data = resp.get("data")
        return data if isinstance(data, dict) else {}

    async def batch_project_status(self, params: dict[str, Any] | None = None) -> dict[str, Any]:
        body = dict(params) if params else {}
        resp = await self._post("/query/v1.8/queryBatchProjectStatus", json=body)
        data = resp.get("data")
        return data if isinstance(data, dict) else {}

    async def get_app(
        self,
        application_id: int | None = None,
        cluster_id: int | None = None,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        body = _merge({"applicationId": application_id, "clusterId": cluster_id}, params)
        resp = await self._post("/query/v1.8/queryApplicationMonitor", json=body)
        data = resp.get("data")
        return data if isinstance(data, dict) else {}

    async def batch_app(self, params: dict[str, Any] | None = None) -> dict[str, Any]:
        body = dict(params) if params else {}
        resp = await self._post("/query/v1.8/queryBatchApplicationMonitor", json=body)
        data = resp.get("data")
        return data if isinstance(data, dict) else {}

    async def get_pod(
        self,
        application_id: int | None = None,
        cluster_id: int | None = None,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        body = _merge({"applicationId": application_id, "clusterId": cluster_id}, params)
        resp = await self._post("/query/v1.8/queryPodMonitor", json=body)
        data = resp.get("data")
        return data if isinstance(data, dict) else {}

    async def batch_container(self, params: dict[str, Any] | None = None) -> dict[str, Any]:
        body = dict(params) if params else {}
        resp = await self._post("/query/v1.8/queryBatchContainerMonitor", json=body)
        data = resp.get("data")
        return data if isinstance(data, dict) else {}

    async def batch_pod(self, params: dict[str, Any] | None = None) -> dict[str, Any]:
        body = dict(params) if params else {}
        resp = await self._post("/query/v1.8/queryBatchPodMonitor", json=body)
        data = resp.get("data")
        return data if isinstance(data, dict) else {}


def _merge(explicit: dict[str, Any], extra: dict[str, Any] | None) -> dict[str, Any]:
    body: dict[str, Any] = {k: v for k, v in explicit.items() if v is not None}
    if extra:
        for k, v in extra.items():
            if v is not None:
                body[k] = v
    return body
