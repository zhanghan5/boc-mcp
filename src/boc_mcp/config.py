from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class McpConfig(BaseModel):
    host: str = "0.0.0.0"
    port: int = 8000


_BOC_ENV_PREFIX = "BOC_"


class AppConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="BOC_",
        env_nested_delimiter="__",
        case_sensitive=False,
        extra="ignore",
    )

    base_url: str = ""
    username: str = ""
    password: str = ""
    verify_ssl: bool = True
    request_timeout: int = 30
    max_retries: int = 3
    log_level: str = "INFO"
    system_id: str = "1"
    mcp: McpConfig = Field(default_factory=McpConfig)
    config_file: str | None = None

    @field_validator("base_url")
    @classmethod
    def _strip_trailing_slash(cls, v: str) -> str:
        return v.rstrip("/")


def _env_has(key: str) -> bool:
    return (_BOC_ENV_PREFIX + key).upper() in os.environ


def _find_yaml() -> Path | None:
    cfg = os.environ.get("BOC_CONFIG_FILE")
    if cfg:
        p = Path(cfg)
        if p.is_file():
            return p
    for cand in (Path.cwd() / "config.yaml", Path.home() / ".boc-mcp" / "config.yaml"):
        if cand.is_file():
            return cand
    return None


def _load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    if not isinstance(data, dict):
        raise ValueError(f"config file {path} must contain a YAML mapping")
    return data


def load_config() -> AppConfig:
    # Start from env-only (pydantic-settings auto-reads env)
    cfg = AppConfig()
    # Apply yaml values only for fields not set via env
    yaml_path = _find_yaml()
    if yaml_path:
        yd = _load_yaml(yaml_path)
        # base-level fields
        for key in (
            "base_url",
            "username",
            "password",
            "verify_ssl",
            "request_timeout",
            "max_retries",
            "log_level",
            "system_id",
        ):
            if not _env_has(key) and key in yd:
                object.__setattr__(cfg, key, yd[key])
        if "mcp" in yd and isinstance(yd["mcp"], dict):
            mcp_data = dict(cfg.mcp.model_dump())
            for mk, mv in yd["mcp"].items():
                if not _env_has(f"MCP__{mk}"):
                    mcp_data[mk] = mv
            object.__setattr__(cfg, "mcp", McpConfig(**mcp_data))
    if not cfg.base_url or not cfg.username or not cfg.password:
        raise ValueError(
            "Missing required config: base_url, username, password must be provided "
            "via environment variables (BOC_BASE_URL, BOC_USERNAME, BOC_PASSWORD) or config.yaml"
        )
    return cfg
