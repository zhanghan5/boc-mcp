from __future__ import annotations

from boc_mcp.models.common import ListResult
from boc_mcp.services.application.models import ApplicationSummary
from boc_mcp.services.base import BaseService


class ApplicationService(BaseService):
    async def get(self, app_id: int) -> dict:
        resp = await self._get(f"/applications/{app_id}")
        return resp.get("data") or resp

    async def list(
        self,
        cluster_id: str | None = None,
        project_name: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> ListResult[ApplicationSummary]:
        params: dict = {"currPageNum": page, "pageSize": min(page_size, 100)}
        if cluster_id is not None:
            params["clusterId"] = cluster_id
        if project_name is not None:
            params["projectName"] = project_name
        resp = await self._get("/bocApplication/projects/list", params=params)
        return _parse_list(resp, ApplicationSummary)


def _parse_list(resp: dict, model_cls):
    if isinstance(resp.get("data"), list) and "rows" not in resp:
        items = [model_cls.model_validate(d) for d in resp["data"]]
        return ListResult[model_cls](items=items, total=len(items), page_count=1)
    lr = ListResult.from_legacy(resp, items_key="rows")
    lr.items = [model_cls.model_validate(d) for d in lr.items]
    return lr
