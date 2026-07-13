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
    assert "boc_service_tree" in tools
    desc = tools["boc_service_tree"].description
    assert desc
    assert any("\u4e00" <= ch <= "\u9fff" for ch in desc)
