from __future__ import annotations

import functools
from typing import Any, Callable

from mcp.shared.exceptions import McpError
from mcp.types import ErrorData

from boc_mcp.client.errors import (
    APIError,
    AuthError,
    BadRequestError,
    BocMcpError,
    ConflictError,
    ForbiddenError,
    NetworkError,
    NotFoundError,
    RequestTimeoutError,
    ServerError,
)

INVALID_PARAMS = -32602
NOT_FOUND = -32001
PERMISSION_DENIED = -32002
UNAUTHORIZED = -32003
INTERNAL_ERROR = -32603


def boc_error_to_mcp(err: Exception) -> McpError:
    if isinstance(err, (BadRequestError, ConflictError)):
        code = INVALID_PARAMS
    elif isinstance(err, NotFoundError):
        code = NOT_FOUND
    elif isinstance(err, ForbiddenError):
        code = PERMISSION_DENIED
    elif isinstance(err, AuthError):
        code = UNAUTHORIZED
    elif isinstance(err, (ServerError, NetworkError, RequestTimeoutError)):
        code = INTERNAL_ERROR
    elif isinstance(err, BocMcpError):
        code = INTERNAL_ERROR
    else:
        code = INTERNAL_ERROR
    message = getattr(err, "message", str(err)) or str(err)
    return McpError(ErrorData(code=code, message=message))


def wrap_tool_errors(fn: Callable[..., Any]) -> Callable[..., Any]:
    @functools.wraps(fn)
    async def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            return await fn(*args, **kwargs)
        except McpError:
            raise
        except Exception as e:
            raise boc_error_to_mcp(e) from e
    return wrapper
