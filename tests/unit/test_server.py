from boc_mcp.config import AppConfig
from boc_mcp.server import create_app


def make_cfg(**kw):
    base = dict(base_url="https://boc.test", username="u", password="p")
    base.update(kw)
    return AppConfig(**base)


def test_create_app_returns_fastmcp():
    from mcp.server.fastmcp import FastMCP

    app = create_app(make_cfg())
    assert isinstance(app, FastMCP)


def test_auth_tools_registered():
    app = create_app(make_cfg())
    tools = app._tool_manager._tools
    assert "boc_auth_status" in tools
    assert "boc_auth_refresh" in tools


def test_instructions_present():
    app = create_app(make_cfg())
    assert "博云" in (app.instructions or "")


def test_custom_health_route_registered():
    app = create_app(make_cfg())
    starlette_app = app.streamable_http_app()
    routes = [r.path for r in starlette_app.routes if hasattr(r, "path")]
    assert "/healthz" in routes
