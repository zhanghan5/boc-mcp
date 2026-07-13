from __future__ import annotations

import asyncio
import logging
from typing import Protocol
from urllib.parse import parse_qs, urlparse

from boc_mcp.auth.models import TokenSet
from boc_mcp.client.errors import AuthError
from boc_mcp.config import AppConfig

log = logging.getLogger(__name__)

_LOGIN_PATH = "/upmstreeapi/login"
_MENUS_PATH = "/upmstreeapi/bocPortal/getMenus"
_TOKEN_PATH = "/upmstreeapi/accessToken"


class _AuthClient(Protocol):
    async def get(self, path: str, *, params: dict | None = None) -> dict: ...
    async def post(self, path: str, *, json: dict | None = None) -> dict: ...


class TokenManager:
    def __init__(self, config: AppConfig, client: _AuthClient) -> None:
        self._config = config
        self._client = client
        self._token: TokenSet | None = None
        self._client_id: str | None = None
        self._lock = asyncio.Lock()

    async def get_token(self) -> TokenSet:
        if self._token is not None:
            return self._token
        async with self._lock:
            if self._token is not None:
                return self._token
            self._token = await self._do_login()
            return self._token

    def invalidate(self) -> None:
        self._token = None
        log.info("Token invalidated; next request will re-login")

    @property
    def system_id(self) -> str:
        return self._config.system_id

    async def _do_login(self) -> TokenSet:
        client_id = await self._ensure_client_id()
        body = {
            "typeConfigId": 0,
            "userName": self._config.username,
            "password": self._config.password,
            "clientId": client_id,
        }
        log.info("Logging in as %s", self._config.username)
        login_resp = await self._client.post(_LOGIN_PATH, json=body)
        if login_resp.get("state") != "success":
            raise AuthError(f"login failed: {login_resp.get('message') or 'unknown'}")
        code = (login_resp.get("data") or {}).get("code")
        if not code:
            raise AuthError("login response missing data.code")
        tok_resp = await self._client.get(f"{_TOKEN_PATH}?code={code}")
        if tok_resp.get("state") != "success":
            raise AuthError(f"get token failed: {tok_resp.get('message') or 'unknown'}")
        data = tok_resp.get("data") or {}
        if not data.get("token"):
            raise AuthError("token response missing token field")
        return TokenSet(
            token=data["token"],
            refresh_token=data.get("refreshToken", ""),
            client_id=client_id,
            session_id=data.get("sessionId"),
            expired_time=data.get("expiredTime"),
        )

    async def _ensure_client_id(self) -> str:
        if self._client_id is not None:
            return self._client_id
        resp = await self._client.get(_MENUS_PATH)
        url = (resp.get("data") or {}).get("redirectLoginUrl", "")
        qs = parse_qs(urlparse(url).query)
        cid_list = qs.get("clientId")
        if not cid_list or not cid_list[0]:
            raise AuthError("could not extract clientId from getMenus response")
        self._client_id = cid_list[0]
        return self._client_id
