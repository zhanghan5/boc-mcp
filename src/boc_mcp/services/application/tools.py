from __future__ import annotations

from typing import Any

from mcp.server.fastmcp import FastMCP

from boc_mcp.client.boc_client import BocApiClient
from boc_mcp.middleware import wrap_tool_errors
from boc_mcp.services.application.service import ApplicationService


def register_tools(mcp: FastMCP, client: BocApiClient, **_: Any) -> None:
    svc = ApplicationService(client)

    @mcp.tool(description="根据应用 ID 查询单个应用的详细信息。")
    @wrap_tool_errors
    async def boc_app_get(app_id: int) -> dict:
        return await svc.get(app_id)

    @mcp.tool(description="分页查询应用列表，可按集群 ID 和应用名称过滤。")
    @wrap_tool_errors
    async def boc_app_list(
        cluster_id: str | None = None,
        project_name: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> dict:
        r = await svc.list(
            cluster_id=cluster_id,
            project_name=project_name,
            page=page,
            page_size=page_size,
        )
        return r.model_dump(by_alias=True)
