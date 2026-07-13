from __future__ import annotations

from typing import Any

from mcp.server.fastmcp import FastMCP

from boc_mcp.client.boc_client import BocApiClient
from boc_mcp.middleware import wrap_tool_errors
from boc_mcp.services.partition.service import PartitionService


def register_tools(mcp: FastMCP, client: BocApiClient, **_: Any) -> None:
    svc = PartitionService(client)

    @mcp.tool(description="分页查询平台分区列表。")
    @wrap_tool_errors
    async def boc_partition_list(page: int = 1, page_size: int = 20) -> dict:
        r = await svc.list_partitions(page=page, page_size=page_size)
        return r.model_dump(by_alias=True)

    @mcp.tool(description="查询指定集群的默认分区。")
    @wrap_tool_errors
    async def boc_partition_get_default(cluster_id: int) -> dict:
        return await svc.get_default_partition(cluster_id)

    @mcp.tool(description="按任意过滤条件查询分区元数据，filters 为可选过滤字典。")
    @wrap_tool_errors
    async def boc_partition_get_meta(filters: dict | None = None) -> dict:
        return await svc.get_partition_meta(filters=filters)

    @mcp.tool(description="查询默认分区列表（不分页）。")
    @wrap_tool_errors
    async def boc_partition_list_default() -> list:
        return [p.model_dump(by_alias=True) for p in await svc.list_default_partitions()]

    @mcp.tool(description="查询分区节点列表，可传入 filters 字典进行过滤。")
    @wrap_tool_errors
    async def boc_partition_list_nodes(filters: dict | None = None) -> list:
        return [n.model_dump(by_alias=True) for n in await svc.list_nodes(filters=filters)]

    @mcp.tool(description="查询所有主机节点列表，可按 clusterId 过滤。")
    @wrap_tool_errors
    async def boc_partition_list_all_hosts(cluster_id: int | None = None) -> list:
        return [
            h.model_dump(by_alias=True) for h in await svc.list_all_hosts(cluster_id=cluster_id)
        ]

    @mcp.tool(description="分页查询主机全量信息，可按集群、租户、主机 IP、节点名称过滤。")
    @wrap_tool_errors
    async def boc_partition_all_info(
        cluster_id: int | None = None,
        env_id: int | None = None,
        host_ip: str | None = None,
        node_name: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> dict:
        r = await svc.all_info(
            cluster_id=cluster_id,
            env_id=env_id,
            host_ip=host_ip,
            node_name=node_name,
            page=page,
            page_size=page_size,
        )
        return r.model_dump(by_alias=True)

    @mcp.tool(description="按条件查询分区详情，filters 为可选过滤字典。")
    @wrap_tool_errors
    async def boc_partition_detail(filters: dict | None = None) -> dict:
        return await svc.detail_by_condition(filters=filters)

    @mcp.tool(description="分页查询当前租户可用的集群分区。")
    @wrap_tool_errors
    async def boc_partition_list_available() -> dict:
        r = await svc.list_available()
        return r.model_dump(by_alias=True)
