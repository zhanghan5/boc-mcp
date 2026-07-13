from __future__ import annotations

from typing import Any

from boc_mcp.models.common import ListResult
from boc_mcp.services.base import BaseService
from boc_mcp.services.workload.models import (
    ContainerSummary,
    PodSummary,
    ServiceSummary,
    WorkloadSummary,
)


def _filter_none(**kw: Any) -> dict[str, Any]:
    return {k: v for k, v in kw.items() if v is not None}


def _parse_list(resp: dict, model_cls, items_key="rows") -> ListResult[Any]:
    if isinstance(resp.get("data"), list) and items_key not in resp:
        items = [model_cls.model_validate(d) for d in resp["data"]]
        return ListResult[model_cls](items=items, total=len(items), page_count=1)
    lr = ListResult.from_legacy(resp, items_key=items_key)
    lr.items = [model_cls.model_validate(d) for d in lr.items]
    return lr


class WorkloadService(BaseService):
    async def list_projects(
        self,
        cluster_id: int | None = None,
        env_id: int | None = None,
        keyword: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> ListResult[WorkloadSummary]:
        body = _filter_none(
            clusterId=cluster_id,
            envId=env_id,
            projectName=keyword,
            currPageNum=page,
            pageSize=min(page_size, 100),
        )
        resp = await self._post("/query/v1.8/queryProject", json=body)
        return _parse_list(resp, WorkloadSummary)

    async def list_projects_and_apps(
        self,
        cluster_id: int | None = None,
        env_id: int | None = None,
        keyword: str | None = None,
        page: int = 1,
        page_size: int = 20,
        is_task: bool | None = None,
    ) -> ListResult[WorkloadSummary]:
        body = _filter_none(
            clusterId=cluster_id,
            envId=env_id,
            applicationName=keyword,
            currPageNum=page,
            pageSize=min(page_size, 100),
            isTask=is_task,
        )
        resp = await self._post("/query/v1.8/queryProjectAndApplication", json=body)
        return _parse_list(resp, WorkloadSummary)

    async def list_applications(
        self,
        cluster_id: int | None = None,
        env_id: int | None = None,
        keyword: str | None = None,
        page: int = 1,
        page_size: int = 20,
        is_task: bool | None = None,
        kind: str | None = None,
        master_ip: str | None = None,
    ) -> ListResult[WorkloadSummary]:
        body = _filter_none(
            clusterId=cluster_id,
            envId=env_id,
            applicationName=keyword,
            currPageNum=page,
            pageSize=min(page_size, 100),
            isTask=is_task,
            kind=kind,
            masterIp=master_ip,
        )
        resp = await self._post("/query/v1.8/queryApplication", json=body)
        return _parse_list(resp, WorkloadSummary)

    async def get_app_networks(
        self,
        application_id: int | None = None,
        application_name: str | None = None,
        cluster_id: int | None = None,
        project_id: int | None = None,
    ) -> list[dict]:
        body = _filter_none(
            applicationId=application_id,
            applicationName=application_name,
            clusterId=cluster_id,
            projectId=project_id,
        )
        resp = await self._post("/query/v2.3/getNetworkByApplicationId", json=body)
        data = resp.get("data") or resp.get("rows") or []
        return data if isinstance(data, list) else [data] if data else []

    async def list_containers(
        self,
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
    ) -> ListResult[ContainerSummary]:
        body = _filter_none(
            clusterId=cluster_id,
            envId=env_id,
            applicationId=application_id,
            applicationContainerName=container_name,
            podId=pod_id,
            hostIp=host_ip,
            hostName=host_name,
            imageNameTag=image_name_tag,
            currPageNum=page,
            pageSize=min(page_size, 100),
            resourceType="queryContainer",
        )
        resp = await self._post("/query/v1.8/queryContainer", json=body)
        return _parse_list(resp, ContainerSummary)

    async def list_pods(
        self,
        cluster_id: int | None = None,
        env_id: int | None = None,
        application_id: int | None = None,
        namespace: str | None = None,
        container_name: str | None = None,
        host_name: str | None = None,
        is_task: bool | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> ListResult[PodSummary]:
        body = _filter_none(
            clusterId=cluster_id,
            envId=env_id,
            applicationId=application_id,
            applicationNamespace=namespace,
            containerName=container_name,
            hostName=host_name,
            isTask=is_task,
            currPageNum=page,
            pageSize=min(page_size, 100),
            resourceType="queryPod",
        )
        resp = await self._post("/query/v1.8/queryPod", json=body)
        return _parse_list(resp, PodSummary)

    async def list_kubectl_pods(
        self, master_ip: str, resource_type: str, page: int = 1, page_size: int = 20
    ) -> ListResult[PodSummary]:
        body = {
            "masterIp": master_ip,
            "resourceType": resource_type,
            "currPageNum": page,
            "pageSize": min(page_size, 100),
        }
        resp = await self._post("/query/v3.0/queryKubectlPods", json=body)
        return _parse_list(resp, PodSummary)

    async def check_service(
        self, application_id: int, cluster_id: int, namespace: str, name: str | None = None
    ) -> dict:
        body = _filter_none(
            applicationId=application_id, clusterId=cluster_id, namespace=namespace, name=name
        )
        return await self._post("/service/v2.3/checkService", json=body)

    async def get_service_by_app(
        self,
        application_name: str,
        project_id: int,
        project_name: str,
        platform_type: str = "kubernetes",
        master_map: dict | None = None,
    ) -> list[dict]:
        body = _filter_none(
            applicationName=application_name,
            projectId=project_id,
            projectName=project_name,
            platformType=platform_type,
            masterMap=master_map,
        )
        resp = await self._post("/service/v2.3/getServiceByApplicationId", json=body)
        data = resp.get("data") or resp.get("rows") or []
        return data if isinstance(data, list) else [data] if data else []

    async def list_services_by_app(
        self,
        application_name: str,
        project_id: int,
        project_name: str,
        master_ip: str,
        platform_type: str = "kubernetes",
        resource_type: str = "queryServiceByApplicationId",
        service_name: str | None = None,
        master_map: dict | None = None,
    ) -> list[dict]:
        body = _filter_none(
            applicationName=application_name,
            projectId=project_id,
            projectName=project_name,
            masterIp=master_ip,
            platformType=platform_type,
            resourceType=resource_type,
            serviceName=service_name,
            masterMap=master_map,
        )
        resp = await self._post("/query/v2.3/queryServiceByApplicationId", json=body)
        data = resp.get("data") or resp.get("rows") or []
        return data if isinstance(data, list) else [data] if data else []

    async def list_services(
        self,
        cluster_id: int | None = None,
        env_id: int | None = None,
        namespace: str | None = None,
        name: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> ListResult[ServiceSummary]:
        body = _filter_none(
            clusterId=cluster_id,
            envId=env_id,
            namespace=namespace,
            name=name,
            currPageNum=page,
            pageSize=min(page_size, 100),
        )
        resp = await self._post("/service/v2.3/listServiceByPage", json=body)
        return _parse_list(resp, ServiceSummary)

    async def query_service(
        self,
        application_name: str,
        master_ip: str,
        project_name: str,
        platform_type: str = "kubernetes",
        resource_type: str = "queryServiceByApplicationId",
        service_name: str | None = None,
        master_map: dict | None = None,
        project_id: int | None = None,
    ) -> dict:
        body = _filter_none(
            applicationName=application_name,
            masterIp=master_ip,
            projectName=project_name,
            platformType=platform_type,
            resourceType=resource_type,
            serviceName=service_name,
            masterMap=master_map,
            projectId=project_id,
        )
        return await self._post("/query/v1.8/queryService", json=body)
