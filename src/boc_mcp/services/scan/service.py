from __future__ import annotations

from boc_mcp.models.common import ListResult
from boc_mcp.services.base import BaseService
from boc_mcp.services.scan.models import ScanReport, ScanStrategy


class ScanService(BaseService):
    async def list_strategies(self, page: int = 1, page_size: int = 20) -> ListResult[ScanStrategy]:
        body = {"currPageNum": page, "pageSize": min(page_size, 100)}
        resp = await self._post("/strategy/v3.3/list", json=body)
        return _parse_list(resp, ScanStrategy)

    async def get_report(self, report_id: int) -> dict:
        resp = await self._get(f"/report/v3.3/detail/{report_id}")
        return resp.get("data") or resp

    async def list_reports(self, page: int = 1, page_size: int = 20) -> ListResult[ScanReport]:
        body = {"currPageNum": page, "pageSize": min(page_size, 100)}
        resp = await self._post("/report/v3.3/list", json=body)
        return _parse_list(resp, ScanReport)


def _parse_list(resp: dict, model_cls):
    if isinstance(resp.get("data"), list) and "rows" not in resp:
        items = [model_cls.model_validate(d) for d in resp["data"]]
        return ListResult[model_cls](items=items, total=len(items), page_count=1)
    lr = ListResult.from_legacy(resp, items_key="rows")
    lr.items = [model_cls.model_validate(d) for d in lr.items]
    return lr
