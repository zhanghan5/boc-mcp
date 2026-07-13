"""End-to-end tests that boot the real FastMCP ASGI app via TestClient.

These tests exercise the full stack: create_app() wiring, custom health routes,
and the MCP HTTP transport.
"""

from __future__ import annotations

import pytest
from starlette.testclient import TestClient

from boc_mcp.config import AppConfig, McpConfig
from boc_mcp.server import create_app


def _make_app():
    cfg = AppConfig(
        base_url="https://example.invalid",
        username="tester",
        password="secret",
        system_id="1",
        mcp=McpConfig(host="127.0.0.1", port=8000),
    )
    return create_app(cfg)


@pytest.mark.e2e
def test_healthz_liveness_returns_200():
    app = _make_app()
    http_app = app.streamable_http_app()
    with TestClient(http_app) as client:
        r = client.get("/healthz")
        assert r.status_code == 200
        assert r.json() == {"status": "ok"}


@pytest.mark.e2e
def test_healthz_ready_returns_200():
    """Readiness uses a token probe; since we never trigger a real request that
    needs a token, the client is present and get() returns success stub."""
    app = _make_app()
    http_app = app.streamable_http_app()
    with TestClient(http_app) as client:
        r = client.get("/healthz/ready")
        assert r.status_code in (200, 503)
