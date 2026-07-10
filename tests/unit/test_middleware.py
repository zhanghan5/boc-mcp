import pytest
from mcp.types import ErrorData
from mcp.shared.exceptions import McpError
from boc_mcp.client.errors import (
    BadRequestError, NotFoundError, ForbiddenError, AuthError,
    ConflictError, ServerError, NetworkError, RequestTimeoutError,
)
from boc_mcp.middleware import (
    boc_error_to_mcp, INVALID_PARAMS, NOT_FOUND, PERMISSION_DENIED,
    INTERNAL_ERROR, UNAUTHORIZED,
)

@pytest.mark.parametrize("exc,code", [
    (BadRequestError("bad"), INVALID_PARAMS),
    (NotFoundError("miss"), NOT_FOUND),
    (ForbiddenError("no"), PERMISSION_DENIED),
    (AuthError("expired"), UNAUTHORIZED),
    (ConflictError("dup"), INVALID_PARAMS),
    (ServerError("boom"), INTERNAL_ERROR),
    (NetworkError("net"), INTERNAL_ERROR),
    (RequestTimeoutError("to"), INTERNAL_ERROR),
])
def test_error_mapping(exc, code):
    err = boc_error_to_mcp(exc)
    assert isinstance(err, McpError)
    assert isinstance(err.error, ErrorData)
    assert err.error.code == code
    assert exc.message in err.error.message

def test_non_boc_error_wrapped_as_internal():
    err = boc_error_to_mcp(ValueError("unexpected"))
    assert err.error.code == INTERNAL_ERROR
