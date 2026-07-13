from __future__ import annotations

from typing import Any

from mcp.server.fastmcp import FastMCP

from boc_mcp.client.boc_client import BocApiClient
from boc_mcp.middleware import wrap_tool_errors
from boc_mcp.services.service_tree.service import ServiceTreeService


def register_tools(mcp: FastMCP, client: BocApiClient, **_: Any) -> None:
    svc = ServiceTreeService(client)

    @mcp.tool(
        description=(
            "查询服务树节点（有数据权限控制），可按父类型、父 id、节点类型筛选。返回树节点列表。"
        )
    )
    @wrap_tool_errors
    async def boc_service_tree(
        p_type: str | None = None,
        pid: int | None = None,
        type_: str | None = None,
    ) -> list[dict]:
        result = await svc.get_tree(p_type=p_type, pid=pid, type_=type_)
        return [item.model_dump(by_alias=True) for item in result]
