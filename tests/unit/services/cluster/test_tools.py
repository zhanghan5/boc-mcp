import pytest

from boc_mcp.config import AppConfig
from boc_mcp.server import create_app


class FakeTM:
    def __init__(self):
        self.calls = 0
        self.invalidations = 0

    async def get_token(self):
        self.calls += 1
        from boc_mcp.auth.models import TokenSet

        return TokenSet(token="t", refresh_token="r", client_id="c")

    def invalidate(self):
        self.invalidations += 1

    @property
    def system_id(self):
        return "1"


@pytest.fixture
def app():
    cfg = AppConfig(base_url="https://boc.test", username="u", password="p")
    app = create_app(cfg)
    return app


def test_cluster_tools_registered(app):
    tools = app._tool_manager._tools
    cluster_tools = [n for n in tools if n.startswith("boc_cluster_")]
    assert "boc_cluster_list" in cluster_tools
    assert "boc_cluster_list_nodes" in cluster_tools
    assert "boc_cluster_get_state" in cluster_tools
    assert len(cluster_tools) == 10


def test_tool_descriptions_are_chinese(app):
    tools = app._tool_manager._tools
    for name in ["boc_cluster_list", "boc_cluster_get_monitor", "boc_cluster_list_nodes"]:
        assert tools[name].description
        assert any("\u4e00" <= c <= "\u9fff" for c in tools[name].description)
