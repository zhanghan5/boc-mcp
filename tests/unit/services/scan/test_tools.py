import pytest

from boc_mcp.config import AppConfig
from boc_mcp.server import create_app


@pytest.fixture
def app():
    cfg = AppConfig(base_url="https://boc.test", username="u", password="p")
    return create_app(cfg)


def test_scan_tools_registered(app):
    tools = app._tool_manager._tools
    scan_tools = [n for n in tools if n.startswith("boc_scan_")]
    assert "boc_scan_list_strategies" in scan_tools
    assert "boc_scan_get_report" in scan_tools
    assert "boc_scan_list_reports" in scan_tools
    assert len(scan_tools) == 3


def test_scan_tool_descriptions_are_chinese(app):
    tools = app._tool_manager._tools
    for name in ["boc_scan_list_strategies", "boc_scan_get_report", "boc_scan_list_reports"]:
        assert tools[name].description
        assert any("\u4e00" <= c <= "\u9fff" for c in tools[name].description)
