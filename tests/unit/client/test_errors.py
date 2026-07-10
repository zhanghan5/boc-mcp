import pytest
from boc_mcp.client.errors import (
    APIError, AuthError, BadRequestError, BocMcpError, ConflictError,
    ForbiddenError, NetworkError, NotFoundError, RequestTimeoutError, ServerError,
    is_token_invalid_message,
)

def test_base_error_has_message():
    err = BocMcpError("something broke", details={"x": 1})
    assert str(err) == "something broke"
    assert err.details == {"x": 1}

def test_api_error_carries_status_and_body():
    err = APIError("bad", status_code=400, code="BAD_REQ", body={"a": 1})
    assert err.status_code == 400
    assert err.code == "BAD_REQ"
    assert err.body == {"a": 1}

@pytest.mark.parametrize("cls,status", [
    (BadRequestError, 400), (ForbiddenError, 403), (NotFoundError, 404),
    (ConflictError, 409), (ServerError, 500), (AuthError, 401),
])
def test_api_error_subclasses_default_status(cls, status):
    err = cls("msg")
    assert err.status_code == status
    assert isinstance(err, APIError)
    assert isinstance(err, BocMcpError)

def test_network_and_timeout_not_api_errors():
    assert isinstance(NetworkError("net"), BocMcpError)
    assert not isinstance(NetworkError("net"), APIError)
    assert isinstance(RequestTimeoutError("to"), BocMcpError)

@pytest.mark.parametrize("msg,expected", [
    ("token expired", True), ("Token 已失效，请重新登录", True),
    ("登录过期", True), ("请求头中 token,refreshToken 必填", True),
    ("invalid token", True), ("everything ok", False), ("查询成功", False),
])
def test_is_token_invalid_message(msg, expected):
    assert is_token_invalid_message(msg) is expected
