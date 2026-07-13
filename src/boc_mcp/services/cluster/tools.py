from __future__ import annotations

from typing import Any

from mcp.server.fastmcp import FastMCP

from boc_mcp.client.boc_client import BocApiClient
from boc_mcp.middleware import wrap_tool_errors
from boc_mcp.services.cluster.service import ClusterService


def register_tools(mcp: FastMCP, client: BocApiClient, **_: Any) -> None:
    svc = ClusterService(client)

    @mcp.tool(description="查询博云平台集群列表，可按名称关键字过滤，支持分页。")
    @wrap_tool_errors
    async def boc_cluster_list(
        keyword: str | None = None, page: int = 1, page_size: int = 20
    ) -> dict:
        r = await svc.list_clusters(keyword=keyword, page=page, page_size=page_size)
        return r.model_dump(by_alias=True)

    @mcp.tool(description="查询所有集群（不分页，返回简单列表）。")
    @wrap_tool_errors
    async def boc_cluster_list_all() -> list:
        return [c.model_dump(by_alias=True) for c in await svc.list_all_clusters()]

    @mcp.tool(description="查询集群基本信息，可按类型、名称、版本过滤，支持分页。")
    @wrap_tool_errors
    async def boc_cluster_list_base_info(
        cluster_kind: str | None = None,
        cluster_name: str | None = None,
        source_type: str | None = None,
        version: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> dict:
        r = await svc.list_base_info(
            cluster_kind=cluster_kind,
            cluster_name=cluster_name,
            source_type=source_type,
            version=version,
            page=page,
            page_size=page_size,
        )
        return r.model_dump(by_alias=True)

    @mcp.tool(description="查询指定集群的监控信息。")
    @wrap_tool_errors
    async def boc_cluster_get_monitor(cluster_id: int) -> dict:
        return await svc.get_monitor_info(cluster_id)

    @mcp.tool(description="查询指定集群的运行状态。")
    @wrap_tool_errors
    async def boc_cluster_get_state(cluster_id: int) -> dict:
        return await svc.get_state(cluster_id)

    @mcp.tool(description="分页查询指定集群下的节点列表。")
    @wrap_tool_errors
    async def boc_cluster_list_nodes(
        cluster_id: int, node_type: str | None = None, page: int = 1, page_size: int = 20
    ) -> dict:
        r = await svc.list_nodes(
            cluster_id=cluster_id, node_type=node_type, page=page, page_size=page_size
        )
        return r.model_dump(by_alias=True)

    @mcp.tool(description="分页查询指定集群的分区列表。")
    @wrap_tool_errors
    async def boc_cluster_list_partitions(
        cluster_id: int, page: int = 1, page_size: int = 20
    ) -> dict:
        r = await svc.list_platform_partitions(
            cluster_id=cluster_id, page=page, page_size=page_size
        )
        return r.model_dump(by_alias=True)

    @mcp.tool(
        description=(
            "查询指定 hostId 列表的分区 CPU/内存资源使用情况，hostIds 为逗号分隔的 id 字符串。"
        )
    )
    @wrap_tool_errors
    async def boc_cluster_get_partition_resource(host_ids: str) -> dict:
        r = await svc.get_partition_resource(host_ids)
        return r.model_dump(by_alias=True)

    @mcp.tool(description="查询指定租户（envId）下的集群列表。")
    @wrap_tool_errors
    async def boc_cluster_list_by_env(env_id: int) -> list:
        return [c.model_dump(by_alias=True) for c in await svc.list_clusters_by_env(env_id)]

    @mcp.tool(description="查询当前租户下集群可用分区。")
    @wrap_tool_errors
    async def boc_cluster_list_available_partitions() -> dict:
        r = await svc.list_available_partitions()
        return r.model_dump(by_alias=True)
