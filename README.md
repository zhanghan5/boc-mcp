# boc-mcp

博云 BeyondContainer 容器云平台的 MCP (Model Context Protocol) Server，让大语言模型可以通过统一的工具接口查询容器云平台的集群、节点、分区、工作负载、镜像版本、监控、安全扫描等资源。

## 特性

- **全能力查询覆盖**：共 58 个工具，覆盖集群、节点、分区、应用/服务/任务、Pod、容器、Service、Secret、网络、服务树、监控、镜像版本、安全扫描 11 个领域。
- **Streamable HTTP 传输**：默认监听 `0.0.0.0:8000`，支持任意 MCP 客户端（Claude Desktop、Codex CLI、Cursor 等）通过 HTTP 接入。
- **自动登录 + Token 缓存**：启动后自动完成博云三步登录流程（取 clientId → 换取 code → 换 token），Token 缓存在内存中；遇到 401 或平台返回 token 失效消息时自动重新登录并重试一次。
- **HTTP 请求适配器**：`BocHttpClient` 封装 aiohttp，统一注入 `token`/`refreshToken`/`systemId` Header、错误映射、超时、重试；通过 `BocApiClient` Protocol 解耦，单元测试使用 Fake 客户端零网络开销。
- **Pydantic 模型 + 蛇形/驼峰兼容**：所有领域模型自动驼峰别名，可直接反序列化博云接口返回。
- **结构化日志**：JSON 生产模式，开发模式彩色输出，自动脱敏密码/Token。
- **健康检查**：`/healthz`（存活）和 `/healthz/ready`（就绪）端点，就绪检查会验证 Token 是否可用。
- **TDD 严格保证**：测试覆盖率阈值 80%，所有工具注册、参数、描述均有测试兜底。

## 快速开始

### 1. 安装依赖

项目使用 Python ≥ 3.12，推荐使用 `uv` 或 `pip`：

```bash
# 用 uv（推荐）
uv venv && uv pip install -e ".[dev]"

# 或用 pip
python -m venv .venv
.venv\Scripts\activate      # Windows
# source .venv/bin/activate # Linux/macOS
pip install -e ".[dev]"
```

### 2. 配置

支持两种配置方式，**环境变量优先级高于 YAML 文件**：

- 环境变量（推荐生产使用）：`BOC_BASE_URL`、`BOC_USERNAME`、`BOC_PASSWORD` 等；
- YAML 配置文件：自动查找 `./config.yaml`、`~/.boc-mcp/config.yaml`，或通过 `BOC_CONFIG_FILE` 指定。

最小配置（环境变量）：

```bash
export BOC_BASE_URL="https://your-boc-platform.com"
export BOC_USERNAME="admin"
export BOC_PASSWORD="your-password"
# 可选
export BOC_SYSTEM_ID="1"
export BOC_VERIFY_SSL="true"
export BOC_MCP__PORT="8000"
```

或使用 YAML：复制 `config/config.example.yaml` 为 `config.yaml` 并修改。

所有配置项：

| 环境变量 | YAML 键 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `BOC_BASE_URL` | `base_url` | —（必填） | 博云平台根地址，不要带尾斜杠 |
| `BOC_USERNAME` | `username` | —（必填） | 登录用户名 |
| `BOC_PASSWORD` | `password` | —（必填） | 登录密码 |
| `BOC_SYSTEM_ID` | `system_id` | `"1"` | 业务系统 ID，默认 1 |
| `BOC_VERIFY_SSL` | `verify_ssl` | `true` | 是否校验 HTTPS 证书 |
| `BOC_REQUEST_TIMEOUT` | `request_timeout` | `30` | 单次 HTTP 请求超时（秒） |
| `BOC_MAX_RETRIES` | `max_retries` | `3` | 网络错误重试次数 |
| `BOC_LOG_LEVEL` | `log_level` | `"INFO"` | 日志级别（DEBUG/INFO/WARNING/ERROR） |
| `BOC_CONFIG_FILE` | — | — | 指定 YAML 配置文件路径 |
| `BOC_MCP__HOST` | `mcp.host` | `"0.0.0.0"` | MCP HTTP 监听地址 |
| `BOC_MCP__PORT` | `mcp.port` | `8000` | MCP HTTP 监听端口 |

### 3. 启动服务

```bash
python -m boc_mcp
# 或开发模式（彩色日志）
$env:BOC_DEV=1; python -m boc_mcp   # PowerShell
# BOC_DEV=1 python -m boc_mcp       # bash
```

服务启动后会：
1. 加载配置 → 2. 初始化日志 → 3. 登录博云平台获取 Token → 4. 监听 `http://0.0.0.0:8000/mcp`。

健康检查：`GET http://localhost:8000/healthz`（存活）、`GET http://localhost:8000/healthz/ready`（就绪，含 Token 检查）。

### 4. 接入 MCP 客户端

**Claude Desktop / Codex CLI** 配置示例（添加到各自的 MCP 配置文件）：

```json
{
  "mcpServers": {
    "boc-mcp": {
      "url": "http://localhost:8000/mcp",
      "env": {
        "BOC_BASE_URL": "https://your-boc-platform.com",
        "BOC_USERNAME": "admin",
        "BOC_PASSWORD": "your-password"
      }
    }
  }
}
```

若需要 stdio 模式，可使用命令方式：

```json
{
  "mcpServers": {
    "boc-mcp": {
      "command": "python",
      "args": ["-m", "boc_mcp"],
      "env": {
        "BOC_BASE_URL": "https://your-boc-platform.com",
        "BOC_USERNAME": "admin",
        "BOC_PASSWORD": "your-password"
      }
    }
  }
}
```

## 工具列表（58 个，全部只读）

所有工具以 `boc_` 开头。列表类工具统一支持 `page`/`page_size`（最大 100）分页参数。

### 认证（auth）
- `boc_auth_status` — 查询登录状态、当前用户、Token 过期时间
- `boc_auth_refresh` — 强制重新登录博云平台

### 应用（application）
- `boc_app_get` — 按应用 ID 查询应用详情
- `boc_app_list` — 分页查询应用列表，可按集群/名称过滤

### 集群（cluster）
- `boc_cluster_list` — 集群列表（分页，关键字过滤）
- `boc_cluster_all` — 所有集群（不分页，简表）
- `boc_cluster_base_info` — 集群基本信息（类型/名称/版本过滤）
- `boc_cluster_monitor` — 指定集群监控信息
- `boc_cluster_state` — 指定集群运行状态
- `boc_cluster_nodes` — 集群下节点列表
- `boc_cluster_partitions` — 集群下分区列表
- `boc_cluster_partition_resource` — 指定 hostId 分区 CPU/内存资源使用
- `boc_cluster_by_env` — 指定租户下集群列表
- `boc_cluster_available_partitions` — 当前租户可用分区

### 服务树（service_tree）
- `boc_service_tree` — 服务树节点查询（支持父类型/父 ID/节点类型筛选）

### 安全扫描（scan）
- `boc_scan_list_strategies` — 安全扫描策略列表
- `boc_scan_get_report` — 扫描报告详情
- `boc_scan_list_reports` — 扫描报告列表

### 配置/密钥（config_secret）
- `boc_secret_list` — 指定集群/命名空间下 Secret 列表

### 网络（network）
- `boc_network_list_by_name` — 按名称/IP 查询网络分区
- `boc_network_available` — 可用（未分配）网络列表
- `boc_network_by_env` — 按租户查询网络列表

### 分区（partition）
- `boc_partition_list` — 分页查询分区列表
- `boc_partition_get_default` — 集群默认分区
- `boc_partition_get_meta` — 按条件查询分区元数据
- `boc_partition_list_default` — 默认分区列表（不分页）
- `boc_partition_list_nodes` — 分区节点列表
- `boc_partition_list_all_hosts` — 所有主机节点列表
- `boc_partition_all_info` — 主机全量信息（集群/租户/IP/名称过滤）
- `boc_partition_detail` — 分区详情
- `boc_partition_list_available` — 当前租户可用分区

### 监控（monitor）
- `boc_monitor_get_project_status` — 单个应用实时监控状态
- `boc_monitor_batch_project` — 批量项目监控数据
- `boc_monitor_batch_project_status` — 批量项目状态监控
- `boc_monitor_get_app` — 单个服务监控数据
- `boc_monitor_batch_app` — 批量应用监控数据
- `boc_monitor_get_pod` — Pod 监控数据
- `boc_monitor_batch_container` — 批量容器监控数据
- `boc_monitor_batch_pod` — 批量 Pod 监控数据

### 版本/镜像（version）
- `boc_version_list` — 版本列表
- `boc_version_get_id_by_name` — 按名称查版本 ID
- `boc_version_list_image_groups` — 版本镜像组列表
- `boc_version_list_dispatched_clusters` — 版本已发布集群列表
- `boc_version_list_undispatched_clusters` — 版本未发布集群列表
- `boc_version_get_image_group` — 镜像组信息
- `boc_version_get_yaml` — 指定 K8s 资源 YAML

### 工作负载（workload）
- `boc_workload_project_list` — 应用（Project）列表
- `boc_workload_app_list` — 应用+服务列表
- `boc_workload_application_list` — 服务/任务（Application）列表
- `boc_workload_service_network` — 指定服务下网络信息
- `boc_workload_container_list` — 容器列表
- `boc_workload_pod_list` — 实例（Pod）列表
- `boc_workload_kubectl_pods` — kubectl 可访问的 Pod 列表
- `boc_workload_check_internal_service` — 检查命名空间下内部服务是否存在
- `boc_workload_get_internal_load` — 内部负载详情
- `boc_workload_list_internal_loads` — 指定服务下内部负载列表
- `boc_workload_internal_service_list` — 内部负载列表（分页）
- `boc_workload_internal_service_detail` — 内部负载通用查询

## 架构

```
┌───────────── MCP Client (Claude/Codex/Cursor) ─────────────┐
                    │  Streamable HTTP (/mcp)
┌───────────────────▼────────────────────────────────────────┐
│  FastMCP (tool layer)                                      │
│   └─ @mcp.tool / @wrap_tool_errors                         │
├────────────────────────────────────────────────────────────┤
│  Service layer (11 domain services)                        │
│   ├─ auth / application / cluster / workload               │
│   ├─ partition / network / config_secret / service_tree    │
│   ├─ monitor / version / scan                              │
│   └─ Pydantic models + _parse_list() 分页统一解析            │
├────────────────────────────────────────────────────────────┤
│  Client layer                                              │
│   ├─ BocApiClient (Protocol)                               │
│   ├─ BocHttpClient (aiohttp 真实实现，注入 header/重试)      │
│   ├─ TokenManager (三步登录 + 内存缓存 + asyncio.Lock)      │
│   └─ paginate() 通用分页迭代器                              │
├────────────────────────────────────────────────────────────┤
│  Cross-cutting                                             │
│   ├─ middleware.wrap_tool_errors (BocMcpError → MCP 错误)   │
│   ├─ logging_setup (JSON/开发模式 + 敏感字段脱敏)            │
│   └─ health (liveness/readiness)                           │
└────────────────────────────────────────────────────────────┘
```

关键设计：
- **认证流程**：博云三步登录 — `GET /upmstreeapi/bocPortal/getMenus` 提取 `clientId` → `POST /upmstreeapi/login` 换取 `code` → `GET /upmstreeapi/accessToken` 获取 `token`/`refreshToken`/`expiredTime`，之后每次请求在 Header 携带 `token`、`refreshToken`、`systemId`。
- **Token 失效处理**：业务请求返回 401 或匹配平台 token 失效消息时，调用 `token_mgr.invalidate()` 清空缓存并重走登录（clientId 已缓存），原请求自动重试一次。
- **两种响应信封**：博云接口同时存在 `{state,code,data,message,entity}` 和 `{success,currPageNum,pageSize,totalCount,pageCount,rows}` 两种结构，`BocHttpClient` 与各 Service 的 `_parse_list()` 统一解析。
- **错误分层**：`BocMcpError` 有明确子类（认证、网络、业务、配置），`wrap_tool_errors` 中间件将其转为 MCP JSON-RPC 标准错误码。

## 开发

```bash
# 运行单元测试（默认）
python -m pytest

# 运行全部测试含覆盖率阈值 80%
python -m pytest --cov=boc_mcp --cov-fail-under=80

# 运行 E2E 测试（需要启动服务）
python -m pytest -m e2e

# 代码检查
ruff check src tests
ruff format --check src tests
mypy src/boc_mcp
```

目录结构：

```
src/boc_mcp/
├── __main__.py           # python -m boc_mcp 入口
├── server.py             # create_app / run，MCP 装配
├── config.py             # 配置加载（env + yaml）
├── logging_setup.py      # 日志 + 敏感字段脱敏
├── middleware.py         # 错误转 MCP 错误
├── health.py             # /healthz, /healthz/ready
├── auth/
│   ├── models.py         # TokenSet
│   └── token_manager.py  # 三步登录 + 缓存 + 失效重登
├── client/
│   ├── boc_client.py     # BocApiClient Protocol + BocHttpClient
│   ├── errors.py         # BocMcpError 体系
│   └── pagination.py     # 通用分页 async generator
├── models/
│   └── common.py         # ListResult[T], ActionResult
└── services/
    ├── base.py           # BaseService (_get/_post/_list ...)
    ├── auth/ application/ cluster/ config_secret/
    ├── monitor/ network/ partition/ scan/
    ├── service_tree/ version/ workload/
    │   ├── models.py     # Pydantic 领域模型
    │   ├── service.py    # 业务逻辑
    │   └── tools.py      # @mcp.tool 注册
```

## 文档

- docs/usage-guide.md：安装、配置、启动、客户端接入、常见查询场景、排错指南
- docs/api-reference.md：全部 58 个工具的接口文档（参数、类型、必填、返回值）
- docs/test-cases.md：自动化测试索引 + 连接真实平台的手工测试用例 + CI 说明
- docs/api-inventory.md：接口清单（博云 API 路径与工具映射）


## Kubernetes 部署

部署清单位于 \deploy/k8s/\，使用 kustomize 一键部署。详见 \deploy/k8s/README.md\。

\\ash
# 1. 构建并推送镜像
docker build -t registry.your-company.com/boc-mcp/boc-mcp:0.1.0 .
docker push registry.your-company.com/boc-mcp/boc-mcp:0.1.0

# 2. 修改 deploy/k8s/01-config.yaml 中的 BOC_BASE_URL 和账号密码

# 3. 一键部署
kubectl apply -k deploy/k8s
\## Docker

```bash
docker build -t boc-mcp:0.1.0 .
docker run -d -p 8000:8000 \
  -e BOC_BASE_URL=https://your-boc-platform.com \
  -e BOC_USERNAME=admin \
  -e BOC_PASSWORD=your-password \
  --name boc-mcp boc-mcp:0.1.0
```

## 许可证

内部使用，遵循团队规范。