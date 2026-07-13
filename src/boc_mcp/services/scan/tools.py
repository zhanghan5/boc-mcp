from __future__ import annotations

from typing import Any

from mcp.server.fastmcp import FastMCP

from boc_mcp.client.boc_client import BocApiClient
from boc_mcp.middleware import wrap_tool_errors
from boc_mcp.services.scan.service import ScanService


def register_tools(mcp: FastMCP, client: BocApiClient, **_: Any) -> None:
    svc = ScanService(client)

    @mcp.tool(description="分页查询安全扫描策略列表。")
    @wrap_tool_errors
    async def boc_scan_list_strategies(page: int = 1, page_size: int = 20) -> dict:
        r = await svc.list_strategies(page=page, page_size=page_size)
        return r.model_dump(by_alias=True)

    @mcp.tool(description="查询指定安全扫描报告的详情。")
    @wrap_tool_errors
    async def boc_scan_get_report(report_id: int) -> dict:
        return await svc.get_report(report_id)

    @mcp.tool(description="分页查询安全扫描报告列表。")
    @wrap_tool_errors
    async def boc_scan_list_reports(page: int = 1, page_size: int = 20) -> dict:
        r = await svc.list_reports(page=page, page_size=page_size)
        return r.model_dump(by_alias=True)
