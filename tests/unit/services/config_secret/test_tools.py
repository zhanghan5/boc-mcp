import pytest

from boc_mcp.config import AppConfig
from boc_mcp.server import create_app


@pytest.fixture
def app():
    cfg = AppConfig(base_url="https://boc.test", username="u", password="p")
    return create_app(cfg)


def test_secret_tool_registered(app):
    tools = app._tool_manager._tools
    assert "boc_secret_list" in tools


def test_secret_tool_description_is_chinese(app):
    tools = app._tool_manager._tools
    desc = tools["boc_secret_list"].description
    assert desc
    assert any("\u4e00" <= c <= "\u9fff" for c in desc)
    assert "Secret" in desc
