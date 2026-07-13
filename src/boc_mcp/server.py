from __future__ import annotations

from typing import Any

from mcp.server.fastmcp import FastMCP
from starlette.requests import Request
from starlette.responses import JSONResponse

from boc_mcp.auth.token_manager import TokenManager
from boc_mcp.client.boc_client import BocHttpClient
from boc_mcp.config import AppConfig, load_config
from boc_mcp.health import liveness, readiness
from boc_mcp.logging_setup import setup_logging
from boc_mcp.services.application import register_tools as reg_application
from boc_mcp.services.auth import register_tools as reg_auth
from boc_mcp.services.cluster import register_tools as reg_cluster
from boc_mcp.services.config_secret import register_tools as reg_config_secret
from boc_mcp.services.monitor import register_tools as reg_monitor
from boc_mcp.services.network import register_tools as reg_network
from boc_mcp.services.partition import register_tools as reg_partition
from boc_mcp.services.scan import register_tools as reg_scan
from boc_mcp.services.service_tree import register_tools as reg_service_tree
from boc_mcp.services.version import register_tools as reg_version
from boc_mcp.services.workload import register_tools as reg_workload

MCP_INSTRUCTIONS = """你是博云 BeyondContainer 容器云平台的运维助手。
可以通过以 boc_ 开头的工具查询平台资源（集群、节点、工作负载、容器、监控、版本镜像等）。
本 MCP 目前只提供查询能力。所有列表类工具有 page/page_size 参数，page_size 最大 100。
关键概念：clusterId（集群 id）、envId（租户/环境 id）、projectId（应用 id）、
applicationId（服务/版本 id）、namespace（命名空间）是常见筛选条件。"""

_REGISTRIES: list[Any] = [
    reg_auth,
    reg_application,
    reg_cluster,
    reg_scan,
    reg_service_tree,
    reg_config_secret,
    reg_network,
    reg_version,
    reg_workload,
    reg_monitor,
    reg_partition,
]


def create_app(config: AppConfig | None = None) -> FastMCP:
    config = config or load_config()
    setup_logging(config.log_level)

    mcp = FastMCP(
        "boc-mcp",
        instructions=MCP_INSTRUCTIONS,
        host=config.mcp.host,
        port=config.mcp.port,
    )

    client = BocHttpClient(config, None)
    token_mgr = TokenManager(config, client)
    client._token_manager = token_mgr

    @mcp.custom_route("/healthz", methods=["GET"])
    async def _healthz(request: Request) -> JSONResponse:
        return await liveness(request)

    @mcp.custom_route("/healthz/ready", methods=["GET"])
    async def _ready(request: Request) -> JSONResponse:
        request.app.state.boc_client = client
        return await readiness(request)

    for reg in _REGISTRIES:
        reg(mcp, client, token_manager=token_mgr)

    return mcp


def run() -> None:
    config = load_config()
    app = create_app(config)
    app.run(transport="streamable-http")


if __name__ == "__main__":
    run()
