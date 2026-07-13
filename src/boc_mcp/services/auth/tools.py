from __future__ import annotations

from typing import Any

from mcp.server.fastmcp import FastMCP

from boc_mcp.auth.token_manager import TokenManager
from boc_mcp.client.boc_client import BocApiClient
from boc_mcp.middleware import wrap_tool_errors
from boc_mcp.services.auth.service import AuthService


def register_tools(
    mcp: FastMCP, client: BocApiClient, token_manager: TokenManager | None = None
) -> None:
    svc = AuthService(token_manager) if token_manager else None

    @mcp.tool(description="查询博云平台登录状态：是否已登录、登录用户、systemId、token 过期时间。")
    @wrap_tool_errors
    async def boc_auth_status() -> dict[str, Any]:
        if svc is None:
            return {"logged_in": False}
        st = await svc.status()
        return st.model_dump()

    @mcp.tool(description="强制重新登录博云平台（当 token 异常或需要切换账号时使用）。")
    @wrap_tool_errors
    async def boc_auth_refresh() -> str:
        if svc is None:
            return "no token manager configured"
        await svc.refresh()
        return "relogin successful"
