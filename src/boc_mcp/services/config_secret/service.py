from __future__ import annotations

from boc_mcp.models.common import ListResult
from boc_mcp.services.base import BaseService
from boc_mcp.services.config_secret.models import SecretItem


class ConfigSecretService(BaseService):
    async def list_secrets(
        self,
        master_ip: str,
        namespace: str,
        master_port: int | None = None,
        master_type: str = "https",
        master_version: str | None = None,
        name: str | None = None,
        env_id: int | None = None,
        project_ids: str | None = None,
        registry_id: int | None = None,
        registry_type: str | None = None,
        type_: str | None = None,
        data: dict | None = None,
        label: dict | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> ListResult[SecretItem]:
        body: dict = {
            "masterIp": master_ip,
            "namespace": namespace,
            "masterType": master_type,
            "currPageNum": page,
            "pageSize": min(page_size, 100),
        }
        if master_port is not None:
            body["masterPort"] = master_port
        if master_version is not None:
            body["masterVersion"] = master_version
        if name is not None:
            body["name"] = name
        if env_id is not None:
            body["envId"] = env_id
        if project_ids is not None:
            body["projectIds"] = project_ids
        if registry_id is not None:
            body["registryId"] = registry_id
        if registry_type is not None:
            body["registryType"] = registry_type
        if type_ is not None:
            body["type"] = type_
        if data is not None:
            body["data"] = data
        if label is not None:
            body["label"] = label
        resp = await self._post("/secret/v2.3/list", json=body)
        return _parse_list(resp, SecretItem)


def _parse_list(resp: dict, model_cls):
    if isinstance(resp.get("data"), list) and "rows" not in resp:
        items = [model_cls.model_validate(d) for d in resp["data"]]
        return ListResult[model_cls](items=items, total=len(items), page_count=1)
    lr = ListResult.from_legacy(resp, items_key="rows")
    lr.items = [model_cls.model_validate(d) for d in lr.items]
    return lr
