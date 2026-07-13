from __future__ import annotations

from typing import Any

from mcp.server.fastmcp import FastMCP

from boc_mcp.client.boc_client import BocApiClient
from boc_mcp.middleware import wrap_tool_errors
from boc_mcp.services.workload.service import WorkloadService


def register_tools(mcp: FastMCP, client: BocApiClient, **_: Any) -> None:
    svc = WorkloadService(client)

    @mcp.tool(description="分页查询应用（Project）列表，支持按集群、租户、关键字过滤。")
    @wrap_tool_errors
    async def boc_workload_list_projects(
        cluster_id: int | None = None,
        env_id: int | None = None,
        keyword: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> dict:
        r = await svc.list_projects(
            cluster_id=cluster_id, env_id=env_id, keyword=keyword, page=page, page_size=page_size
        )
        return r.model_dump(by_alias=True, mode="json")

    @mcp.tool(description="分页查询应用与服务列表，支持按集群、租户、关键字过滤。")
    @wrap_tool_errors
    async def boc_workload_list_projects_and_apps(
        cluster_id: int | None = None,
        env_id: int | None = None,
        keyword: str | None = None,
        is_task: bool | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> dict:
        r = await svc.list_projects_and_apps(
            cluster_id=cluster_id,
            env_id=env_id,
            keyword=keyword,
            is_task=is_task,
            page=page,
            page_size=page_size,
        )
        return r.model_dump(by_alias=True, mode="json")

    @mcp.tool(
        description="分页查询服务/任务（Application）列表，支持按集群、租户、关键字、类型过滤。"
    )
    @wrap_tool_errors
    async def boc_workload_list_applications(
        cluster_id: int | None = None,
        env_id: int | None = None,
        keyword: str | None = None,
        is_task: bool | None = None,
        kind: str | None = None,
        master_ip: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> dict:
        r = await svc.list_applications(
            cluster_id=cluster_id,
            env_id=env_id,
            keyword=keyword,
            is_task=is_task,
            kind=kind,
            master_ip=master_ip,
            page=page,
            page_size=page_size,
        )
        return r.model_dump(by_alias=True, mode="json")

    @mcp.tool(description="查询指定服务下的网络信息。")
    @wrap_tool_errors
    async def boc_workload_get_app_networks(
        application_id: int | None = None,
        application_name: str | None = None,
        cluster_id: int | None = None,
        project_id: int | None = None,
    ) -> list:
        return await svc.get_app_networks(
            application_id=application_id,
            application_name=application_name,
            cluster_id=cluster_id,
            project_id=project_id,
        )

    @mcp.tool(description="分页查询容器列表，支持按集群、租户、服务、Pod、主机、镜像过滤。")
    @wrap_tool_errors
    async def boc_workload_list_containers(
        cluster_id: int | None = None,
        env_id: int | None = None,
        application_id: int | None = None,
        container_name: str | None = None,
        pod_id: int | None = None,
        host_ip: str | None = None,
        host_name: str | None = None,
        image_name_tag: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> dict:
        r = await svc.list_containers(
            cluster_id=cluster_id,
            env_id=env_id,
            application_id=application_id,
            container_name=container_name,
            pod_id=pod_id,
            host_ip=host_ip,
            host_name=host_name,
            image_name_tag=image_name_tag,
            page=page,
            page_size=page_size,
        )
        return r.model_dump(by_alias=True, mode="json")

    @mcp.tool(
        description="分页查询实例（Pod）列表，支持按集群、租户、服务、命名空间、容器、主机过滤。"
    )
    @wrap_tool_errors
    async def boc_workload_list_pods(
        cluster_id: int | None = None,
        env_id: int | None = None,
        application_id: int | None = None,
        namespace: str | None = None,
        container_name: str | None = None,
        host_name: str | None = None,
        is_task: bool | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> dict:
        r = await svc.list_pods(
            cluster_id=cluster_id,
            env_id=env_id,
            application_id=application_id,
            namespace=namespace,
            container_name=container_name,
            host_name=host_name,
            is_task=is_task,
            page=page,
            page_size=page_size,
        )
        return r.model_dump(by_alias=True, mode="json")

    @mcp.tool(description="查询 kubectl 可访问的 Pod 列表（需要 master_ip 和资源类型）。")
    @wrap_tool_errors
    async def boc_workload_list_kubectl_pods(
        master_ip: str, resource_type: str, page: int = 1, page_size: int = 20
    ) -> dict:
        r = await svc.list_kubectl_pods(
            master_ip=master_ip, resource_type=resource_type, page=page, page_size=page_size
        )
        return r.model_dump(by_alias=True, mode="json")

    @mcp.tool(description="检查指定命名空间下内部服务是否存在。")
    @wrap_tool_errors
    async def boc_workload_check_service(
        application_id: int, cluster_id: int, namespace: str, name: str | None = None
    ) -> dict:
        return await svc.check_service(
            application_id=application_id, cluster_id=cluster_id, namespace=namespace, name=name
        )

    @mcp.tool(description="根据服务 id 获取内部负载详情。")
    @wrap_tool_errors
    async def boc_workload_get_service_by_app(
        application_name: str,
        project_id: int,
        project_name: str,
        platform_type: str = "kubernetes",
        master_map: dict | None = None,
    ) -> list:
        return await svc.get_service_by_app(
            application_name=application_name,
            project_id=project_id,
            project_name=project_name,
            platform_type=platform_type,
            master_map=master_map,
        )

    @mcp.tool(description="获取指定服务下的内部负载列表。")
    @wrap_tool_errors
    async def boc_workload_list_services_by_app(
        application_name: str,
        project_id: int,
        project_name: str,
        master_ip: str,
        platform_type: str = "kubernetes",
        service_name: str | None = None,
        master_map: dict | None = None,
    ) -> list:
        return await svc.list_services_by_app(
            application_name=application_name,
            project_id=project_id,
            project_name=project_name,
            master_ip=master_ip,
            platform_type=platform_type,
            service_name=service_name,
            master_map=master_map,
        )

    @mcp.tool(description="分页查询内部负载（Service）列表，支持按集群、租户、命名空间、名称过滤。")
    @wrap_tool_errors
    async def boc_workload_list_services(
        cluster_id: int | None = None,
        env_id: int | None = None,
        namespace: str | None = None,
        name: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> dict:
        r = await svc.list_services(
            cluster_id=cluster_id,
            env_id=env_id,
            namespace=namespace,
            name=name,
            page=page,
            page_size=page_size,
        )
        return r.model_dump(by_alias=True, mode="json")

    @mcp.tool(description="查询内部负载详情（通用 Service 查询接口）。")
    @wrap_tool_errors
    async def boc_workload_query_service(
        application_name: str,
        master_ip: str,
        project_name: str,
        platform_type: str = "kubernetes",
        service_name: str | None = None,
        master_map: dict | None = None,
        project_id: int | None = None,
    ) -> dict:
        return await svc.query_service(
            application_name=application_name,
            master_ip=master_ip,
            project_name=project_name,
            platform_type=platform_type,
            service_name=service_name,
            master_map=master_map,
            project_id=project_id,
        )
