from __future__ import annotations

from typing import Any


class BocMcpError(Exception):
    def __init__(self, message: str, details: dict[str, Any] | None = None) -> None:
        self.message = message
        self.details = details
        super().__init__(message)


class APIError(BocMcpError):
    default_status: int = 500

    def __init__(
        self,
        message: str,
        *,
        status_code: int | None = None,
        code: str | None = None,
        body: Any = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message, details=details)
        self.status_code = status_code if status_code is not None else self.default_status
        self.code = code
        self.body = body


class BadRequestError(APIError):
    default_status = 400


class AuthError(APIError):
    default_status = 401


class ForbiddenError(APIError):
    default_status = 403


class NotFoundError(APIError):
    default_status = 404


class ConflictError(APIError):
    default_status = 409


class ServerError(APIError):
    default_status = 500


class NetworkError(BocMcpError):
    pass


class RequestTimeoutError(BocMcpError):
    pass


_TOKEN_INVALID_KEYWORDS = (
    "token",
    "登录过期",
    "token 过期",
    "token失效",
    "token已失效",
    "登录已失效",
    "未登录",
    "请重新登录",
    "过期",
    "invalid token",
    "expired",
    "unauthorized",
)


def is_token_invalid_message(message: str) -> bool:
    if not message:
        return False
    low = message.lower()
    return any(kw in low for kw in _TOKEN_INVALID_KEYWORDS)
