from __future__ import annotations

from boc_mcp.services.base import BaseService
from boc_mcp.services.service_tree.models import ServiceTreeNode


class ServiceTreeService(BaseService):
    async def get_tree(
        self,
        p_type: str | None = None,
        pid: int | None = None,
        type_: str | None = None,
    ) -> list[ServiceTreeNode]:
        params: dict = {}
        if p_type is not None:
            params["pType"] = p_type
        if pid is not None:
            params["pid"] = pid
        if type_ is not None:
            params["type"] = type_
        resp = await self._get("/service-tree", params=params)
        if isinstance(resp, list):
            data = resp
        elif isinstance(resp, dict) and isinstance(resp.get("data"), list):
            data = resp["data"]
        else:
            data = []
        return [ServiceTreeNode.model_validate(d) for d in data]
