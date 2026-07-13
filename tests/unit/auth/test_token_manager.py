import asyncio

import pytest

from boc_mcp.auth.token_manager import TokenManager, TokenSet
from boc_mcp.client.errors import AuthError
from boc_mcp.config import AppConfig


class FakeClient:
    def __init__(self, client_id="abc123", code="code-xyz", token="t", refresh="r"):
        self.client_id = client_id
        self.code = code
        self.token = token
        self.refresh = refresh
        self.get_calls = 0
        self.post_calls = 0
        self.fail_on_call: int | None = None

    async def get(self, path, *, params=None):
        self.get_calls += 1
        if path.startswith("/upmstreeapi/bocPortal/getMenus"):
            return {
                "code": 100000,
                "data": {
                    "isValid": False,
                    "redirectLoginUrl": f"http://host/?clientId={self.client_id}",
                },
                "state": "error",
                "message": "token required",
            }
        if path.startswith("/upmstreeapi/accessToken"):
            if self.fail_on_call and self.get_calls == self.fail_on_call:
                return {"state": "error", "message": "token expired", "code": 401, "data": None}
            return {
                "state": "success",
                "code": 200,
                "data": {
                    "token": self.token,
                    "refreshToken": self.refresh,
                    "expiredTime": "2026-07-10T12:00:00.000+0800",
                    "sessionId": "s",
                },
            }
        return {}

    async def post(self, path, *, json=None):
        self.post_calls += 1
        if path == "/upmstreeapi/login":
            if self.fail_on_call and self.post_calls == self.fail_on_call:
                return {"state": "error", "message": "bad credentials", "code": 401, "data": None}
            assert json["typeConfigId"] == 0
            assert json["userName"]
            assert json["password"]
            assert json["clientId"] == self.client_id
            return {
                "state": "success",
                "code": 200,
                "data": {"code": self.code, "id": 1, "name": json["userName"]},
            }
        return {}


def make_cfg(**kw):
    base = dict(base_url="https://boc.test", username="admin", password="secret")
    base.update(kw)
    return AppConfig(**base)


@pytest.mark.asyncio
async def test_lazy_login_performs_3_steps():
    c = FakeClient()
    tm = TokenManager(make_cfg(), c)
    ts = await tm.get_token()
    assert isinstance(ts, TokenSet)
    assert ts.token == "t"
    assert ts.refresh_token == "r"
    assert ts.client_id == "abc123"
    assert c.get_calls == 2
    assert c.post_calls == 1


@pytest.mark.asyncio
async def test_client_id_cached_after_relogin():
    c = FakeClient()
    tm = TokenManager(make_cfg(), c)
    await tm.get_token()
    tm.invalidate()
    await tm.get_token()
    assert c.get_calls == 3
    assert c.post_calls == 2


@pytest.mark.asyncio
async def test_second_get_uses_cache():
    c = FakeClient()
    tm = TokenManager(make_cfg(), c)
    await tm.get_token()
    await tm.get_token()
    assert c.get_calls == 2
    assert c.post_calls == 1


@pytest.mark.asyncio
async def test_invalidate_relogs():
    c = FakeClient()
    tm = TokenManager(make_cfg(), c)
    await tm.get_token()
    c.post_calls = 0
    c.get_calls = 0
    tm.invalidate()
    await tm.get_token()
    assert c.post_calls == 1


@pytest.mark.asyncio
async def test_concurrent_invalidate_only_relogs_once():
    c = FakeClient()
    tm = TokenManager(make_cfg(), c)
    await tm.get_token()
    c.post_calls = 0
    c.get_calls = 0
    tm.invalidate()
    results = await asyncio.gather(*[tm.get_token() for _ in range(10)])
    assert all(r.token == "t" for r in results)
    assert c.post_calls == 1
    assert c.get_calls == 1


@pytest.mark.asyncio
async def test_login_failure_raises_auth_error():
    c = FakeClient()
    c.fail_on_call = 1
    tm = TokenManager(make_cfg(), c)
    with pytest.raises(AuthError):
        await tm.get_token()


@pytest.mark.asyncio
async def test_system_id_from_config():
    c = FakeClient()
    tm = TokenManager(make_cfg(system_id="sys42"), c)
    assert tm.system_id == "sys42"
