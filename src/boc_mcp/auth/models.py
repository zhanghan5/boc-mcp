from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TokenSet:
    token: str
    refresh_token: str
    client_id: str
    session_id: str | None = None
    expired_time: str | None = None
