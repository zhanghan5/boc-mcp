from __future__ import annotations

from boc_mcp.services.base import BaseService
from boc_mcp.services.network.models import NetworkPartition


def _extract_list(resp: dict | list) -> list[dict]:
    if isinstance(resp, list):
        return resp
    data = resp.get("data") if isinstance(resp, dict) else None
    if isinstance(data, list):
        return data
    if data is not None:
        return [data]
    if isinstance(resp, dict):
        return [resp]
    return []


class NetworkService(BaseService):
    async def list_by_name(
        self, id: int | None = None, ips: str | None = None
    ) -> list[NetworkPartition]:
        params: dict = {}
        if id is not None:
            params["id"] = id
        if ips is not None:
            params["ips"] = ips
        resp = await self._get("/partitionNetwork/getListByNetWorkName", params=params or None)
        return [NetworkPartition.model_validate(d) for d in _extract_list(resp)]

    async def list_available(self, cluster_id: int | None = None) -> list[NetworkPartition]:
        params: dict = {}
        if cluster_id is not None:
            params["clusterId"] = cluster_id
        resp = await self._get("/partitionNetwork/getUnUseredList", params=params or None)
        return [NetworkPartition.model_validate(d) for d in _extract_list(resp)]

    async def list_by_env(self, env_id: int | None = None) -> list[NetworkPartition]:
        body: dict = {}
        if env_id is not None:
            body["envId"] = env_id
        resp = await self._post("/partitionNetwork/v2.3/getNetworkListByEnvId", json=body)
        return [NetworkPartition.model_validate(d) for d in _extract_list(resp)]
