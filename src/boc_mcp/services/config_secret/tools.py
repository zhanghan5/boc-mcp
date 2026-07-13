from __future__ import annotations

from typing import Any

from mcp.server.fastmcp import FastMCP

from boc_mcp.client.boc_client import BocApiClient
from boc_mcp.middleware import wrap_tool_errors
from boc_mcp.services.config_secret.service import ConfigSecretService


def register_tools(mcp: FastMCP, client: BocApiClient, **_: Any) -> None:
    svc = ConfigSecretService(client)

    @mcp.tool(description="查询指定集群和命名空间下的 Secret 列表，支持按名称/类型过滤，分页返回。")
    @wrap_tool_errors
    async def boc_secret_list(
        master_ip: str,
        namespace: str,
        master_port: int | None = None,
        master_type: str = "https",
        master_version: str | None = None,
        name: str | None = None,
        env_id: int | None = None,
        project_ids: str | None = None,
        registry_id: int | None = None,
        registry_type: str | None = None,
        type_: str | None = None,
        data: dict | None = None,
        label: dict | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> dict:
        r = await svc.list_secrets(
            master_ip=master_ip,
            namespace=namespace,
            master_port=master_port,
            master_type=master_type,
            master_version=master_version,
            name=name,
            env_id=env_id,
            project_ids=project_ids,
            registry_id=registry_id,
            registry_type=registry_type,
            type_=type_,
            data=data,
            label=label,
            page=page,
            page_size=page_size,
        )
        return r.model_dump(by_alias=True)
