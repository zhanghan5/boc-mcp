from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Any

from boc_mcp.client.boc_client import BocApiClient
from boc_mcp.client.pagination import paginate


class BaseService:
    def __init__(self, client: BocApiClient) -> None:
        self._client = client

    async def _get(self, path: str, *, params: dict | None = None) -> dict:
        return await self._client.get(path, params=params)

    async def _post(self, path: str, *, json: dict | None = None) -> dict:
        return await self._client.post(path, json=json)

    async def _put(self, path: str, *, json: dict | None = None) -> dict:
        return await self._client.put(path, json=json)

    async def _delete(self, path: str) -> dict:
        return await self._client.delete(path)

    async def _list(self, path: str, *, page_size: int = 20, **kwargs: Any) -> AsyncIterator[dict]:
        async def fetch(**kw: Any) -> dict:
            return await self._client.post(path, json=kw)

        async for item in paginate(fetch, size=page_size, **kwargs):
            yield item
