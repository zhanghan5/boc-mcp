from __future__ import annotations

from typing import Any

from mcp.server.fastmcp import FastMCP

from boc_mcp.client.boc_client import BocApiClient
from boc_mcp.middleware import wrap_tool_errors
from boc_mcp.services.version.service import VersionService


def register_tools(mcp: FastMCP, client: BocApiClient, **_: Any) -> None:
    svc = VersionService(client)

    @mcp.tool(description="查询版本列表，支持按应用/项目/集群/租户过滤。")
    @wrap_tool_errors
    async def boc_version_list(
        app_id: int | None = None,
        project_id: int | None = None,
        cluster_id: int | None = None,
        env_id: int | None = None,
        is_task: bool | None = None,
        version_id: int | None = None,
        page_size: int = 20,
    ) -> dict:
        r = await svc.list_versions(
            app_id=app_id,
            project_id=project_id,
            cluster_id=cluster_id,
            env_id=env_id,
            is_task=is_task,
            version_id=version_id,
            page_size=page_size,
        )
        return r.model_dump(by_alias=True, mode="json")

    @mcp.tool(description="根据版本名称查询版本 id。")
    @wrap_tool_errors
    async def boc_version_get_id_by_name(
        version_name: str,
        app_id: int | None = None,
        application_id: int | None = None,
        project_id: int | None = None,
        cluster_id: int | None = None,
        current_version_id: int | None = None,
        env_id: int | None = None,
        is_task: bool | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> dict:
        return await svc.get_id_by_name(
            version_name=version_name,
            app_id=app_id,
            application_id=application_id,
            project_id=project_id,
            cluster_id=cluster_id,
            current_version_id=current_version_id,
            env_id=env_id,
            is_task=is_task,
            page=page,
            page_size=page_size,
        )

    @mcp.tool(description="查询版本的镜像组列表。")
    @wrap_tool_errors
    async def boc_version_list_image_groups(
        app_id: int | None = None,
        application_id: int | None = None,
        project_id: int | None = None,
        cluster_id: int | None = None,
        current_version_id: int | None = None,
        env_id: int | None = None,
        is_task: bool | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> dict:
        r = await svc.list_image_groups(
            app_id=app_id,
            application_id=application_id,
            project_id=project_id,
            cluster_id=cluster_id,
            current_version_id=current_version_id,
            env_id=env_id,
            is_task=is_task,
            page=page,
            page_size=page_size,
        )
        return r.model_dump(by_alias=True, mode="json")

    @mcp.tool(description="查询指定版本下已发布的集群列表。")
    @wrap_tool_errors
    async def boc_version_list_dispatched_clusters(
        application_id: int, cluster_id: int | None = None, version_name: str | None = None
    ) -> list:
        return await svc.list_dispatched_clusters(
            application_id=application_id, cluster_id=cluster_id, version_name=version_name
        )

    @mcp.tool(description="查询指定版本下未发布的集群列表，分页返回。")
    @wrap_tool_errors
    async def boc_version_list_undispatched_clusters(
        version_name: str,
        app_id: int | None = None,
        application_id: int | None = None,
        project_id: int | None = None,
        cluster_id: int | None = None,
        current_version_id: int | None = None,
        env_id: int | None = None,
        is_task: bool | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> dict:
        r = await svc.list_undispatched_clusters(
            version_name=version_name,
            app_id=app_id,
            application_id=application_id,
            project_id=project_id,
            cluster_id=cluster_id,
            current_version_id=current_version_id,
            env_id=env_id,
            is_task=is_task,
            page=page,
            page_size=page_size,
        )
        return r.model_dump(by_alias=True, mode="json")

    @mcp.tool(description="查询镜像组信息。")
    @wrap_tool_errors
    async def boc_version_get_image_group(
        application_name: str | None = None,
        project_id: int | None = None,
        app_id: int | None = None,
        resource_type: str = "queryImageGroup",
    ) -> list:
        return await svc.get_image_group(
            application_name=application_name,
            project_id=project_id,
            app_id=app_id,
            resource_type=resource_type,
        )

    @mcp.tool(description="查询指定 Kubernetes 资源（kind/name）的 YAML 定义。")
    @wrap_tool_errors
    async def boc_version_get_yaml(kind: str, name: str) -> dict:
        return await svc.get_yaml(kind=kind, name=name)
