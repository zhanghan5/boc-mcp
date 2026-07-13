import pytest

from boc_mcp.config import AppConfig
from boc_mcp.server import create_app


@pytest.fixture
def app():
    cfg = AppConfig(base_url="https://boc.test", username="u", password="p")
    return create_app(cfg)


def test_partition_tools_registered(app):
    tools = app._tool_manager._tools
    expected = [
        "boc_partition_list",
        "boc_partition_get_default",
        "boc_partition_get_meta",
        "boc_partition_list_default",
        "boc_partition_list_nodes",
        "boc_partition_list_all_hosts",
        "boc_partition_all_info",
        "boc_partition_detail",
        "boc_partition_list_available",
    ]
    for name in expected:
        assert name in tools, f"missing tool {name}"


def test_tool_descriptions_are_chinese(app):
    tools = app._tool_manager._tools
    for name in [
        "boc_partition_list",
        "boc_partition_get_default",
        "boc_partition_all_info",
        "boc_partition_list_available",
    ]:
        desc = tools[name].description
        assert desc
        assert any("\u4e00" <= ch <= "\u9fff" for ch in desc)
