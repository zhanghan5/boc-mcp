from __future__ import annotations

from typing import Any

from mcp.server.fastmcp import FastMCP

from boc_mcp.client.boc_client import BocApiClient
from boc_mcp.middleware import wrap_tool_errors
from boc_mcp.services.network.service import NetworkService


def register_tools(mcp: FastMCP, client: BocApiClient, **_: Any) -> None:
    svc = NetworkService(client)

    @mcp.tool(description="按名称或 IP 查询网络分区列表。")
    @wrap_tool_errors
    async def boc_network_list_by_name(id: int | None = None, ips: str | None = None) -> list:
        items = await svc.list_by_name(id=id, ips=ips)
        return [item.model_dump() for item in items]

    @mcp.tool(description="查询可用（未分配）的网络列表，可按集群 id 过滤。")
    @wrap_tool_errors
    async def boc_network_list_available(cluster_id: int | None = None) -> list:
        items = await svc.list_available(cluster_id=cluster_id)
        return [item.model_dump() for item in items]

    @mcp.tool(description="按租户 id 查询网络列表。")
    @wrap_tool_errors
    async def boc_network_list_by_env(env_id: int | None = None) -> list:
        items = await svc.list_by_env(env_id=env_id)
        return [item.model_dump() for item in items]
