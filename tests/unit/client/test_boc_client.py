import asyncio, pytest
from boc_mcp.client.boc_client import BocHttpClient
from boc_mcp.client.errors import (
    AuthError, BadRequestError, ForbiddenError, NotFoundError,
    ConflictError, ServerError, NetworkError, RequestTimeoutError,
)
from boc_mcp.auth.models import TokenSet as TS
from boc_mcp.config import AppConfig
import aiohttp


class FakeTokenManager:
    def __init__(self, token="tok", refresh="ref"):
        self.token=token; self.refresh=refresh; self.calls=0; self.invalidations=0
    async def get_token(self):
        self.calls+=1
        return TS(token=self.token, refresh_token=self.refresh, client_id="cid", session_id="s", expired_time=None)
    def invalidate(self): self.invalidations += 1
    @property
    def system_id(self): return "1"


class FakeResponse:
    def __init__(self, status, payload=None, error=None):
        self.status = status
        self._payload = payload
        self._error = error
    async def json(self, content_type=None):
        if self._error: raise self._error
        return self._payload
    async def text(self):
        return str(self._payload) if not self._error else str(self._error)
    async def __aenter__(self): return self
    async def __aexit__(self, *a): return False


class FakeCM:
    def __init__(self, resp): self._resp = resp
    async def __aenter__(self): return await self._resp.__aenter__()
    async def __aexit__(self, *a): return await self._resp.__aexit__(*a)


class FakeSession:
    def __init__(self, responses):
        self._responses = list(responses)
        self._idx = 0
        self.calls = []
    def request(self, method, url, **kw):
        i = self._idx; self._idx += 1
        if i >= len(self._responses):
            raise AssertionError(f"unexpected call {i}: {method} {url}")
        exp_method, prefix, val = self._responses[i]
        assert method == exp_method
        assert str(url).startswith(prefix)
        self.calls.append((method, url, kw))
        if isinstance(val, Exception):
            raise val
        return FakeCM(val)
    async def close(self): pass


@pytest.fixture
def cfg():
    return AppConfig(base_url="https://boc.test", username="u", password="p", request_timeout=5, max_retries=2)


def _mkclient(cfg, responses):
    tm = FakeTokenManager()
    client = BocHttpClient(cfg, tm)
    client._session = FakeSession(responses)
    return client, tm


def _r(status, payload): return FakeResponse(status, payload)

@pytest.mark.asyncio
async def test_get_injects_auth_headers(cfg):
    client, tm = _mkclient(cfg, [("GET","https://boc.test/api/foo", _r(200, {"state":"success","data":{"x":1}}))])
    r = await client.get("/api/foo")
    assert r["data"]["x"] == 1
    kw = client._session.calls[0][2]
    assert kw["headers"]["token"] == "tok"
    assert kw["headers"]["refreshToken"] == "ref"
    assert kw["headers"]["systemId"] == "1"

@pytest.mark.asyncio
async def test_401_triggers_relogin_and_retry(cfg):
    client, tm = _mkclient(cfg, [
        ("GET","https://boc.test/api/foo", _r(401, {"state":"error","message":"token expired"})),
        ("GET","https://boc.test/api/foo", _r(200, {"state":"success","data":"ok"})),
    ])
    r = await client.get("/api/foo")
    assert r["data"] == "ok"
    assert tm.invalidations == 1
    assert tm.calls == 2

@pytest.mark.asyncio
async def test_401_only_retries_once(cfg):
    client, _ = _mkclient(cfg, [
        ("GET","https://boc.test/api/foo", _r(401, {"state":"error","message":"bad"})),
        ("GET","https://boc.test/api/foo", _r(401, {"state":"error","message":"bad"})),
    ])
    with pytest.raises(AuthError):
        await client.get("/api/foo")

@pytest.mark.asyncio
@pytest.mark.parametrize("status,exc", [
    (400,BadRequestError),(403,ForbiddenError),(404,NotFoundError),(409,ConflictError),(500,ServerError),
])
async def test_http_errors_map(cfg, status, exc):
    client,_ = _mkclient(cfg, [("GET","https://boc.test/api/x", _r(status, {"message":f"e{status}"}))])
    with pytest.raises(exc):
        await client.get("/api/x")

@pytest.mark.asyncio
async def test_timeout_raises_timeout_error(cfg):
    client,_ = _mkclient(cfg, [("GET","https://boc.test/api/x", asyncio.TimeoutError())])
    with pytest.raises(RequestTimeoutError):
        await client.get("/api/x")

@pytest.mark.asyncio
async def test_client_error_raises_network_error(cfg):
    client,_ = _mkclient(cfg, [("GET","https://boc.test/api/x", aiohttp.ClientError("boom"))])
    with pytest.raises(NetworkError):
        await client.get("/api/x")

@pytest.mark.asyncio
async def test_not_used_as_context_manager_raises(cfg):
    tm = FakeTokenManager(); client = BocHttpClient(cfg, tm)
    with pytest.raises(RuntimeError):
        await client.get("/foo")

@pytest.mark.asyncio
async def test_path_joining(cfg):
    client,_ = _mkclient(cfg, [("GET","https://boc.test/some/path", _r(200, {"ok":True}))])
    assert (await client.get("some/path"))["ok"] is True
