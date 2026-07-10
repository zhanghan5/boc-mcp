from __future__ import annotations
from boc_mcp.models.common import ListResult
from boc_mcp.services.base import BaseService
from boc_mcp.services.cluster.models import (
    ClusterSummary, ClusterNode, ClusterPartition, PartitionResource,
)


class ClusterService(BaseService):
    async def list_clusters(self, keyword: str | None = None, page: int = 1,
                            page_size: int = 20) -> ListResult[ClusterSummary]:
        body = {"currPageNum": page, "pageSize": min(page_size, 100)}
        if keyword:
            body["clusterName"] = keyword
        resp = await self._post("/cluster/v2.3/list", json=body)
        return _parse_list(resp, ClusterSummary)

    async def list_all_clusters(self) -> list[ClusterSummary]:
        resp = await self._get("/cluster/v2.3/listAll")
        data = resp.get("data") or []
        if not isinstance(data, list):
            data = [data] if data else []
        return [ClusterSummary(**d) for d in data]

    async def list_base_info(self, cluster_kind: str | None = None,
                             cluster_name: str | None = None, source_type: str | None = None,
                             version: str | None = None, page: int = 1,
                             page_size: int = 20) -> ListResult[ClusterSummary]:
        body: dict = {"currPageNum": page, "pageSize": min(page_size, 100)}
        if cluster_kind: body["clusterKind"] = cluster_kind
        if cluster_name: body["clusterName"] = cluster_name
        if source_type: body["sourceType"] = source_type
        if version: body["version"] = version
        resp = await self._post("/cluster/v3.0/listBaseInfo", json=body)
        return _parse_list(resp, ClusterSummary)

    async def get_monitor_info(self, cluster_id: int) -> dict:
        resp = await self._get(f"/cluster/v3.0/listMonitorInfo/{cluster_id}")
        return resp.get("data") or resp

    async def get_state(self, cluster_id: int) -> dict:
        resp = await self._get(f"/platformCluster/v2.3/getClusterState/{cluster_id}")
        return resp.get("data") or resp

    async def list_nodes(self, cluster_id: int, node_type: str | None = None,
                         page: int = 1, page_size: int = 20) -> ListResult[ClusterNode]:
        body = {"clusterId": cluster_id, "currPageNum": page, "pageSize": min(page_size, 100)}
        if node_type: body["nodeType"] = node_type
        resp = await self._post("/platformCluster/v2.3/getClusterNodes", json=body)
        return _parse_list(resp, ClusterNode)

    async def list_platform_partitions(self, cluster_id: int, page: int = 1,
                                       page_size: int = 20) -> ListResult[ClusterPartition]:
        body = {"clusterId": cluster_id, "currPageNum": page, "pageSize": min(page_size, 100)}
        resp = await self._post("/platformCluster/v2.3/getPartition", json=body)
        return _parse_list(resp, ClusterPartition)

    async def get_partition_resource(self, host_ids: str) -> PartitionResource:
        resp = await self._get(f"/cluster/v2.3/clusterPartitionResource/{host_ids}")
        data = resp.get("data") or {}
        return PartitionResource.model_validate(data) if data else PartitionResource(host_ids=host_ids)

    async def list_clusters_by_env(self, env_id: int) -> list[ClusterSummary]:
        resp = await self._get(f"/platformCluster/v2.3/getClusterByEnvId/{env_id}")
        data = resp.get("data") or []
        if not isinstance(data, list):
            data = [data] if data else []
        return [ClusterSummary.model_validate(d) for d in data]

    async def list_available_partitions(self) -> ListResult[ClusterPartition]:
        resp = await self._post("/partition/v2.3/clusterPartition", json={})
        return _parse_list(resp, ClusterPartition)


def _parse_list(resp: dict, model_cls):
    # resp can be legacy pagination with rows, or direct {"data": [...]}
    if isinstance(resp.get("data"), list) and "rows" not in resp:
        items = [model_cls.model_validate(d) for d in resp["data"]]
        return ListResult[model_cls](items=items, total=len(items), page_count=1)
    lr = ListResult.from_legacy(resp, items_key="rows")
    lr.items = [model_cls.model_validate(d) for d in lr.items]
    return lr
