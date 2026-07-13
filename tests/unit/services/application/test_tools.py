from __future__ import annotations

import pytest

from boc_mcp.config import AppConfig
from boc_mcp.server import create_app


@pytest.fixture
def app():
    cfg = AppConfig(base_url="https://boc.test", username="u", password="p")
    return create_app(cfg)


def test_tools_registered(app):
    tools = app._tool_manager._tools
    assert "boc_app_get" in tools
    assert "boc_app_list" in tools
    for name in ("boc_app_get", "boc_app_list"):
        desc = tools[name].description
        assert desc
        assert any("\u4e00" <= ch <= "\u9fff" for ch in desc)
