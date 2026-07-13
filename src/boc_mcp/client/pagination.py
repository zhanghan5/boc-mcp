from __future__ import annotations

from collections.abc import AsyncIterator, Callable, Coroutine
from typing import Any


async def paginate(
    fetch_page: Callable[..., Coroutine[Any, Any, dict]],
    *,
    page_param: str = "currPageNum",
    size_param: str = "pageSize",
    size: int = 20,
    items_key: str = "rows",
    **kwargs: Any,
) -> AsyncIterator[dict]:
    page = 1
    while True:
        body = dict(kwargs)
        body[page_param] = page
        body[size_param] = size
        resp = await fetch_page(**body)
        rows = resp.get(items_key) or resp.get("data", {}).get(items_key) or []
        for item in rows:
            yield item
        total = resp.get("totalCount", 0) or resp.get("data", {}).get("totalCount", 0)
        if page * size >= total or not rows:
            break
        page += 1
