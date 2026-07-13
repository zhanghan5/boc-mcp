from __future__ import annotations

from typing import Any

from boc_mcp.models.common import ListResult
from boc_mcp.services.base import BaseService
from boc_mcp.services.version.models import ImageGroup, VersionSummary


def _filter_none(**kw: Any) -> dict[str, Any]:
    return {k: v for k, v in kw.items() if v is not None}


def _parse_list(resp: dict, model_cls, items_key="rows") -> ListResult[Any]:
    if isinstance(resp.get("data"), list) and items_key not in resp:
        items = [model_cls.model_validate(d) for d in resp["data"]]
        return ListResult[model_cls](items=items, total=len(items), page_count=1)
    lr = ListResult.from_legacy(resp, items_key=items_key)
    lr.items = [model_cls.model_validate(d) for d in lr.items]
    return lr


class VersionService(BaseService):
    async def list_versions(
        self,
        app_id: int | None = None,
        project_id: int | None = None,
        cluster_id: int | None = None,
        env_id: int | None = None,
        is_task: bool | None = None,
        version_id: int | None = None,
        page_size: int = 20,
    ) -> ListResult[VersionSummary]:
        body = _filter_none(
            appId=app_id,
            projectId=project_id,
            clusterId=cluster_id,
            envId=env_id,
            isTask=is_task,
            versionId=version_id,
            currPageNum=1,
            pageSize=min(page_size, 100),
        )
        resp = await self._post("/query/v1.6/queryVersion", json=body)
        return _parse_list(resp, VersionSummary)

    async def get_id_by_name(
        self,
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
        body = _filter_none(
            appId=app_id,
            applicationId=application_id,
            projectId=project_id,
            clusterId=cluster_id,
            currentVersionId=current_version_id,
            envId=env_id,
            isTask=is_task,
            versionName=version_name,
            currPageNum=page,
            pageSize=min(page_size, 100),
        )
        return await self._post("/query/v2.3/queryVersionIdByVersionName", json=body)

    async def list_image_groups(
        self,
        app_id: int | None = None,
        application_id: int | None = None,
        project_id: int | None = None,
        cluster_id: int | None = None,
        current_version_id: int | None = None,
        env_id: int | None = None,
        is_task: bool | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> ListResult[ImageGroup]:
        body = _filter_none(
            appId=app_id,
            applicationId=application_id,
            projectId=project_id,
            clusterId=cluster_id,
            currentVersionId=current_version_id,
            envId=env_id,
            isTask=is_task,
            currPageNum=page,
            pageSize=min(page_size, 100),
        )
        resp = await self._post("/query/v1.8/queryVersionImageGroupByApplicationId", json=body)
        return _parse_list(resp, ImageGroup)

    async def list_dispatched_clusters(
        self, application_id: int, cluster_id: int | None = None, version_name: str | None = None
    ) -> list[dict]:
        body = _filter_none(
            applicationId=application_id, clusterId=cluster_id, versionName=version_name
        )
        resp = await self._post("/query/v2.3/queryDispatchVersionByVersionName", json=body)
        data = resp.get("data") or resp.get("rows") or []
        return data if isinstance(data, list) else [data] if data else []

    async def list_undispatched_clusters(
        self,
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
    ) -> ListResult[dict]:
        body = _filter_none(
            appId=app_id,
            applicationId=application_id,
            projectId=project_id,
            clusterId=cluster_id,
            currentVersionId=current_version_id,
            envId=env_id,
            isTask=is_task,
            versionName=version_name,
            currPageNum=page,
            pageSize=min(page_size, 100),
        )
        resp = await self._post("/query/v2.3/queryUnDispatchVersionByVersionName", json=body)
        return _parse_list(resp, dict)

    async def get_image_group(
        self,
        application_name: str | None = None,
        project_id: int | None = None,
        app_id: int | None = None,
        resource_type: str = "queryImageGroup",
    ) -> list[dict]:
        body = _filter_none(
            appId=app_id,
            applicationName=application_name,
            projectId=project_id,
            resourceType=resource_type,
        )
        resp = await self._post("/query/v2.3/queryImageGroup", json=body)
        data = resp.get("data") or resp.get("rows") or []
        return data if isinstance(data, list) else [data] if data else []

    async def get_yaml(self, kind: str, name: str) -> dict:
        return await self._post("/map/v1.8/queryYaml", json={"kind": kind, "name": name})
