import pytest
from starlette.testclient import TestClient
from starlette.applications import Starlette
from starlette.routing import Route
from boc_mcp.health import liveness, readiness

class OkClient:
    async def get(self, path, *, params=None):
        return {"state": "success", "data": {"name": "u"}}
class FailClient:
    async def get(self, path, *, params=None):
        raise RuntimeError("down")

def make_app(client=None):
    app = Starlette(routes=[Route("/healthz", liveness), Route("/healthz/ready", readiness)])
    app.state.boc_client = client
    return app

def test_liveness():
    with TestClient(make_app()) as c:
        r = c.get("/healthz")
        assert r.status_code == 200
        assert r.json() == {"status":"ok"}

def test_readiness_ok():
    with TestClient(make_app(OkClient())) as c:
        r = c.get("/healthz/ready")
        assert r.status_code == 200
        assert r.json()["status"] == "ready"

def test_readiness_fail():
    with TestClient(make_app(FailClient())) as c:
        r = c.get("/healthz/ready")
        assert r.status_code == 503
        assert r.json()["status"] == "not_ready"

def test_readiness_no_client_is_ready():
    with TestClient(make_app(None)) as c:
        r = c.get("/healthz/ready")
        assert r.status_code == 200
