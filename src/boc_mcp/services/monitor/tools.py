from __future__ import annotations

from typing import Any

from mcp.server.fastmcp import FastMCP

from boc_mcp.client.boc_client import BocApiClient
from boc_mcp.middleware import wrap_tool_errors
from boc_mcp.services.monitor.service import MonitorService


def register_tools(mcp: FastMCP, client: BocApiClient, **_: Any) -> None:
    svc = MonitorService(client)

    @mcp.tool(
        description=(
            "查询单个应用（项目/服务）的实时监控状态，"
            "支持按 applicationId、clusterId、projectId 过滤，"
            "可通过 params 传入时间范围等扩展参数。"
        )
    )
    @wrap_tool_errors
    async def boc_monitor_get_project_status(
        application_id: int | None = None,
        cluster_id: int | None = None,
        project_id: int | None = None,
        params: dict | None = None,
    ) -> dict:
        return await svc.get_project_status(
            application_id=application_id,
            cluster_id=cluster_id,
            project_id=project_id,
            params=params,
        )

    @mcp.tool(description="批量查询项目监控数据，params 传入集群、时间范围、指标等过滤条件。")
    @wrap_tool_errors
    async def boc_monitor_batch_project(params: dict | None = None) -> dict:
        return await svc.batch_project(params=params)

    @mcp.tool(description="批量查询项目状态监控数据，params 传入集群、时间范围、指标等过滤条件。")
    @wrap_tool_errors
    async def boc_monitor_batch_project_status(params: dict | None = None) -> dict:
        return await svc.batch_project_status(params=params)

    @mcp.tool(
        description=(
            "查询单个应用（服务）的监控数据，"
            "支持按 applicationId、clusterId 过滤，"
            "可通过 params 传入时间范围等扩展参数。"
        )
    )
    @wrap_tool_errors
    async def boc_monitor_get_app(
        application_id: int | None = None,
        cluster_id: int | None = None,
        params: dict | None = None,
    ) -> dict:
        return await svc.get_app(
            application_id=application_id, cluster_id=cluster_id, params=params
        )

    @mcp.tool(description="批量查询应用监控数据，params 传入集群、时间范围、指标等过滤条件。")
    @wrap_tool_errors
    async def boc_monitor_batch_app(params: dict | None = None) -> dict:
        return await svc.batch_app(params=params)

    @mcp.tool(
        description=(
            "查询 Pod 监控数据，支持按 applicationId、clusterId 过滤，"
            "可通过 params 传入时间范围等扩展参数。"
        )
    )
    @wrap_tool_errors
    async def boc_monitor_get_pod(
        application_id: int | None = None,
        cluster_id: int | None = None,
        params: dict | None = None,
    ) -> dict:
        return await svc.get_pod(
            application_id=application_id, cluster_id=cluster_id, params=params
        )

    @mcp.tool(description="批量查询容器监控数据，params 传入集群、时间范围、指标等过滤条件。")
    @wrap_tool_errors
    async def boc_monitor_batch_container(params: dict | None = None) -> dict:
        return await svc.batch_container(params=params)

    @mcp.tool(description="批量查询 Pod 监控数据，params 传入集群、时间范围、指标等过滤条件。")
    @wrap_tool_errors
    async def boc_monitor_batch_pod(params: dict | None = None) -> dict:
        return await svc.batch_pod(params=params)
