from __future__ import annotations
from boc_mcp.auth.token_manager import TokenManager
from boc_mcp.services.auth.models import AuthStatus


class AuthService:
    def __init__(self, token_manager: TokenManager) -> None:
        self._tm = token_manager

    async def current_token(self):
        return await self._tm.get_token()

    async def refresh(self) -> None:
        self._tm.invalidate()
        await self._tm.get_token()

    async def status(self) -> AuthStatus:
        ts = await self._tm.get_token()
        return AuthStatus(
            logged_in=True,
            username=self._tm._config.username,
            system_id=self._tm.system_id,
            expired_time=ts.expired_time,
        )
