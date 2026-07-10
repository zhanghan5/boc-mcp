from __future__ import annotations
from pydantic import BaseModel

class AuthStatus(BaseModel):
    logged_in: bool
    username: str
    system_id: str
    expired_time: str | None = None
