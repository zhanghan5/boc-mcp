from __future__ import annotations

from typing import Any

from boc_mcp.models.common import ListResult
from boc_mcp.services.base import BaseService
from boc_mcp.services.partition.models import HostNode, Partition, PartitionNode


class PartitionService(BaseService):
    async def list_partitions(self, page: int = 1, page_size: int = 20) -> ListResult[Partition]:
        body = {"currPageNum": page, "pageSize": min(page_size, 100)}
        resp = await self._post("/partition/v2.3/list", json=body)
        return _parse_list(resp, Partition)

    async def get_default_partition(self, cluster_id: int) -> dict:
        resp = await self._get(f"/partition/v3.3/getDefaultPartition/{cluster_id}")
        data = resp.get("data")
        if isinstance(data, dict):
            return Partition.model_validate(data).model_dump(by_alias=True)
        return data if isinstance(data, dict) else {}

    async def get_partition_meta(self, filters: dict | None = None) -> dict:
        body: dict[str, Any] = dict(filters or {})
        resp = await self._post("/partition/v2.3/getPartitionMeta", json=body)
        data = resp.get("data")
        return data if isinstance(data, dict) else {}

    async def list_default_partitions(self) -> list[Partition]:
        resp = await self._post("/partition/v2.3/listByKind", json={})
        data = resp.get("data") or []
        if not isinstance(data, list):
            data = [data] if data else []
        return [Partition.model_validate(d) for d in data]

    async def list_nodes(self, filters: dict | None = None) -> list[PartitionNode]:
        body: dict[str, Any] = dict(filters or {})
        resp = await self._post("/partition/v2.3/nodelist", json=body)
        data = resp.get("data") or []
        if not isinstance(data, list):
            data = [data] if data else []
        return [PartitionNode.model_validate(d) for d in data]

    async def list_all_hosts(self, cluster_id: int | None = None) -> list[HostNode]:
        body: dict[str, Any] = {}
        if cluster_id is not None:
            body["clusterId"] = cluster_id
        resp = await self._post("/partition/v3.3/getAllHost", json=body)
        data = resp.get("data") or []
        if not isinstance(data, list):
            data = [data] if data else []
        return [HostNode.model_validate(d) for d in data]

    async def all_info(
        self,
        cluster_id: int | None = None,
        env_id: int | None = None,
        host_ip: str | None = None,
        node_name: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> ListResult[HostNode]:
        body: dict[str, Any] = {"currPageNum": page, "pageSize": min(page_size, 100)}
        if cluster_id is not None:
            body["clusterId"] = cluster_id
        if env_id is not None:
            body["envId"] = env_id
        if host_ip is not None:
            body["hostIp"] = host_ip
        if node_name is not None:
            body["nodeName"] = node_name
        resp = await self._post("/partition/v2.3/allInfo", json=body)
        return _parse_list(resp, HostNode)

    async def detail_by_condition(self, filters: dict | None = None) -> dict:
        body: dict[str, Any] = dict(filters or {})
        resp = await self._post("/partition/v2.3/detailByCondition", json=body)
        data = resp.get("data")
        return data if isinstance(data, dict) else {}

    async def list_available(self) -> ListResult[Partition]:
        resp = await self._post("/partition/v2.3/clusterPartition", json={})
        return _parse_list(resp, Partition)


def _parse_list(resp: dict, model_cls):
    if isinstance(resp.get("data"), list) and "rows" not in resp:
        items = [model_cls.model_validate(d) for d in resp["data"]]
        return ListResult[model_cls](items=items, total=len(items), page_count=1)
    lr = ListResult.from_legacy(resp, items_key="rows")
    lr.items = [model_cls.model_validate(d) for d in lr.items]
    return lr
