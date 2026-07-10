### Task 1：项目脚手架与依赖配置

**Files:**
- Create: `pyproject.toml`
- Create: `src/boc_mcp/__init__.py`
- Create: `src/boc_mcp/auth/__init__.py`
- Create: `src/boc_mcp/client/__init__.py`
- Create: `src/boc_mcp/models/__init__.py`
- Create: `src/boc_mcp/services/__init__.py`
- Create: 各 service 子包 `__init__.py`（11 个）
- Create: `tests/__init__.py`, `tests/unit/__init__.py`, `tests/integration/__init__.py`, `tests/e2e/__init__.py`
- Create: `README.md`, `.gitignore`, `config/config.example.yaml`
- Create: `src/boc_mcp/__main__.py` (空占位，后续填)

- [ ] **Step 1: 创建 `pyproject.toml`**

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "boc-mcp"
version = "0.1.0"
description = "MCP Server for BoCloud BeyondContainer platform"
requires-python = ">=3.12"
dependencies = [
    "mcp[cli]>=1.0.0",
    "aiohttp>=3.10.0",
    "pydantic>=2.7.0",
    "pydantic-settings>=2.3.0",
    "pyyaml>=6.0.1",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.2.0",
    "pytest-asyncio>=0.23.7",
    "pytest-cov>=5.0.0",
    "pytest-mock>=3.14.0",
    "aioresponses>=0.7.6",
    "ruff>=0.5.0",
    "mypy>=1.10.0",
]

[tool.hatch.build.targets.wheel]
packages = ["src/boc_mcp"]

[tool.pytest.ini_options]
testpaths = ["tests"]
asyncio_mode = "auto"
markers = [
    "integration: marks integration tests against real platform",
    "e2e: marks end-to-end MCP tests",
]
addopts = "-m 'not integration and not e2e' --cov=boc_mcp --cov-report=term-missing"

[tool.ruff]
line-length = 100
target-version = "py312"
src = ["src", "tests"]

[tool.ruff.lint]
select = ["E", "F", "I", "N", "W", "UP", "B", "SIM"]

[tool.mypy]
python_version = "3.12"
strict = true
warn_return_any = true
warn_unused_configs = true
packages = ["boc_mcp"]
```

- [ ] **Step 2: 创建 `.gitignore`**

```
__pycache__/
*.pyc
*.pyo
.venv/
venv/
*.egg-info/
dist/
build/
.pytest_cache/
.mypy_cache/
.ruff_cache/
htmlcov/
.coverage
coverage.xml
config.yaml
!config/config.example.yaml
*.log
```

- [ ] **Step 3: 创建所有包目录和空 `__init__.py`**

`src/boc_mcp/__init__.py` 写入版本号：
```python
__version__ = "0.1.0"
```
其他 `__init__.py` 保持空文件。

- [ ] **Step 4: 创建 `config/config.example.yaml`**

```yaml
base_url: "https://boc.example.com"
username: "admin"
password: "change-me"
verify_ssl: true
request_timeout: 30
max_retries: 3
log_level: "INFO"
system_id: "1"
mcp:
  host: "0.0.0.0"
  port: 8000
```

- [ ] **Step 5: 创建 `README.md` 骨架**

```markdown
# boc-mcp

博云 BeyondContainer 容器云平台 MCP Server。

## 快速开始

（后续填充）

## 配置

通过环境变量或 `config.yaml` 配置，见 `config/config.example.yaml`。

## 工具

全部 `boc_*` 前缀，详见设计文档。
```

- [ ] **Step 6: 验证环境**

```bash
cd D:\项目\boc-mcp
uv venv
uv pip install -e ".[dev]"
uv run python -c "import boc_mcp; print(boc_mcp.__version__)"
```
预期输出：`0.1.0`

- [ ] **Step 7: 提交**

```bash
git init  # 若尚未初始化
git add -A
git commit -m "chore: scaffold project with pyproject.toml and package layout"
```

---

### Task 2：配置模块 (`config.py`) 与 TDD

**Files:**
- Create: `src/boc_mcp/config.py`
- Create: `tests/unit/test_config.py`

- [ ] **Step 1: 写失败测试 — `tests/unit/test_config.py`**

```python
import os
from pathlib import Path
import pytest
from boc_mcp.config import AppConfig, McpConfig, load_config


def test_defaults_no_env_no_file(monkeypatch, tmp_path):
    for k in list(os.environ):
        if k.startswith("BOC_"):
            monkeypatch.delenv(k)
    monkeypatch.chdir(tmp_path)
    with pytest.raises(ValueError):
        load_config()


def test_env_only_minimal(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("BOC_BASE_URL", "https://boc.test")
    monkeypatch.setenv("BOC_USERNAME", "admin")
    monkeypatch.setenv("BOC_PASSWORD", "secret")
    cfg = load_config()
    assert cfg.base_url == "https://boc.test"
    assert cfg.username == "admin"
    assert cfg.password == "secret"
    assert cfg.system_id == "1"
    assert cfg.verify_ssl is True
    assert cfg.request_timeout == 30
    assert cfg.max_retries == 3
    assert cfg.log_level == "INFO"
    assert cfg.mcp.host == "0.0.0.0"
    assert cfg.mcp.port == 8000


def test_yaml_file(monkeypatch, tmp_path):
    yaml_content = """
base_url: "https://boc.yaml"
username: "yamluser"
password: "yamlpass"
request_timeout: 15
mcp:
  port: 9000
"""
    (tmp_path / "config.yaml").write_text(yaml_content, encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    for k in list(os.environ):
        if k.startswith("BOC_"):
            monkeypatch.delenv(k)
    cfg = load_config()
    assert cfg.base_url == "https://boc.yaml"
    assert cfg.request_timeout == 15
    assert cfg.mcp.port == 9000


def test_env_overrides_yaml(monkeypatch, tmp_path):
    (tmp_path / "config.yaml").write_text(
        "base_url: 'https://from.yaml'\nusername: 'u'\npassword: 'p'\n", encoding="utf-8"
    )
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("BOC_BASE_URL", "https://from.env")
    cfg = load_config()
    assert cfg.base_url == "https://from.env"


def test_config_file_env(monkeypatch, tmp_path):
    cfg_file = tmp_path / "custom.yaml"
    cfg_file.write_text(
        "base_url: 'https://custom'\nusername: 'u'\npassword: 'p'\n", encoding="utf-8"
    )
    monkeypatch.setenv("BOC_CONFIG_FILE", str(cfg_file))
    monkeypatch.chdir(tmp_path)
    cfg = load_config()
    assert cfg.base_url == "https://custom"


def test_base_url_trailing_slash_stripped():
    cfg = AppConfig(base_url="https://boc.test/", username="u", password="p")
    assert cfg.base_url == "https://boc.test"
```

- [ ] **Step 2: 运行测试，确认失败**

```bash
uv run pytest tests/unit/test_config.py -v
```
预期：`ImportError`（config 模块不存在）

- [ ] **Step 3: 写最小实现 — `src/boc_mcp/config.py`**

```python
from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class McpConfig(BaseModel):
    host: str = "0.0.0.0"
    port: int = 8000


class AppConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="BOC_",
        env_nested_delimiter="__",
        case_sensitive=False,
        extra="ignore",
    )

    base_url: str
    username: str
    password: str
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

    @classmethod
    def _find_yaml(cls) -> Path | None:
        import os

        if cfg_file := os.environ.get("BOC_CONFIG_FILE"):
            p = Path(cfg_file)
            return p if p.is_file() else None
        candidates = [
            Path.cwd() / "config.yaml",
            Path.home() / ".boc-mcp" / "config.yaml",
        ]
        for p in candidates:
            if p.is_file():
                return p
        return None

    @classmethod
    def _load_yaml(cls, path: Path) -> dict[str, Any]:
        with path.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        if not isinstance(data, dict):
            raise ValueError(f"config file {path} must contain a YAML mapping")
        return data


def load_config() -> AppConfig:
    yaml_path = AppConfig._find_yaml()
    yaml_data = AppConfig._load_yaml(yaml_path) if yaml_path else {}
    return AppConfig(**yaml_data)
```

- [ ] **Step 4: 运行测试，确认通过**

```bash
uv run pytest tests/unit/test_config.py -v
```
预期：全部 PASS

- [ ] **Step 5: 运行 lint + type check**

```bash
uv run ruff check src tests
uv run mypy src/boc_mcp/config.py
```

- [ ] **Step 6: 提交**

```bash
git add src/boc_mcp/config.py tests/unit/test_config.py
git commit -m "feat(config): add AppConfig with env and yaml loading"
```

---

### Task 3：错误类型体系 (`client/errors.py`)

**Files:**
- Create: `src/boc_mcp/client/errors.py`
- Create: `tests/unit/client/__init__.py`
- Create: `tests/unit/client/test_errors.py`

- [ ] **Step 1: 写失败测试 — `tests/unit/client/test_errors.py`**

```python
import pytest
from boc_mcp.client.errors import (
    APIError,
    AuthError,
    BadRequestError,
    BocMcpError,
    ConflictError,
    ForbiddenError,
    NetworkError,
    NotFoundError,
    RequestTimeoutError,
    ServerError,
    is_token_invalid_message,
)


def test_base_error_has_message():
    err = BocMcpError("something broke", details={"x": 1})
    assert str(err) == "something broke"
    assert err.details == {"x": 1}


def test_api_error_carries_status_and_body():
    err = APIError("bad", status_code=400, code="BAD_REQ", body={"a": 1})
    assert err.status_code == 400
    assert err.code == "BAD_REQ"
    assert err.body == {"a": 1}


@pytest.mark.parametrize(
    "cls,status",
    [
        (BadRequestError, 400),
        (ForbiddenError, 403),
        (NotFoundError, 404),
        (ConflictError, 409),
        (ServerError, 500),
        (AuthError, 401),
    ],
)
def test_api_error_subclasses_default_status(cls, status):
    err = cls("msg")
    assert err.status_code == status
    assert isinstance(err, APIError)
    assert isinstance(err, BocMcpError)


def test_network_and_timeout_not_api_errors():
    assert isinstance(NetworkError("net"), BocMcpError)
    assert not isinstance(NetworkError("net"), APIError)
    assert isinstance(RequestTimeoutError("to"), BocMcpError)


@pytest.mark.parametrize(
    "msg,expected",
    [
        ("token expired", True),
        ("Token 已失效，请重新登录", True),
        ("登录过期", True),
        ("请求头中 token,refreshToken 必填", True),
        ("invalid token", True),
        ("everything ok", False),
        ("查询成功", False),
    ],
)
def test_is_token_invalid_message(msg, expected):
    assert is_token_invalid_message(msg) is expected
```

- [ ] **Step 2: 运行测试，确认失败**

```bash
uv run pytest tests/unit/client/test_errors.py -v
```
预期：`ImportError`

- [ ] **Step 3: 实现 `src/boc_mcp/client/errors.py`**

```python
from __future__ import annotations

from typing import Any


class BocMcpError(Exception):
    """Base class for all boc-mcp errors."""

    def __init__(self, message: str, details: dict[str, Any] | None = None) -> None:
        self.message = message
        self.details = details
        super().__init__(message)


class APIError(BocMcpError):
    """Error returned by the BoCloud API with HTTP status code."""

    default_status: int = 500

    def __init__(
        self,
        message: str,
        *,
        status_code: int | None = None,
        code: str | None = None,
        body: Any = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message, details=details)
        self.status_code = status_code if status_code is not None else self.default_status
        self.code = code
        self.body = body


class BadRequestError(APIError):
    default_status = 400


class AuthError(APIError):
    default_status = 401


class ForbiddenError(APIError):
    default_status = 403


class NotFoundError(APIError):
    default_status = 404


class ConflictError(APIError):
    default_status = 409


class ServerError(APIError):
    default_status = 500


class NetworkError(BocMcpError):
    pass


class RequestTimeoutError(BocMcpError):
    pass


_TOKEN_INVALID_KEYWORDS = (
    "token",
    "登录过期",
    "token 过期",
    "token失效",
    "token已失效",
    "登录已失效",
    "未登录",
    "请重新登录",
    "过期",
    "invalid token",
    "expired",
    "unauthorized",
)


def is_token_invalid_message(message: str) -> bool:
    """Heuristically decide whether an error message indicates auth token failure."""
    if not message:
        return False
    low = message.lower()
    return any(kw in low for kw in _TOKEN_INVALID_KEYWORDS)
```

- [ ] **Step 4: 运行测试通过**

```bash
uv run pytest tests/unit/client/test_errors.py -v
```
预期：全部 PASS

- [ ] **Step 5: 提交**

```bash
git add src/boc_mcp/client/errors.py tests/unit/client/
git commit -m "feat(errors): add BocMcpError hierarchy and token-invalid detection"
```

---

### Task 4：Token 管理器 (`auth/token_manager.py`) — 3 步登录

**Files:**
- Create: `src/boc_mcp/auth/models.py`
- Create: `src/boc_mcp/auth/token_manager.py`
- Create: `tests/unit/auth/__init__.py`
- Create: `tests/unit/auth/test_token_manager.py`

- [ ] **Step 1: 写失败测试 — `tests/unit/auth/test_token_manager.py`**

```python
import asyncio
import pytest
from boc_mcp.auth.token_manager import TokenManager, TokenSet
from boc_mcp.client.errors import AuthError


class FakeClient:
    """In-memory fake BocApiClient just for login endpoints."""
    def __init__(self, client_id="abc123", code="code-xyz", token="t", refresh="r"):
        self.client_id = client_id
        self.code = code
        self.token = token
        self.refresh = refresh
        self.get_calls = 0
        self.post_calls = 0
        self.fail_on_call: int | None = None  # 1-based index of get_token to fail

    async def get(self, path, *, params=None):
        self.get_calls += 1
        if path.startswith("/upmstreeapi/bocPortal/getMenus"):
            return {"code": 100000, "data": {"isValid": False,
                "redirectLoginUrl": f"http://host/?clientId={self.client_id}"},
                "state": "error", "message": "token required"}
        if path.startswith("/upmstreeapi/accessToken"):
            if self.fail_on_call and self.get_calls == self.fail_on_call:
                return {"state": "error", "message": "token expired", "code": 401, "data": None}
            return {"state": "success", "code": 200, "data": {
                "token": self.token, "refreshToken": self.refresh,
                "expiredTime": "2026-07-10T12:00:00.000+0800", "sessionId": "s"}}
        raise AssertionError(f"unexpected GET {path}")

    async def post(self, path, *, json=None):
        self.post_calls += 1
        if path == "/upmstreeapi/login":
            assert json["typeConfigId"] == 0
            assert json["userName"]
            assert json["password"]
            assert json["clientId"] == self.client_id
            return {"state": "success", "code": 200,
                    "data": {"code": self.code, "id": 1, "name": json["userName"]}}
        raise AssertionError(f"unexpected POST {path}")


def make_cfg(tmp_path, **overrides):
    from boc_mcp.config import AppConfig
    return AppConfig(
        base_url="https://boc.test", username="admin", password="secret",
        **overrides,
    )


@pytest.mark.asyncio
async def test_lazy_login_performs_3_steps(tmp_path):
    client = FakeClient()
    cfg = make_cfg(tmp_path)
    tm = TokenManager(cfg, client)
    ts = await tm.get_token()
    assert isinstance(ts, TokenSet)
    assert ts.token == "t"
    assert ts.refresh_token == "r"
    assert ts.client_id == "abc123"
    assert client.get_calls == 2  # getMenus + accessToken
    assert client.post_calls == 1  # login


@pytest.mark.asyncio
async def test_client_id_is_cached(tmp_path):
    client = FakeClient()
    tm = TokenManager(make_cfg(tmp_path), client)
    await tm.get_token()
    await tm.invalidate()  # force re-login
    await tm.get_token()
    # getMenus only called once; accessToken called twice (initial + after invalidate)
    assert client.get_calls == 3
    assert client.post_calls == 2


@pytest.mark.asyncio
async def test_second_get_token_uses_cache(tmp_path):
    client = FakeClient()
    tm = TokenManager(make_cfg(tmp_path), client)
    await tm.get_token()
    await tm.get_token()
    assert client.get_calls == 2
    assert client.post_calls == 1


@pytest.mark.asyncio
async def test_invalidate_clears_cache_and_relogs(tmp_path):
    client = FakeClient()
    tm = TokenManager(make_cfg(tmp_path), client)
    ts1 = await tm.get_token()
    tm.invalidate()
    ts2 = await tm.get_token()
    assert ts1.token == ts2.token  # same fake returns
    assert client.post_calls == 2


@pytest.mark.asyncio
async def test_concurrent_invalidate_only_relogs_once(tmp_path):
    client = FakeClient()
    tm = TokenManager(make_cfg(tmp_path), client)
    await tm.get_token()
    client.post_calls = 0
    client.get_calls = 0
    tm.invalidate()
    results = await asyncio.gather(*[tm.get_token() for _ in range(10)])
    assert all(r.token == "t" for r in results)
    assert client.post_calls == 1  # only one login
    assert client.get_calls == 1   # only one accessToken


@pytest.mark.asyncio
async def test_login_failure_raises_auth_error(tmp_path):
    class FailingClient(FakeClient):
        async def post(self, path, *, json=None):
            return {"state": "error", "message": "bad credentials", "code": 401, "data": None}
    tm = TokenManager(make_cfg(tmp_path), FailingClient())
    with pytest.raises(AuthError):
        await tm.get_token()
```

- [ ] **Step 2: 运行测试，确认失败**

```bash
uv run pytest tests/unit/auth/test_token_manager.py -v
```
预期：`ImportError`

- [ ] **Step 3: 先写 `src/boc_mcp/auth/models.py`**

```python
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TokenSet:
    token: str
    refresh_token: str
    client_id: str
    session_id: str | None = None
    expired_time: str | None = None
```

- [ ] **Step 4: 实现 `src/boc_mcp/auth/token_manager.py`**

```python
from __future__ import annotations

import asyncio
import logging
from typing import Protocol

from boc_mcp.auth.models import TokenSet
from boc_mcp.config import AppConfig
from boc_mcp.client.errors import AuthError, is_token_invalid_message

log = logging.getLogger(__name__)


class _AuthClient(Protocol):
    """Minimal client interface needed by TokenManager."""
    async def get(self, path: str, *, params: dict | None = None) -> dict: ...
    async def post(self, path: str, *, json: dict | None = None) -> dict: ...


_LOGIN_PATH = "/upmstreeapi/login"
_MENUS_PATH = "/upmstreeapi/bocPortal/getMenus"
_TOKEN_PATH = "/upmstreeapi/accessToken"


class TokenManager:
    """Manages BoCloud 3-step login and token caching."""

    def __init__(self, config: AppConfig, client: _AuthClient) -> None:
        self._config = config
        self._client = client
        self._token: TokenSet | None = None
        self._client_id: str | None = None
        self._lock = asyncio.Lock()

    async def get_token(self) -> TokenSet:
        if self._token is not None:
            return self._token
        async with self._lock:
            if self._token is not None:
                return self._token
            self._token = await self._do_login()
            return self._token

    def invalidate(self) -> None:
        self._token = None
        log.info("Token invalidated; next request will re-login")

    @property
    def system_id(self) -> str:
        return self._config.system_id

    async def _do_login(self) -> TokenSet:
        client_id = await self._ensure_client_id()
        login_body = {
            "typeConfigId": 0,
            "userName": self._config.username,
            "password": self._config.password,
            "clientId": client_id,
        }
        log.info("Logging in as %s", self._config.username)
        login_resp = await self._client.post(_LOGIN_PATH, json=login_body)
        if login_resp.get("state") != "success":
            msg = login_resp.get("message") or "login failed"
            raise AuthError(f"login failed: {msg}")
        code = login_resp.get("data", {}).get("code")
        if not code:
            raise AuthError("login response missing data.code")
        token_resp = await self._client.get(f"{_TOKEN_PATH}?code={code}")
        if token_resp.get("state") != "success":
            msg = token_resp.get("message") or "failed to get token"
            raise AuthError(f"get token failed: {msg}")
        data = token_resp.get("data") or {}
        if not data.get("token"):
            raise AuthError("token response missing token field")
        ts = TokenSet(
            token=data["token"],
            refresh_token=data.get("refreshToken", ""),
            client_id=client_id,
            session_id=data.get("sessionId"),
            expired_time=data.get("expiredTime"),
        )
        log.info("Login successful, token cached")
        return ts

    async def _ensure_client_id(self) -> str:
        if self._client_id is not None:
            return self._client_id
        resp = await self._client.get(_MENUS_PATH)
        url = (resp.get("data") or {}).get("redirectLoginUrl", "")
        # extract clientId from URL query
        for part in url.split("?")[-1:]:
            for kv in part.split("&"):
                if kv.startswith("clientId="):
                    self._client_id = kv.split("=", 1)[1]
                    return self._client_id
        raise AuthError("could not extract clientId from getMenus response")
```

- [ ] **Step 5: 运行测试通过**

```bash
uv run pytest tests/unit/auth/test_token_manager.py -v
```
预期：全部 PASS

- [ ] **Step 6: 提交**

```bash
git add src/boc_mcp/auth tests/unit/auth
git commit -m "feat(auth): 3-step login TokenManager with caching and concurrency safety"
```

---

### Task 5：通用分页模型 (`models/common.py`)

**Files:**
- Create: `src/boc_mcp/models/__init__.py`
- Create: `src/boc_mcp/models/common.py`
- Create: `tests/unit/models/__init__.py`
- Create: `tests/unit/models/test_common.py`

- [ ] **Step 1: 写失败测试**

```python
from boc_mcp.models.common import ListResult


def test_list_result_from_legacy():
    payload = {"currPageNum": 1, "pageSize": 10, "totalCount": 25, "pageCount": 3, "rows": [{"id": 1}, {"id": 2}]}
    r = ListResult[dict].from_legacy(payload, items_key="rows")
    assert r.page == 1
    assert r.page_size == 10
    assert r.total == 25
    assert r.page_count == 3
    assert r.items == [{"id": 1}, {"id": 2}]


def test_list_result_from_state_envelope():
    payload = {"state": "success", "code": 200, "data": {"a": 1}, "message": "ok", "entity": None}
    r = ListResult[dict].from_legacy(payload, items_key="rows")
    assert r.items == []
    assert r.total == 0


def test_list_result_default():
    r = ListResult[dict](items=[{"x": 1}], page=1, page_size=20, total=1, page_count=1)
    assert r.total == 1
```

- [ ] **Step 2: 运行失败（ImportError）**
- [ ] **Step 3: 实现 `src/boc_mcp/models/common.py`**

```python
from __future__ import annotations

from typing import Any, Generic, TypeVar
from pydantic import BaseModel, Field

T = TypeVar("T")


class ListResult(BaseModel, Generic[T]):
    """Paginated list result, normalizes both legacy envelope shapes."""
    items: list[T] = Field(default_factory=list)
    page: int = 1
    page_size: int = 20
    total: int = 0
    page_count: int = 0

    @classmethod
    def from_legacy(cls, payload: dict[str, Any], *, items_key: str = "rows") -> "ListResult[Any]":
        data = payload.get("data")
        if isinstance(data, dict) and items_key in data:
            source = data
        else:
            source = payload
        return cls(
            items=source.get(items_key) or [],
            page=source.get("currPageNum", 1),
            page_size=source.get("pageSize", 20),
            total=source.get("totalCount", 0),
            page_count=source.get("pageCount", 0),
        )


class ActionResult(BaseModel):
    success: bool = True
    message: str = ""
```

- [ ] **Step 4: 测试通过，提交**

```bash
uv run pytest tests/unit/models/test_common.py -v
git add src/boc_mcp/models tests/unit/models
git commit -m "feat(models): add ListResult and ActionResult common models"
```

---

### Task 6：HTTP 客户端 (`client/boc_client.py`)

**Files:**
- Create: `src/boc_mcp/client/__init__.py`
- Create: `src/boc_mcp/client/boc_client.py`
- Create: `src/boc_mcp/client/pagination.py`
- Create: `tests/unit/client/test_boc_client.py`
- Create: `tests/unit/client/test_pagination.py`

- [ ] **Step 1: 写失败测试 — `tests/unit/client/test_boc_client.py`**

```python
import asyncio
import pytest
import aiohttp
from aioresponses import aioresponses
from boc_mcp.client.boc_client import BocHttpClient, BocApiClient
from boc_mcp.client.errors import (
    AuthError, BadRequestError, ForbiddenError, NotFoundError,
    ConflictError, ServerError, NetworkError, RequestTimeoutError,
)
from boc_mcp.auth.token_manager import TokenManager, TokenSet
from boc_mcp.auth.models import TokenSet as TS


class FakeTokenManager:
    def __init__(self, token="tok", refresh="ref"):
        self.token = token
        self.refresh = refresh
        self.calls = 0
        self.invalidations = 0
    async def get_token(self):
        self.calls += 1
        return TS(token=self.token, refresh_token=self.refresh, client_id="cid",
                  session_id="s", expired_time=None)
    def invalidate(self):
        self.invalidations += 1
    @property
    def system_id(self):
        return "1"


@pytest.fixture
def cfg():
    from boc_mcp.config import AppConfig
    return AppConfig(base_url="https://boc.test", username="u", password="p",
                     request_timeout=5, max_retries=2)


@pytest.mark.asyncio
async def test_get_injects_auth_headers(cfg):
    tm = FakeTokenManager()
    client = BocHttpClient(cfg, tm)
    with aioresponses() as m:
        m.get("https://boc.test/api/foo", payload={"state": "success", "data": {"x": 1}},
              headers={"Content-Type": "application/json"})
        async with client:
            resp = await client.get("/api/foo")
            # assert auth header was sent
            req_key = ("GET", "https://boc.test/api/foo")
            assert req_key in m.requests
            req_headers = m.requests[req_key][0].kwargs["headers"]
            assert req_headers["token"] == "tok"
            assert req_headers["refreshToken"] == "ref"
            assert req_headers["systemId"] == "1"
            assert resp == {"state": "success", "data": {"x": 1}}


@pytest.mark.asyncio
async def test_401_triggers_relogin_and_retry(cfg):
    tm = FakeTokenManager()
    client = BocHttpClient(cfg, tm)
    call_count = 0
    async def handler(url, **kwargs):
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            return aioresponses.CallbackResult(status=401,
                payload={"state": "error", "message": "token expired"})
        return aioresponses.CallbackResult(status=200,
            payload={"state": "success", "data": "ok"})
    with aioresponses() as m:
        m.get("https://boc.test/api/foo", callback=handler, repeat=True)
        async with client:
            resp = await client.get("/api/foo")
            assert resp == {"state": "success", "data": "ok"}
            assert call_count == 2
            assert tm.invalidations == 1
            assert tm.calls == 2


@pytest.mark.asyncio
async def test_401_only_retries_once(cfg):
    tm = FakeTokenManager()
    client = BocHttpClient(cfg, tm)
    with aioresponses() as m:
        m.get("https://boc.test/api/foo", status=401,
              payload={"state": "error", "message": "bad"}, repeat=True)
        async with client:
            with pytest.raises(AuthError):
                await client.get("/api/foo")


@pytest.mark.asyncio
@pytest.mark.parametrize("status,exc", [
    (400, BadRequestError),
    (403, ForbiddenError),
    (404, NotFoundError),
    (409, ConflictError),
    (500, ServerError),
])
async def test_http_errors_map_to_custom_exceptions(cfg, status, exc):
    tm = FakeTokenManager()
    client = BocHttpClient(cfg, tm)
    with aioresponses() as m:
        m.get(f"https://boc.test/api/x", status=status,
              payload={"message": f"err{status}"})
        async with client:
            with pytest.raises(exc):
                await client.get("/api/x")


@pytest.mark.asyncio
async def test_timeout_raises_timeout_error(cfg):
    tm = FakeTokenManager()
    client = BocHttpClient(cfg, tm)
    with aioresponses() as m:
        m.get("https://boc.test/api/x", exception=asyncio.TimeoutError())
        async with client:
            with pytest.raises(RequestTimeoutError):
                await client.get("/api/x")


@pytest.mark.asyncio
async def test_ssl_verify_can_be_disabled(cfg, monkeypatch):
    cfg.verify_ssl = False
    tm = FakeTokenManager()
    client = BocHttpClient(cfg, tm)
    # instantiate connector and verify ssl=False
    with aioresponses() as m:
        m.get("https://boc.test/api/foo", payload={"ok": True})
        async with client:
            resp = await client.get("/api/foo")
            assert resp == {"ok": True}
            # internal session connector has ssl=False
            assert client._session.connector._ssl is False


@pytest.mark.asyncio
async def test_base_url_path_joining(cfg):
    tm = FakeTokenManager()
    client = BocHttpClient(cfg, tm)
    with aioresponses() as m:
        m.get("https://boc.test/some/path", payload={"ok": True})
        async with client:
            r = await client.get("some/path")
            assert r == {"ok": True}
```

- [ ] **Step 2: 运行测试，确认失败**
- [ ] **Step 3: 实现 `src/boc_mcp/client/pagination.py`**

```python
from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Any, Callable


async def paginate(
    fetch_page: Callable[..., Any],
    *,
    page_param: str = "currPageNum",
    size_param: str = "pageSize",
    size: int = 20,
    items_key: str = "rows",
    **kwargs: Any,
) -> AsyncIterator[dict]:
    """Generic async generator that paginates a Boc-style list endpoint.

    fetch_page(page, page_size) -> dict with keys rows/totalCount/...
    """
    page = 1
    while True:
        body = dict(kwargs) if kwargs else {}
        body[page_param] = page
        body[size_param] = size
        resp = await fetch_page(**body)
        rows = resp.get(items_key) or resp.get("data", {}).get(items_key) or []
        for item in rows:
            yield item
        total = resp.get("totalCount", 0) or resp.get("data", {}).get("totalCount", 0)
        if page * size >= total or not rows:
            break
        page += 1
```

- [ ] **Step 4: 实现 `src/boc_mcp/client/boc_client.py`**

```python
from __future__ import annotations

import asyncio
import logging
from collections.abc import AsyncIterator
from typing import Any, Protocol, runtime_checkable

import aiohttp
from boc_mcp.auth.token_manager import TokenManager
from boc_mcp.client.errors import (
    APIError,
    AuthError,
    BadRequestError,
    ConflictError,
    ForbiddenError,
    NetworkError,
    NotFoundError,
    RequestTimeoutError,
    ServerError,
    is_token_invalid_message,
)
from boc_mcp.client.pagination import paginate
from boc_mcp.config import AppConfig

log = logging.getLogger(__name__)


@runtime_checkable
class BocApiClient(Protocol):
    async def request(self, method: str, path: str, *, params: dict | None = None,
                      json: Any = None) -> dict: ...
    async def get(self, path: str, *, params: dict | None = None) -> dict: ...
    async def post(self, path: str, *, json: Any = None) -> dict: ...
    async def put(self, path: str, *, json: Any = None) -> dict: ...
    async def delete(self, path: str) -> dict: ...
    def paginated_get(self, path: str, *, page_size: int = 20,
                      **kwargs: Any) -> AsyncIterator[dict]: ...


_STATUS_MAP: dict[int, type[APIError]] = {
    400: BadRequestError,
    401: AuthError,
    403: ForbiddenError,
    404: NotFoundError,
    409: ConflictError,
}


def _full_url(base_url: str, path: str) -> str:
    if path.startswith("http://") or path.startswith("https://"):
        return path
    sep = "" if base_url.endswith("/") or path.startswith("/") else "/"
    return f"{base_url}{sep}{path.lstrip('/')}"


class BocHttpClient:
    def __init__(self, config: AppConfig, token_manager: TokenManager) -> None:
        self._config = config
        self._token_manager = token_manager
        self._session: aiohttp.ClientSession | None = None

    async def __aenter__(self) -> "BocHttpClient":
        connector = aiohttp.TCPConnector(ssl=self._config.verify_ssl)
        timeout = aiohttp.ClientTimeout(total=self._config.request_timeout)
        self._session = aiohttp.ClientSession(connector=connector, timeout=timeout)
        return self

    async def __aexit__(self, *exc: Any) -> None:
        if self._session:
            await self._session.close()
            self._session = None

    async def _auth_headers(self) -> dict[str, str]:
        ts = await self._token_manager.get_token()
        return {
            "token": ts.token,
            "refreshToken": ts.refresh_token,
            "systemId": self._token_manager.system_id,
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    async def request(self, method: str, path: str, *, params: dict | None = None,
                      json: Any = None, _retried: bool = False) -> dict:
        if self._session is None:
            raise RuntimeError("BocHttpClient must be used as an async context manager")
        url = _full_url(self._config.base_url, path)
        headers = await self._auth_headers()
        log.debug("%s %s", method, url)
        try:
            async with self._session.request(method, url, params=params, json=json,
                                             headers=headers) as resp:
                status = resp.status
                try:
                    body = await resp.json(content_type=None)
                except Exception:
                    body = {"raw": await resp.text()}
                if status == 401 and not _retried:
                    msg = body.get("message", "") if isinstance(body, dict) else ""
                    if is_token_invalid_message(msg) or status == 401:
                        log.info("Token invalid, re-logging in")
                        self._token_manager.invalidate()
                        return await self.request(method, path, params=params, json=json,
                                                  _retried=True)
                if status >= 400:
                    self._raise_api_error(status, body)
                return body if isinstance(body, dict) else {"data": body}
        except asyncio.TimeoutError as e:
            raise RequestTimeoutError(f"request timed out: {method} {path}") from e
        except aiohttp.ClientError as e:
            raise NetworkError(f"network error: {e}") from e

    def _raise_api_error(self, status: int, body: Any) -> None:
        msg = "API error"
        code = None
        if isinstance(body, dict):
            msg = body.get("message") or body.get("msg") or msg
            code = body.get("code")
        exc_cls = _STATUS_MAP.get(status)
        if exc_cls is None:
            if status >= 500:
                exc_cls = ServerError
            else:
                exc_cls = APIError
        raise exc_cls(msg, status_code=status, code=str(code) if code is not None else None,
                      body=body)

    async def get(self, path: str, *, params: dict | None = None) -> dict:
        return await self.request("GET", path, params=params)

    async def post(self, path: str, *, json: Any = None) -> dict:
        return await self.request("POST", path, json=json)

    async def put(self, path: str, *, json: Any = None) -> dict:
        return await self.request("PUT", path, json=json)

    async def delete(self, path: str) -> dict:
        return await self.request("DELETE", path)

    async def paginated_get(self, path: str, *, page_size: int = 20,
                            **kwargs: Any) -> AsyncIterator[dict]:
        size = max(1, min(page_size, 100))
        async def fetch(**kw: Any) -> dict:
            return await self.post(path, json=kw) if path.startswith("/query") or path.startswith("/service") else await self.get(path, params=kw)
        async for item in paginate(fetch, size=size, **kwargs):
            yield item
```

- [ ] **Step 5: 补充分页测试 `tests/unit/client/test_pagination.py`**

```python
import pytest
from boc_mcp.client.pagination import paginate


@pytest.mark.asyncio
async def test_paginate_yields_all_items():
    pages = [
        {"rows": [{"id": 1}, {"id": 2}], "totalCount": 5, "currPageNum": 1, "pageSize": 2},
        {"rows": [{"id": 3}, {"id": 4}], "totalCount": 5, "currPageNum": 2, "pageSize": 2},
        {"rows": [{"id": 5}], "totalCount": 5, "currPageNum": 3, "pageSize": 2},
    ]
    idx = 0
    async def fetch(**kw):
        nonlocal idx
        assert kw["currPageNum"] == idx + 1
        p = pages[idx]
        idx += 1
        return p
    items = [i async for i in paginate(fetch, size=2)]
    assert [i["id"] for i in items] == [1, 2, 3, 4, 5]


@pytest.mark.asyncio
async def test_paginate_handles_empty():
    async def fetch(**kw):
        return {"rows": [], "totalCount": 0}
    items = [i async for i in paginate(fetch)]
    assert items == []
```

- [ ] **Step 6: 运行全部 client 测试通过**

```bash
uv run pytest tests/unit/client/ -v
```
预期：全部 PASS

- [ ] **Step 7: 提交**

```bash
git add src/boc_mcp/client tests/unit/client
git commit -m "feat(client): BocHttpClient with auth injection, 401 retry, error mapping, pagination"
```

---

### Task 7：结构化日志 (`logging_setup.py`)

**Files:**
- Create: `src/boc_mcp/logging_setup.py`
- Create: `tests/unit/test_logging.py`

- [ ] **Step 1: 写测试 `tests/unit/test_logging.py`**

```python
import logging
import json
from boc_mcp.logging_setup import setup_logging, _SensitiveFilter


def test_setup_logging_produces_json_in_prod(capsys, monkeypatch):
    monkeypatch.delenv("BOC_DEV", raising=False)
    setup_logging(level="INFO")
    logger = logging.getLogger("boc_mcp.test")
    logger.info("hello", extra={"path": "/x", "status": 200})
    out = capsys.readouterr().err
    line = [l for l in out.splitlines() if "hello" in l][0]
    rec = json.loads(line)
    assert rec["message"] == "hello"
    assert rec["level"] == "INFO"
    assert rec["path"] == "/x"
    assert rec["status"] == 200


def test_sensitive_filter_masks_password():
    f = _SensitiveFilter()
    rec = logging.LogRecord("x", logging.INFO, "", 0, "password=secret123 token=abc", (), None)
    f.filter(rec)
    assert "secret123" not in rec.getMessage()
    assert "abc" not in rec.getMessage()
    assert "***" in rec.getMessage()
```

- [ ] **Step 2: 运行失败（ImportError）**
- [ ] **Step 3: 实现 `src/boc_mcp/logging_setup.py`**

```python
from __future__ import annotations

import json
import logging
import os
import sys
from typing import Any

_SENSITIVE_KEYS = ("password", "token", "refreshToken", "authorization", "secret")


class _JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": self.formatTime(record, "%Y-%m-%dT%H:%M:%S%z"),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        for k, v in record.__dict__.items():
            if k not in ("args", "asctime", "created", "exc_info", "exc_text", "filename",
                         "funcName", "levelname", "levelno", "lineno", "module", "msecs",
                         "message", "msg", "name", "pathname", "process", "processName",
                         "relativeCreated", "stack_info", "thread", "threadName"):
                payload[k] = v
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=False, default=str)


class _SensitiveFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        try:
            msg = record.getMessage()
        except Exception:
            return True
        for key in _SENSITIVE_KEYS:
            idx = msg.lower().find(key.lower())
            if idx >= 0:
                # Mask anything after "key=" or "key":" until delimiter
                msg = msg[:idx] + key + "=***"
        record.msg = msg
        record.args = ()
        return True


def setup_logging(level: str = "INFO") -> None:
    is_dev = os.environ.get("BOC_DEV") == "1" or os.environ.get("DEV") == "1"
    handler = logging.StreamHandler(sys.stderr)
    if is_dev:
        handler.setFormatter(logging.Formatter(
            "%(asctime)s %(levelname)s %(name)s: %(message)s"))
    else:
        handler.setFormatter(_JsonFormatter())
    handler.addFilter(_SensitiveFilter())
    root = logging.getLogger("boc_mcp")
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(getattr(logging, level.upper(), logging.INFO))
    root.propagate = False
```

- [ ] **Step 4: 运行测试通过**

```bash
uv run pytest tests/unit/test_logging.py -v
```

- [ ] **Step 5: 提交**

```bash
git add src/boc_mcp/logging_setup.py tests/unit/test_logging.py
git commit -m "feat(logging): structured JSON logging with sensitive data masking"
```

---

### Task 8：统一错误处理 middleware (`middleware.py`)

**Files:**
- Create: `src/boc_mcp/middleware.py`
- Create: `tests/unit/test_middleware.py`

- [ ] **Step 1: 写测试 `tests/unit/test_middleware.py`**

```python
import pytest
from mcp.types import ErrorData
from mcp.shared.exceptions import McpError
from boc_mcp.client.errors import (
    BadRequestError, NotFoundError, ForbiddenError, AuthError,
    ConflictError, ServerError, NetworkError, RequestTimeoutError, APIError,
)
from boc_mcp.middleware import boc_error_to_mcp, INVALID_PARAMS, NOT_FOUND, PERMISSION_DENIED, INTERNAL_ERROR, UNAUTHORIZED


@pytest.mark.parametrize("exc,code", [
    (BadRequestError("bad"), INVALID_PARAMS),
    (NotFoundError("miss"), NOT_FOUND),
    (ForbiddenError("no"), PERMISSION_DENIED),
    (AuthError("expired"), UNAUTHORIZED),
    (ConflictError("dup"), INVALID_PARAMS),
    (ServerError("boom"), INTERNAL_ERROR),
    (NetworkError("net"), INTERNAL_ERROR),
    (RequestTimeoutError("to"), INTERNAL_ERROR),
])
def test_error_mapping(exc, code):
    err = boc_error_to_mcp(exc)
    assert isinstance(err, McpError)
    assert isinstance(err.error, ErrorData)
    assert err.error.code == code
    assert exc.message in err.error.message


def test_non_boc_error_wrapped_as_internal():
    err = boc_error_to_mcp(ValueError("unexpected"))
    assert err.error.code == INTERNAL_ERROR
```

- [ ] **Step 2: 实现 `src/boc_mcp/middleware.py`**

```python
from __future__ import annotations

from mcp.shared.exceptions import McpError
from mcp.types import ErrorData, INVALID_PARAMS, INTERNAL_ERROR, METHOD_NOT_FOUND

from boc_mcp.client.errors import (
    APIError,
    AuthError,
    BadRequestError,
    BocMcpError,
    ConflictError,
    ForbiddenError,
    NetworkError,
    NotFoundError,
    RequestTimeoutError,
    ServerError,
)

# MCP JSON-RPC error codes (reuse standard JSON-RPC; MCP SDK defines these).
INVALID_REQUEST = -32600
NOT_FOUND = -32001
PERMISSION_DENIED = -32002
UNAUTHORIZED = -32003
UNAVAILABLE = -32004


def boc_error_to_mcp(err: Exception) -> McpError:
    if isinstance(err, BadRequestError) or isinstance(err, ConflictError):
        code = INVALID_PARAMS
    elif isinstance(err, NotFoundError):
        code = NOT_FOUND
    elif isinstance(err, ForbiddenError):
        code = PERMISSION_DENIED
    elif isinstance(err, AuthError):
        code = UNAUTHORIZED
    elif isinstance(err, ServerError) or isinstance(err, NetworkError) or isinstance(err, RequestTimeoutError):
        code = INTERNAL_ERROR
    elif isinstance(err, BocMcpError):
        code = INTERNAL_ERROR
    else:
        code = INTERNAL_ERROR
    message = getattr(err, "message", str(err)) or str(err)
    return McpError(ErrorData(code=code, message=message))


def wrap_tool_errors(fn):
    """Decorator for tool functions that converts BocMcpError -> McpError and re-raises."""
    import functools
    @functools.wraps(fn)
    async def wrapper(*args, **kwargs):
        try:
            return await fn(*args, **kwargs)
        except McpError:
            raise
        except Exception as e:
            raise boc_error_to_mcp(e) from e
    return wrapper
```

- [ ] **Step 3: 测试通过、提交**

```bash
uv run pytest tests/unit/test_middleware.py -v
git add src/boc_mcp/middleware.py tests/unit/test_middleware.py
git commit -m "feat(middleware): BocMcpError to McpError mapping and tool decorator"
```

---

### Task 9：BaseService (`services/base.py`)

**Files:**
- Create: `src/boc_mcp/services/__init__.py`
- Create: `src/boc_mcp/services/base.py`
- Create: `tests/unit/services/__init__.py`
- Create: `tests/unit/services/base/__init__.py`
- Create: `tests/unit/services/base/test_base_service.py`

- [ ] **Step 1: 写测试**

```python
import pytest
from boc_mcp.services.base import BaseService


class FakeClient:
    def __init__(self):
        self.calls = []
    async def get(self, path, *, params=None):
        self.calls.append(("get", path, params))
        return {"ok": True, "path": path}
    async def post(self, path, *, json=None):
        self.calls.append(("post", path, json))
        return {"ok": True, "path": path}
    async def put(self, path, *, json=None):
        self.calls.append(("put", path, json))
        return {"ok": True}
    async def delete(self, path):
        self.calls.append(("delete", path))
        return {"ok": True}


def make_svc():
    c = FakeClient()
    return BaseService(c), c


@pytest.mark.asyncio
async def test_get_delegates_to_client():
    svc, c = make_svc()
    r = await svc._get("/foo", params={"a": 1})
    assert c.calls[-1] == ("get", "/foo", {"a": 1})
    assert r["ok"] is True


@pytest.mark.asyncio
async def test_post_put_delete_delegate():
    svc, c = make_svc()
    await svc._post("/x", json={"b": 2})
    await svc._put("/y", json={"c": 3})
    await svc._delete("/z")
    assert [m for m, _, _ in c.calls] == ["post", "put", "delete"]


@pytest.mark.asyncio
async def test_list_returns_paginated_items():
    page = 0
    async def fake_post(path, *, json=None):
        nonlocal page
        page += 1
        if page == 1:
            return {"rows": [{"id": 1}, {"id": 2}], "totalCount": 3, "currPageNum": 1, "pageSize": 2}
        return {"rows": [{"id": 3}], "totalCount": 3, "currPageNum": 2, "pageSize": 2}
    c = FakeClient()
    c.post = fake_post
    svc = BaseService(c)
    items = []
    async for item in svc._list("/list", page_size=2):
        items.append(item)
    assert [i["id"] for i in items] == [1, 2, 3]
```

- [ ] **Step 2: 实现 `src/boc_mcp/services/base.py`**

```python
from __future__ import annotations

from typing import Any
from collections.abc import AsyncIterator
from boc_mcp.client.boc_client import BocApiClient
from boc_mcp.client.pagination import paginate


class BaseService:
    """Base class for domain services."""

    def __init__(self, client: BocApiClient) -> None:
        self._client = client

    async def _get(self, path: str, *, params: dict | None = None) -> dict:
        return await self._client.get(path, params=params)

    async def _post(self, path: str, *, json: dict | None = None) -> dict:
        return await self._client.post(path, json=json)

    async def _put(self, path: str, *, json: dict | None = None) -> dict:
        return await self._client.put(path, json=json)

    async def _delete(self, path: str) -> dict:
        return await self._client.delete(path)

    async def _list(self, path: str, *, page_size: int = 20, **kwargs: Any) -> AsyncIterator[dict]:
        async def fetch(**kw: Any) -> dict:
            return await self._client.post(path, json=kw)
        async for item in paginate(fetch, size=page_size, **kwargs):
            yield item
```

- [ ] **Step 3: 测试通过 + 提交**

```bash
uv run pytest tests/unit/services/base/ -v
git add src/boc_mcp/services/base.py src/boc_mcp/services/__init__.py tests/unit/services/
git commit -m "feat(services): BaseService with common HTTP helpers and pagination"
```

---

### Task 10：Health 端点 (`health.py`)

**Files:**
- Create: `src/boc_mcp/health.py`
- Create: `tests/unit/test_health.py`

- [ ] **Step 1: 写测试**

```python
import pytest
from starlette.testclient import TestClient
from starlette.applications import Starlette
from starlette.routing import Route
from boc_mcp.health import liveness, readiness


def make_app(client=None):
    app = Starlette(routes=[
        Route("/healthz", liveness),
        Route("/healthz/ready", readiness),
    ])
    app.state.boc_client = client
    return app


def test_liveness():
    with TestClient(make_app()) as c:
        r = c.get("/healthz")
        assert r.status_code == 200
        assert r.json() == {"status": "ok"}


class OkClient:
    async def get(self, path, *, params=None):
        return {"state": "success", "data": {"name": "u"}}


class FailClient:
    async def get(self, path, *, params=None):
        raise RuntimeError("down")


def test_readiness_ok():
    with TestClient(make_app(OkClient())) as c:
        r = c.get("/healthz/ready")
        assert r.status_code == 200
        assert r.json()["status"] == "ready"


def test_readiness_fail_when_api_down():
    with TestClient(make_app(FailClient())) as c:
        r = c.get("/healthz/ready")
        assert r.status_code == 503
        assert r.json()["status"] == "not_ready"
```

- [ ] **Step 2: 实现 `src/boc_mcp/health.py`**

```python
from __future__ import annotations

from starlette.responses import JSONResponse
from starlette.requests import Request


async def liveness(request: Request) -> JSONResponse:
    return JSONResponse({"status": "ok"}, status_code=200)


async def readiness(request: Request) -> JSONResponse:
    client = getattr(request.app.state, "boc_client", None)
    if client is None:
        return JSONResponse({"status": "ready"}, status_code=200)
    try:
        await client.get("/upmstreeapi/bocPortal/getMenus")
        return JSONResponse({"status": "ready"}, status_code=200)
    except Exception as e:
        return JSONResponse({"status": "not_ready", "error": str(e)}, status_code=503)
```

- [ ] **Step 3: 测试通过 + 提交**

```bash
uv run pytest tests/unit/test_health.py -v
git add src/boc_mcp/health.py tests/unit/test_health.py
git commit -m "feat(health): /healthz liveness and /healthz/ready readiness endpoints"
```

---

### Task 11：Server 入口与工具注册框架 (`server.py`)

**Files:**
- Create: `src/boc_mcp/server.py`
- Create: `tests/unit/test_server.py`
- Create: `scripts/dev_server.py`

- [ ] **Step 1: 写测试**

```python
import pytest
from boc_mcp.server import create_app, MCP_INSTRUCTIONS
from boc_mcp.config import AppConfig


def make_cfg(**overrides):
    return AppConfig(base_url="https://boc.test", username="u", password="p", **overrides)


def test_create_app_returns_fastmcp():
    from mcp.server.fastmcp import FastMCP
    app = create_app(make_cfg())
    assert isinstance(app, FastMCP)


def test_all_tools_registered():
    app = create_app(make_cfg())
    tools = app._tool_manager._tools  # internal registry
    names = sorted(tools.keys())
    # At least auth tools must be present (infrastructure stage)
    assert "boc_auth_get_client_id" in names
    assert "boc_auth_login" in names
    assert "boc_auth_get_token" in names


def test_instructions_present():
    app = create_app(make_cfg())
    assert "博云" in (app.instructions or "")
```

- [ ] **Step 2: 先创建 auth service + tools（占位，详细实现在 Task 12），然后写 server 框架**

先创建 `src/boc_mcp/services/auth/models.py`、`service.py`、`tools.py`、`__init__.py` 空骨架（Task 12 填充）。

- [ ] **Step 3: 实现 `src/boc_mcp/server.py`**

```python
from __future__ import annotations

from typing import Any
from mcp.server.fastmcp import FastMCP
from starlette.routing import Mount, Route

from boc_mcp.auth.token_manager import TokenManager
from boc_mcp.client.boc_client import BocHttpClient
from boc_mcp.config import AppConfig, load_config
from boc_mcp.health import liveness, readiness
from boc_mcp.logging_setup import setup_logging
from boc_mcp.middleware import wrap_tool_errors
from boc_mcp.services.auth import register_tools as reg_auth

MCP_INSTRUCTIONS = """你是博云 BeyondContainer 容器云平台的运维助手。
你可以通过以 boc_ 开头的工具查询平台资源（集群、节点、工作负载、容器、监控、版本镜像等）。
本 MCP 目前只提供查询能力。所有列表类工具有 page/page_size 参数，page_size 最大 100。
关键概念：cluster_id（集群 id）、env_id（租户/环境 id）、project_id（应用 id）、
applicationId（服务/版本 id）、namespace（命名空间）是常见筛选条件。
"""

# All domain registries — populated as service modules are implemented.
_REGISTRIES: list[Any] = [
    reg_auth,
    # Future: reg_service_tree, reg_application, reg_cluster, reg_partition, ...
]


def create_app(config: AppConfig | None = None) -> FastMCP:
    config = config or load_config()
    setup_logging(config.log_level)

    mcp = FastMCP("boc-mcp", instructions=MCP_INSTRUCTIONS)

    # Wire HTTP client and token manager
    http_client = BocHttpClient(config, None)  # token manager added after construction
    token_mgr = TokenManager(config, http_client)
    http_client._token_manager = token_mgr  # circular resolved

    mcp.state.config = config
    mcp.state.token_manager = token_mgr
    mcp.state.boc_client = http_client

    # Health routes mounted on underlying starlette app
    # FastMCP exposes a `streamable_http_app()` Starlette app; we add routes to it
    # via custom ASGI wrapper.
    from starlette.applications import Starlette
    from starlette.routing import Route as R

    mcp_app = mcp.streamable_http_app()
    health_app = Starlette(routes=[
        R("/healthz", liveness),
        R("/healthz/ready", readiness),
    ])
    health_app.state.boc_client = http_client

    async def dispatch(scope, receive, send):
        if scope["type"] == "http":
            path = scope.get("path", "/")
            if path.startswith("/healthz"):
                await health_app(scope, receive, send)
                return
        await mcp_app(scope, receive, send)

    mcp._http_dispatch = dispatch  # for manual usage

    for reg in _REGISTRIES:
        reg(mcp, http_client)

    return mcp


def run() -> None:
    config = load_config()
    app = create_app(config)
    # Use custom ASGI app with health endpoints
    import uvicorn
    uvicorn.run(app._http_dispatch, host=config.mcp.host, port=config.mcp.port)


if __name__ == "__main__":
    run()
```

- [ ] **Step 4: 实现 `scripts/dev_server.py`**

```python
#!/usr/bin/env python
"""Local dev entry: reloads when src changes."""
import asyncio
from boc_mcp.server import run

if __name__ == "__main__":
    run()
```

- [ ] **Step 5: 先为 auth 建空壳：**

`src/boc_mcp/services/auth/__init__.py`:
```python
from boc_mcp.services.auth.tools import register_tools
__all__ = ["register_tools"]
```

`src/boc_mcp/services/auth/models.py`:
```python
from pydantic import BaseModel

class ClientIdResult(BaseModel):
    client_id: str

class LoginResult(BaseModel):
    code: str
    user_id: int | None = None
    user_name: str

class AccessTokenResult(BaseModel):
    token: str
    refresh_token: str
    expired_time: str | None = None
    session_id: str | None = None
```

`src/boc_mcp/services/auth/service.py`:
```python
from __future__ import annotations
from urllib.parse import urlparse, parse_qs
from boc_mcp.services.base import BaseService
from boc_mcp.services.auth.models import ClientIdResult, LoginResult, AccessTokenResult

class AuthService(BaseService):
    async def get_client_id(self) -> ClientIdResult:
        resp = await self._get("/upmstreeapi/bocPortal/getMenus")
        url = (resp.get("data") or {}).get("redirectLoginUrl", "")
        qs = parse_qs(urlparse(url).query)
        cid = qs.get("clientId", [None])[0]
        if not cid:
            raise ValueError("no clientId in response")
        return ClientIdResult(client_id=cid)

    async def login(self, client_id: str) -> LoginResult:
        from boc_mcp.config import AppConfig
        # We need username/password; receive from caller or config? Config via closure.
        raise NotImplementedError

    async def get_token(self, code: str) -> AccessTokenResult:
        raise NotImplementedError
```

`src/boc_mcp/services/auth/tools.py`:
```python
from __future__ import annotations
from boc_mcp.client.boc_client import BocApiClient

def register_tools(mcp, client: BocApiClient) -> None:
    @mcp.tool(description="获取登录所需的 clientId（调试用）")
    async def boc_auth_get_client_id() -> str:
        from boc_mcp.services.auth.service import AuthService
        svc = AuthService(client)
        r = await svc.get_client_id()
        return r.model_dump_json()

    @mcp.tool(description="登录，返回 code（调试用）")
    async def boc_auth_login(client_id: str) -> str:
        return "ok"

    @mcp.tool(description="用 code 换 token（调试用）")
    async def boc_auth_get_token(code: str) -> str:
        return "ok"
```

- [ ] **Step 6: 跑测试，确认 create_app 基本通过，提交**

```bash
uv run pytest tests/unit/test_server.py -v
git add src/boc_mcp/server.py scripts/dev_server.py tests/unit/test_server.py src/boc_mcp/services/auth/
git commit -m "feat(server): FastMCP app factory with health routes and tool registry"
```

---

### Task 12：重构 auth 模块 — 真实 3 步登录工具

**File:**
- Modify: `src/boc_mcp/services/auth/service.py`
- Modify: `src/boc_mcp/services/auth/tools.py`
- Create: `tests/unit/services/auth/__init__.py`
- Create: `tests/unit/services/auth/test_service.py`
- Create: `tests/unit/services/auth/test_tools.py`

auth service 不重复实现登录；它薄封装 TokenManager，提供 token 状态查询和强制重登能力。

- [ ] **Step 1: 重写测试 `tests/unit/services/auth/test_service.py`**

```python
import pytest
from boc_mcp.auth.token_manager import TokenManager, TokenSet
from boc_mcp.auth.models import TokenSet as TS
from boc_mcp.services.auth.service import AuthService

class FakeClient:
    async def get(self, path, *, params=None):
        if path.startswith("/upmstreeapi/bocPortal/getMenus"):
            return {"data": {"redirectLoginUrl": "http://x/?clientId=cid"}}
        if path.startswith("/upmstreeapi/accessToken"):
            return {"state": "success", "data": {"token": "t", "refreshToken": "r",
                    "expiredTime": "2026-01-01", "sessionId": "s"}}
        return {}
    async def post(self, path, *, json=None):
        if path == "/upmstreeapi/login":
            return {"state": "success", "data": {"code": "codex", "name": json["userName"]}}
        return {}

@pytest.mark.asyncio
async def test_auth_service_refresh_forces_relogin(cfg):
    from boc_mcp.config import AppConfig
    cfg = AppConfig(base_url="https://boc.test", username="u", password="p")
    tm = TokenManager(cfg, FakeClient())
    svc = AuthService(tm)
    ts1 = await svc.current_token()
    assert ts1.token == "t"
    await svc.refresh()
    ts2 = await svc.current_token()
    assert ts2.token == "t"

@pytest.mark.asyncio
async def test_auth_service_status():
    from boc_mcp.config import AppConfig
    cfg = AppConfig(base_url="https://boc.test", username="u", password="p")
    tm = TokenManager(cfg, FakeClient())
    svc = AuthService(tm)
    st = await svc.status()
    assert st.logged_in is True
    assert st.username == "u"
```

- [ ] **Step 2: 重写 `src/boc_mcp/services/auth/service.py`**

```python
from __future__ import annotations
from pydantic import BaseModel
from boc_mcp.auth.token_manager import TokenManager

class AuthStatus(BaseModel):
    logged_in: bool
    username: str
    system_id: str
    expired_time: str | None = None

class AuthService:
    def __init__(self, token_manager: TokenManager) -> None:
        self._tm = token_manager

    async def current_token(self):
        return await self._tm.get_token()

    async def refresh(self) -> None:
        self._tm.invalidate()
        await self._tm.get_token()

    async def status(self) -> AuthStatus:
        ts = await self._tm.get_token()
        return AuthStatus(
            logged_in=True,
            username=self._tm._config.username,
            system_id=self._tm.system_id,
            expired_time=ts.expired_time,
        )
```

- [ ] **Step 3: 重写 `src/boc_mcp/services/auth/tools.py`**

```python
from __future__ import annotations
from boc_mcp.auth.token_manager import TokenManager
from boc_mcp.client.boc_client import BocApiClient
from boc_mcp.services.auth.service import AuthService

def register_tools(mcp, client: BocApiClient, token_manager: TokenManager | None = None) -> None:
    svc = AuthService(token_manager) if token_manager else None

    @mcp.tool(description="查询当前登录状态：是否已登录、登录用户、systemId、token 过期时间。")
    async def boc_auth_status() -> dict:
        if svc is None:
            return {"logged_in": False}
        st = await svc.status()
        return st.model_dump()

    @mcp.tool(description="强制重新登录博云平台（当 token 异常时使用）。")
    async def boc_auth_refresh() -> str:
        if svc is None:
            return "no token manager configured"
        await svc.refresh()
        return "relogin successful"
```

- [ ] **Step 4: 更新 `server.py` 将 token_manager 传入 reg_auth**

修改 `server.py` 中调用 `reg_auth(mcp, http_client, token_mgr)`。

- [ ] **Step 5: 测试通过并提交**

```bash
uv run pytest tests/unit/services/auth/ tests/unit/test_server.py -v
git add src/boc_mcp/services/auth src/boc_mcp/server.py tests/unit/services/auth
git commit -m "refactor(auth): AuthService wraps TokenManager with status/refresh tools"
```

---


