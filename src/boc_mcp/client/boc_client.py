from __future__ import annotations

import logging
from collections.abc import AsyncIterator
from typing import TYPE_CHECKING, Any, Protocol, runtime_checkable

import aiohttp

from boc_mcp.client.errors import (
    APIError,
    AuthError,
    BadRequestError,
    ConflictError,
    ForbiddenError,
    NetworkError,
    NotFoundError,
    RequestTimeoutError,
    ServerError,
    is_token_invalid_message,
)
from boc_mcp.client.pagination import paginate
from boc_mcp.config import AppConfig

if TYPE_CHECKING:
    from boc_mcp.auth.token_manager import TokenManager

log = logging.getLogger(__name__)


@runtime_checkable
class BocApiClient(Protocol):
    async def request(
        self, method: str, path: str, *, params: dict | None = None, json: Any = None
    ) -> dict: ...
    async def get(self, path: str, *, params: dict | None = None) -> dict: ...
    async def post(self, path: str, *, json: Any = None) -> dict: ...
    async def put(self, path: str, *, json: Any = None) -> dict: ...
    async def delete(self, path: str) -> dict: ...
    def paginated_get(
        self, path: str, *, page_size: int = 20, **kwargs: Any
    ) -> AsyncIterator[dict]: ...


_STATUS_MAP: dict[int, type[APIError]] = {
    400: BadRequestError,
    401: AuthError,
    403: ForbiddenError,
    404: NotFoundError,
    409: ConflictError,
}


def _full_url(base_url: str, path: str) -> str:
    if path.startswith("http://") or path.startswith("https://"):
        return path
    return f"{base_url.rstrip('/')}/{path.lstrip('/')}"


class BocHttpClient:
    def __init__(self, config: AppConfig, token_manager: TokenManager | None) -> None:
        self._config = config
        self._token_manager = token_manager
        self._session: aiohttp.ClientSession | None = None

    async def __aenter__(self) -> BocHttpClient:
        connector = aiohttp.TCPConnector(ssl=self._config.verify_ssl)
        timeout = aiohttp.ClientTimeout(total=self._config.request_timeout)
        self._session = aiohttp.ClientSession(connector=connector, timeout=timeout)
        return self

    async def __aexit__(self, *exc: Any) -> None:
        if self._session:
            await self._session.close()
            self._session = None

    async def _auth_headers(self) -> dict[str, str]:
        assert self._token_manager is not None
        ts = await self._token_manager.get_token()
        return {
            "token": ts.token,
            "refreshToken": ts.refresh_token,
            "systemId": self._token_manager.system_id,
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    async def request(
        self,
        method: str,
        path: str,
        *,
        params: dict | None = None,
        json: Any = None,
        _retried: bool = False,
    ) -> dict:
        if self._session is None:
            raise RuntimeError("BocHttpClient must be used as an async context manager")
        url = _full_url(self._config.base_url, path)
        headers = await self._auth_headers()
        log.debug("%s %s", method, url)
        try:
            async with self._session.request(
                method, url, params=params, json=json, headers=headers
            ) as resp:
                status = resp.status
                try:
                    body = await resp.json(content_type=None)
                except Exception:
                    body = {"raw": await resp.text()}
                msg = body.get("message", "") if isinstance(body, dict) else ""
                token_invalid = status == 401 or (
                    isinstance(body, dict) and is_token_invalid_message(str(msg))
                )
                if token_invalid and not _retried:
                    log.info("Token invalid, re-logging in")
                    if self._token_manager:
                        self._token_manager.invalidate()
                    return await self.request(method, path, params=params, json=json, _retried=True)
                if status >= 400:
                    self._raise_api_error(status, body)
                return body if isinstance(body, dict) else {"data": body}
        except TimeoutError as e:
            raise RequestTimeoutError(f"request timed out: {method} {path}") from e
        except aiohttp.ClientError as e:
            raise NetworkError(f"network error: {e}") from e

    def _raise_api_error(self, status: int, body: Any) -> None:
        msg = "API error"
        code = None
        if isinstance(body, dict):
            msg = body.get("message") or body.get("msg") or msg
            c = body.get("code")
            code = str(c) if c is not None else None
        exc = _STATUS_MAP.get(status)
        if exc is None:
            exc = ServerError if status >= 500 else APIError
        raise exc(msg, status_code=status, code=code, body=body)

    async def get(self, path: str, *, params: dict | None = None) -> dict:
        return await self.request("GET", path, params=params)

    async def post(self, path: str, *, json: Any = None) -> dict:
        return await self.request("POST", path, json=json)

    async def put(self, path: str, *, json: Any = None) -> dict:
        return await self.request("PUT", path, json=json)

    async def delete(self, path: str) -> dict:
        return await self.request("DELETE", path)

    async def paginated_get(
        self, path: str, *, page_size: int = 20, **kwargs: Any
    ) -> AsyncIterator[dict]:
        size = max(1, min(page_size, 100))

        async def fetch(**kw: Any) -> dict:
            return await self.post(path, json=kw)

        async for item in paginate(fetch, size=size, **kwargs):
            yield item
