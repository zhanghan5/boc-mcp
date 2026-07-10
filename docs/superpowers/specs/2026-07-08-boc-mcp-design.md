# 博云容器云平台 MCP 服务设计文档

- 日期：2026-07-08
- 状态：Approved
- 语言：Python 3.12+
- 传输协议：MCP Streamable HTTP
- 开发方法：Spec-Driven Development (SDD) + Test-Driven Development (TDD)

## 1. 背景与目标

为博云（BoCloud）BeyondContainer 容器云平台构建一个 MCP（Model Context Protocol）Server，使 AI 客户端（如 Codex、Claude Desktop）能够通过标准 MCP 协议调用博云平台的全部能力，包括集群/节点、工作负载、命名空间/租户、镜像、运维（日志/事件/监控/告警）、CI/CD 流水线、配置/密钥等。

### 1.1 非目标
- 不做 UI/前端
- 不做博云平台本身未提供的能力聚合（初期）
- 不提供独立 CLI 命令行工具（MCP Server 本身由 MCP 客户端调度）

### 1.2 质量标准
- 单元测试覆盖率 ≥ 80%
- 完整类型注解，通过 mypy 严格检查
- 容器化部署（Dockerfile + Healthcheck）
- GitHub Actions CI 自动化（lint + format-check + type-check + test + coverage gate）
- 结构化日志，敏感字段脱敏
- HTTP 健康检查端点

## 2. 认证方式

- 登录机制：3 步登录——①获取 clientId → ②用户名+密码+clientId 登录换 code → ③code 换 token/refreshToken（详见 §13.13）
- Token 特性：会过期，接口返回 `expiredTime`；有 refreshToken 但文档中未提供 refresh 端点
- 管理策略：
  - Lazy login：首次 API 请求时触发完整 3 步登录，缓存 token + refreshToken + clientId（clientId 可长期复用），systemId 从配置读取（默认 "1"）
  - 自动重试：请求返回 token 失效（401 或 state=error 提示登录失效）时，重新走步骤 ②③ 换新 token → 重试原请求一次
  - 并发保护：使用 asyncio.Lock 保证多个协程同时触发失效时只发一次登录请求
  - 不做提前刷新

## 3. 架构：三层分层

数据流：MCP Tool 调用 → Service 方法 → BocApiClient（自动注入 token，401 自动重登）→ 博云 API → Pydantic 模型 → Tool 返回结构化对象 → MCP SDK 自动序列化为 JSON 给客户端/LLM。

### 3.1 适配器模式

`client/boc_client.py` 内定义 Protocol 接口 + aiohttp 实现：
- `BocApiClient` Protocol：定义 `request/get/post/put/delete/paginated_get` 方法签名
- `BocHttpClient`：基于 aiohttp 的真实实现
- Service 层只依赖 `BocApiClient` Protocol
- 测试时提供 `FakeBocClient` 内存实现，无需 mock 底层库

## 4. 目录结构

```
boc-mcp/
├── pyproject.toml
├── README.md
├── Dockerfile
├── .github/workflows/ci.yml
├── docs/superpowers/specs/2026-07-08-boc-mcp-design.md
├── config/config.example.yaml
├── src/boc_mcp/
│   ├── __init__.py
│   ├── server.py              # FastMCP 入口 + create_app() 工厂
│   ├── config.py              # pydantic-settings 配置加载
│   ├── logging_setup.py       # 结构化日志 + 脱敏
│   ├── middleware.py          # 统一错误处理（BocMcpError → McpError）
│   ├── health.py              # /healthz, /healthz/ready（挂载到 MCP 底层 Starlette app）
│   ├── auth/
│   │   ├── __init__.py
│   │   ├── token_manager.py   # Token 缓存/失效/重登/并发锁
│   │   └── models.py          # 登录请求/响应模型
│   ├── client/
│   │   ├── __init__.py
│   │   ├── boc_client.py      # BocApiClient Protocol + BocHttpClient 实现
│   │   ├── errors.py          # 自定义异常体系
│   │   └── pagination.py      # 通用分页生成器
│   ├── models/common.py       # 共享枚举、分页响应模型
│   └── services/
│       ├── __init__.py
│       ├── base.py            # BaseService（通用 _get/_post/_put/_delete/_list）
│       ├── auth/              # 登录流程（clientId/login/accessToken）
│       ├── service_tree/      # 服务树
│       ├── application/       # 应用（Project）详情/列表
│       ├── cluster/           # 集群查询/状态/节点/分区/监控
│       ├── partition/         # 分区/节点/YAML
│       ├── network/           # 网络分区
│       ├── workload/          # 服务/容器/实例/内部负载/kubectlPod
│       ├── monitor/           # 监控数据（应用/服务/容器/实例/状态）
│       ├── version/           # 版本/镜像组/发布集群
│       ├── scan/              # 安全扫描策略/报告
│       └── config_secret/     # Secret 查询
├── tests/
│   ├── conftest.py            # 共享 fixtures
│   ├── unit/
│   │   ├── auth/
│   │   ├── client/
│   │   └── services/
│   ├── integration/           # @pytest.mark.integration，默认跳过
│   └── e2e/                   # @pytest.mark.e2e，默认跳过
└── scripts/dev_server.py
```

`health.py` 通过 FastMCP 暴露的底层 Starlette ASGI app 挂载额外路由（`/healthz`、`/healthz/ready`），不占用 MCP 协议路径（默认 `/mcp`）。

每个 `services/<domain>/` 子包结构一致：
```
services/<domain>/
├── __init__.py      # 导出 register_tools(mcp, client)
├── models.py        # 本域 Pydantic 请求/响应模型
├── service.py       # XxxService(BaseService)，纯业务逻辑，无 MCP 依赖
└── tools.py         # register_tools 实现，@mcp.tool() 装饰器
```

## 5. 工具命名与注册约定

- 工具名统一加前缀 `boc_`，如 `boc_list_deployments`、`boc_get_pod_logs`、`boc_restart_deployment`
- 工具描述用中文，清晰说明用途、场景、关键参数含义
- 工具函数返回 Pydantic 模型或基本类型，由 MCP SDK 自动序列化（不手动 dump 成 JSON 字符串）
- 所有列表类工具必须显式暴露 `page`、`page_size` 参数；`page_size` 默认 20、最大 100，在工具层做上限截断，避免单次返回超大数据压爆 LLM 上下文
- 错误处理统一通过 MCP middleware 完成：捕获 `BocMcpError` 并转为 MCP 错误码（INVALID_PARAMS / NOT_FOUND / PERMISSION_DENIED / INTERNAL_ERROR），附带可读中文 message
- 每个域的 `register_tools(mcp, client)` 集中注册，`server.py` 调用各域 register 函数
- MCP `instructions`（系统提示）描述博云平台基本概念、工具使用建议、常见工作流指引
- 所有工具均为只读查询（接口文档未提供写操作），工具描述里明确告知 LLM 本 MCP 仅支持查询

## 6. HTTP 客户端能力

- 基于 aiohttp 异步实现 `BocApiClient`
- 每次请求自动注入 3 个 header：`token`、`refreshToken`、`systemId`（token/refreshToken 来自登录流程，systemId 默认 "1"，可配置）
- 401 处理：调用 `token_manager.invalidate()` → 重新登录 → 重试原请求一次（最多一次）
- 重试策略：5xx、连接错误、超时做指数退避重试（`max_retries` 次，默认 3；401 重登不计入重试次数）
- 统一错误映射：
  - 400 → `BadRequestError`
  - 401 → `AuthError`（重试后仍 401 才抛出）
  - 403 → `ForbiddenError`
  - 404 → `NotFoundError`
  - 409 → `ConflictError`
  - 5xx → `ServerError`
  - 网络错误 → `NetworkError`
  - 超时 → `RequestTimeoutError`
- 分页：`paginated_get()` 返回 `AsyncIterator[dict]`，自动翻页
- 支持 `verify_ssl` 开关（对接自签证书环境）
- 日志：每次请求记录 method/path/status/duration_ms/request_id

### 6.1 异常类层次

```
BocMcpError（基类：message, details）
├── APIError（status_code, code, body）
│   ├── BadRequestError
│   ├── ForbiddenError
│   ├── NotFoundError
│   ├── ConflictError
│   ├── ServerError
│   └── AuthError
├── NetworkError
└── RequestTimeoutError
```

## 7. 配置

使用 `pydantic-settings`，加载优先级：环境变量 > YAML 配置文件 > 默认值。

### 7.1 配置项

| Key | 环境变量 | 描述 | 默认 |
|---|---|---|---|
| `base_url` | `BOC_BASE_URL` | 博云平台地址 | 必填 |
| `username` | `BOC_USERNAME` | 登录用户名 | 必填 |
| `password` | `BOC_PASSWORD` | 登录密码 | 必填 |
| `verify_ssl` | `BOC_VERIFY_SSL` | 验证 SSL 证书 | `true` |
| `request_timeout` | `BOC_REQUEST_TIMEOUT` | 请求超时秒数 | `30` |
| `max_retries` | `BOC_MAX_RETRIES` | 失败最大重试次数 | `3` |
| `log_level` | `BOC_LOG_LEVEL` | 日志级别 | `INFO` |
| `mcp.host` | `BOC_MCP_HOST` | HTTP 监听地址 | `0.0.0.0` |
| `mcp.port` | `BOC_MCP_PORT` | HTTP 监听端口 | `8000` |
| `system_id` | `BOC_SYSTEM_ID` | 请求头 systemId 值 | `"1"` |
| `config_file` | `BOC_CONFIG_FILE` | 配置文件路径 | 见下文 |

### 7.2 YAML 文件查找顺序
1. `BOC_CONFIG_FILE` 环境变量指定路径
2. `./config.yaml`
3. `~/.boc-mcp/config.yaml`

## 8. 日志与可观测性

- 标准 `logging` 模块，生产输出 JSON 行格式；开发环境（`BOC_DEV=true`）输出彩色文本
- 字段：`timestamp`、`level`、`logger`、`message`、`method`、`path`、`status_code`、`duration_ms`、`tool_name`、`request_id`
- 每个请求自动生成 UUID `request_id`，贯穿 TokenManager → Client → Service → Tool → middleware 日志
- 脱敏：日志不打印 `password`、`Authorization` 头、明文 token；响应体中出现 token 字段也以 `***` 替换
- Health 端点：
  - `GET /healthz` → 200 `{"status": "ok"}` 存活检查（不访问博云）
  - `GET /healthz/ready` → 200/503，调轻量 API（如获取当前用户信息）验证 token 和连通性

## 9. 部署

### 9.1 Dockerfile
- 基础镜像：`python:3.12-slim`
- 多阶段构建（builder + runtime）
- 使用 `uv` 安装依赖
- 非 root 用户运行（uid 10001）
- `EXPOSE 8000`
- `HEALTHCHECK` 调用 `/healthz`
- 入口：以 mcp SDK 最新版推荐的 streamable-http 启动方式为准（`FastMCP.run(transport="streamable-http")` 或等价形式）

### 9.2 本地开发
- `scripts/dev_server.py` 启动开发 server，可开启 reload
- 配置使用 `config/config.example.yaml` 拷贝后的 `config.yaml`

## 10. 依赖

运行时：
- `mcp`（官方 Python SDK，FastMCP + streamable-http）
- `aiohttp`
- `pydantic>=2`、`pydantic-settings`
- `pyyaml`

开发时：
- `pytest`、`pytest-asyncio`、`pytest-cov`、`pytest-mock`
- `ruff`（lint + format）
- `mypy`
- `aioresponses`（mock aiohttp）

## 11. TDD 开发顺序

严格按三层自底向上，每层先写测试再写实现（Red → Green → Refactor）：

1. **TokenManager**：单元测试覆盖首次登录、缓存命中、401 失效重登、并发单次登录（Lock 保证）；然后实现
2. **BocHttpClient**：单元测试覆盖 token 注入、401 重试一次（不超过一次）、重试指数退避、错误码映射、分页、超时、SSL 校验开关；然后实现
3. **错误处理 middleware**：单元测试覆盖各 BocMcpError 子类 → MCP 错误码映射；然后实现
4. **BaseService**：单元测试覆盖 _get/_post/_put/_delete/_list 委托 client 正确；然后实现
5. **各领域 Service**：拿到接口文档后逐个域推进，每个方法先写 Service 单测（用 FakeBocClient 预置响应）→ 实现
6. **各领域 tools**：先写 Tool 单测（验证参数/描述/分页上限/middleware 异常转义/调用 service）→ 实现
7. **server.create_app + health 路由**：测试工具注册完整性、配置加载、/healthz 响应；然后实现
8. **E2E**：启动真实 MCP server（绑定随机端口）+ MCP HTTP client，跑通端到端调用（登录→列资源→详情）
9. **Dockerfile + CI**：构建镜像并验证 CI pipeline 全绿

### 11.1 测试分层

| 层级 | 目录 | 默认执行 | 覆盖率 |
|---|---|---|---|
| 单元测试 | `tests/unit/` | 是 | 计入 80% |
| 集成测试 | `tests/integration/` | 否（`-m "not integration"`） | 不计入 |
| E2E 测试 | `tests/e2e/` | 否（`-m "not e2e"`） | 不计入 |

### 11.2 关键 fixtures（`tests/conftest.py`）

- `fake_client`：`FakeBocClient` 内存实现，支持预置响应和断言调用参数
- `token_manager`：测试配置 + mock 登录请求
- `http_client`：真实 `BocHttpClient` + `aioresponses` mock 底层
- `mcp_app`：`create_app()` 产出的 FastMCP 实例，用于工具注册测试


## 12. 下一步前置依赖

- 接口文档已解析完成（见 §13），所有 58 个接口已按模块整理为工具清单
- 待确认：
  - `systemId` header 的值如何获取/配置
  - refreshToken 是否存在刷新端点（文档未提供，按"重登"处理）
  - 后续若有写操作接口（创建/伸缩/删除等）补充，按相同模式扩展 service 子包
- 架构层和基础设施层（auth 三步登录/client/config/logging/middleware/health/server 入口/CI/Dockerfile）可直接开工

## 13. 接口清单（基于博云容器接口文档.pdf）

> 文档共包含 **58 个 HTTP 接口**，均为**查询（GET/POST 只读）**操作；无创建/更新/删除/伸缩等写操作接口。

> 登录流程为 3 步：① `GET /upmstreeapi/bocPortal/getMenus` 获取 clientId → ② `POST /upmstreeapi/login`（typeConfigId=0 + userName + password + clientId）获取 code（在响应 data.code 字段）→ ③ `GET /upmstreeapi/accessToken?code=<code>` 获取 token + refreshToken + expiredTime。

> 后续请求通过 HTTP header 传递认证：`token`、`refreshToken`、`systemId`。


### 13.1 auth（登录认证）（3 个工具）

| 工具名 | 方法 | 路径 | 说明 | 必填参数 |
|---|---|---|---|---|
| `boc_auth_get_client_id` | GET | `/upmstreeapi/bocPortal/getMenus` | 获取 clientId | — |
| `boc_auth_login` | POST | `/upmstreeapi/login` | 登录 | `typeConfigId`, `userName`, `password`, `clientId` |
| `boc_auth_get_token` | GET | `/upmstreeapi/accessToken` | 获取 token | — |

### 13.2 service_tree（服务树）（1 个工具）

| 工具名 | 方法 | 路径 | 说明 | 必填参数 |
|---|---|---|---|---|
| `boc_service_tree` | GET | `/service-tree` | 服务树右侧菜单，有数据权限控制 | — |

### 13.3 application（应用/项目）（2 个工具）

| 工具名 | 方法 | 路径 | 说明 | 必填参数 |
|---|---|---|---|---|
| `boc_app_get` | GET | `/applications/{id}` | 详情 | `id` |
| `boc_app_list` | GET | `/bocApplication/projects/list` | 列表 | — |

### 13.4 cluster（集群管理）（10 个工具）

| 工具名 | 方法 | 路径 | 说明 | 必填参数 |
|---|---|---|---|---|
| `boc_cluster_list` | POST | `/cluster/v2.3/list` | 查询集群 | — |
| `boc_cluster_list_all` | POST | `/cluster/v2.3/listAll` | 查询所有集群 | — |
| `boc_cluster_list_base_info` | POST | `/cluster/v3.0/listBaseInfo` | 查询集群基本信息 | `currPageNum`, `pageSize` |
| `boc_cluster_get_monitor` | GET | `/cluster/v3.0/listMonitorInfo/{clusterId}` | 查询集群监控信息 | — |
| `boc_cluster_get_state` | GET | `/platformCluster/v2.3/getClusterState/{clusterId}` | 获得集群状态 | — |
| `boc_cluster_list_nodes` | POST | `/platformCluster/v2.3/getClusterNodes` | 获取集群节点 | `currPageNum`, `pageSize`, `clusterId` |
| `boc_cluster_list_partitions` | POST | `/platformCluster/v2.3/getPartition` | 获取集群分区 | `clusterId`, `currPageNum`, `pageSize` |
| `boc_cluster_partition_resource` | GET | `/cluster/v2.3/clusterPartitionResource/{hostIds}` | 分区 CPU，MEM 查询 | `hostIds` |
| `boc_cluster_list_by_env` | GET | `/platformCluster/v2.3/getClusterByEnvId/{envId}` | 租户下集群 | — |
| `boc_partition_list_available` | POST | `/partition/v2.3/clusterPartition` | 查询当前租户下集群可用分区 | — |

### 13.5 partition（分区与节点）（9 个工具）

| 工具名 | 方法 | 路径 | 说明 | 必填参数 |
|---|---|---|---|---|
| `boc_partition_list` | POST | `/partition/v2.3/list` | 查询分区 | — |
| `boc_partition_get_default` | POST | `/partition/v3.3/getDefaultPartition/{clusterId}` | 查询集群默认分区 | — |
| `boc_partition_get_meta` | POST | `/partition/v2.3/getPartitionMeta` | 条件查询分区信息 | — |
| `boc_partition_list_default` | POST | `/partition/v2.3/listByKind` | 查询普通-默认分区 | — |
| `boc_partition_list_nodes` | POST | `/partition/v2.3/nodelist` | 分区节点列表 | — |
| `boc_partition_list_all_hosts` | POST | `/partition/v3.3/getAllHost` | 查询集群分区下所有节点 | — |
| `boc_partition_all_info` | POST | `/partition/v2.3/allInfo` | 租户集群下所有节点 | `clusterId`, `envId` |
| `boc_partition_detail` | POST | `/partition/v2.3/detailByCondition` | 获取分区实例信息 | — |
| `boc_version_get_yaml` | POST | `/map/v1.8/queryYaml` | 查询 YAML | `kind`, `name` |

### 13.6 network（网络分区）（3 个工具）

| 工具名 | 方法 | 路径 | 说明 | 必填参数 |
|---|---|---|---|---|
| `boc_network_list_by_name` | GET | `/partitionNetwork/getListByNetWorkName` | 获取网络分区 | `id`, `ips` |
| `boc_network_list_available` | GET | `/partitionNetwork/getUnUseredList` | 获取可用网络 | `clusterId` |
| `boc_network_list_by_env` | POST | `/partitionNetwork/v2.3/getNetworkListByEnvId` | 获取租户网络 | — |

### 13.7 workload（工作负载/服务/容器/实例）（12 个工具）

| 工具名 | 方法 | 路径 | 说明 | 必填参数 |
|---|---|---|---|---|
| `boc_workload_list_projects` | POST | `/query/v1.8/queryProject` | 查询应用 | — |
| `boc_workload_list_projects_and_apps` | POST | `/query/v1.8/queryProjectAndApplication` | 查询应用和服务 | `clusterId`, `envId`, `userId` |
| `boc_workload_list_applications` | POST | `/query/v1.8/queryApplication` | 查询服务或任务 | `currPageNum`, `envId`, `pageSize`, `projectId`, `resourceType` |
| `boc_workload_get_app_networks` | POST | `/query/v2.3/getNetworkByApplicationId` | 获取服务下网络信息 | `applicationId`, `clusterId` |
| `boc_workload_list_containers` | POST | `/query/v1.8/queryContainer` | 查询容器 | `currPageNum`, `envId`, `pageSize`, `podId`, `prometheusUrl`, `resourceType` |
| `boc_workload_list_pods` | POST | `/query/v1.8/queryPod` | 查询实例 | `applicationId`, `clusterId`, `currPageNum`, `envId`, `hostName`, `pageSize` ... |
| `boc_workload_list_kubectl_pods` | POST | `/query/v3.0/queryKubectlPods` | 查询 kubectlPod | `masterIp`, `resourceType` |
| `boc_workload_check_service` | POST | `/service/v2.3/checkService` | 查看内部负载是否存在 | `applicationId`, `clusterId`, `namespace` |
| `boc_workload_get_service_by_app` | POST | `/service/v2.3/getServiceByApplicationId` | 根据服务 id 获取内部负载 | `masterMap`, `projectId`, `projectName`, `platformType`, `applicationName` |
| `boc_workload_list_services_by_app` | POST | `/query/v2.3/queryServiceByApplicationId` | 获取服务下内部负载 | `masterIp`, `masterMap`, `platformType`, `projectId`, `projectName` |
| `boc_workload_list_services` | POST | `/service/v2.3/listServiceByPage` | 获分页获取内部负载 | `clusterId`, `namespace`, `pageSize` |
| `boc_workload_query_service` | POST | `/query/v1.8/queryService` | 内部负载查询 | — |

### 13.8 monitor（监控数据）（8 个工具）

| 工具名 | 方法 | 路径 | 说明 | 必填参数 |
|---|---|---|---|---|
| `boc_monitor_get_project_status` | POST | `/query/v1.8/queryProjectStatus` | 查询应用状态 | `projectId` |
| `boc_monitor_batch_project` | POST | `/query/v1.8/queryBatchProjectMonitor` | 查询应用监控数据 | — |
| `boc_monitor_batch_project_status` | POST | `/query/v1.8/queryBatchProjectStatus` | 查询服务状态 | — |
| `boc_monitor_get_app` | POST | `/query/v1.8/queryApplicationMonitor` | 查询服务或任务监控数据 | `applicationContainerName`, `applicationNamespace`, `applicationPodName`, `clusterId`, `id`, `kubernetesVersion` ... |
| `boc_monitor_batch_app` | POST | `/query/v1.8/queryBatchApplicationMonitor` | 查询服务监控数据 | — |
| `boc_monitor_get_pod` | POST | `/query/v1.8/queryPodMonitor` | 查询容器实例监控数据 | `applicationContainerName`, `applicationNamespace`, `applicationPodName`, `containerId`, `kubernetesVersion`, `prometheusUrl` ... |
| `boc_monitor_batch_container` | POST | `/query/v1.8/queryBatchContainerMonitor` | 查询容器监控数据 | — |
| `boc_monitor_batch_pod` | POST | `/query/v1.8/queryBatchPodMonitor` | 查询实例监控数据 | — |

### 13.9 version（版本/镜像/YAML）（6 个工具）

| 工具名 | 方法 | 路径 | 说明 | 必填参数 |
|---|---|---|---|---|
| `boc_version_list` | POST | `/query/v1.6/queryVersion` | 版本查询 | `appId`, `isTask` |
| `boc_version_get_id_by_name` | POST | `/query/v2.3/queryVersionIdByVersionName` | 查询版本 Id | `appId`, `clusterId`, `versionName` |
| `boc_version_list_image_groups` | POST | `/query/v1.8/queryVersionImageGroupByApplicationId` | 查询版本镜像组 | `appId`, `clusterId` |
| `boc_version_list_dispatched_clusters` | POST | `/query/v2.3/queryDispatchVersionByVersionName` | 获取版本下已发布的集群 | `applicationId` |
| `boc_version_list_undispatched_clusters` | POST | `/query/v2.3/queryUnDispatchVersionByVersionName` | 获取版本下未发布的集群 | `applicationId`, `projectId`, `versionName` |
| `boc_version_get_image_group` | POST | `/query/v2.3/queryImageGroup` | ImageGroup 查询 | `applicationName`, `projectId`, `resourceType` |

### 13.10 scan（安全扫描）（3 个工具）

| 工具名 | 方法 | 路径 | 说明 | 必填参数 |
|---|---|---|---|---|
| `boc_scan_list_strategies` | POST | `/strategy/v3.3/list` | 扫描策略列表<分页> | — |
| `boc_scan_get_report` | GET | `/report/v3.3/detail/{id}` | 扫描报告详情 | `id` |
| `boc_scan_list_reports` | POST | `/report/v3.3/list` | 扫描报告列表<分页> | — |

### 13.11 config_secret（Secret）（1 个工具）

| 工具名 | 方法 | 路径 | 说明 | 必填参数 |
|---|---|---|---|---|
| `boc_secret_list` | POST | `/secret/v2.3/list` | 查询 secret 列表 | — |

**合计：58 个 MCP 工具。**


### 13.12 工具命名约定

- 所有工具加 `boc_<domain>_<action>` 前缀，语义化命名（非简单 URL 拼接），例如：
  - 认证：`boc_auth_get_client_id`、`boc_auth_login`、`boc_auth_get_token`
  - 集群：`boc_cluster_list`、`boc_cluster_get_state`、`boc_cluster_list_nodes`
  - 工作负载：`boc_workload_list_pods`、`boc_workload_list_containers`、`boc_workload_list_services`
  - 监控：`boc_monitor_get_pod`、`boc_monitor_batch_app`、`boc_monitor_batch_pod`
  - 版本：`boc_version_list`、`boc_version_get_yaml`、`boc_version_list_image_groups`
- 分页类工具统一保留 `page`、`page_size` 参数，`page_size` 默认 20、最大 100
- 路径参数（`{clusterId}`、`{id}`、`{envId}`、`{hostIds}`）作为工具必填参数
- POST body 参数按接口文档"是否必填"映射为工具必填/可选参数
- 所有工具返回结构化 Pydantic 模型，由 MCP SDK 自动序列化

### 13.13 登录流程与 Token 管理（修订）

根据接口文档，博云平台登录为 3 步流程（不同于常见 OAuth）：

1. **获取 clientId**：`GET /upmstreeapi/bocPortal/getMenus`（无认证 header）→ 返回体 `data.redirectLoginUrl` 是一个 URL，其 query 参数中包含 `clientId`；**clientId 可长期缓存复用**
2. **登录**：`POST /upmstreeapi/login`，body `{typeConfigId: 0, userName, password, clientId}` → 返回 `data.code`（注意是 `data` 对象下的 `code` 字段，不是顶层状态码）
3. **获取 token**：`GET /upmstreeapi/accessToken?code=<data.code>` → 返回 `data.token`、`data.refreshToken`、`data.expiredTime`（ISO8601 时间）

**后续业务请求 Header**：
- `token: <token>`
- `refreshToken: <refreshToken>`
- `systemId: <system_id>`（默认 `"1"`，可通过 `BOC_SYSTEM_ID` 配置项覆盖）
- Token 仅通过 Header 传递，请求 Body 中无需携带 token 字段

**Token 失效处理**：
- 业务接口若返回 `state: "error"` 且 message 包含"token""登录""过期""失效"等关键词，或 HTTP 状态 401，视为 token 失效
- 失效时：invalidate 当前 token → 重新走步骤 ②③ 获取新 token（clientId 复用）→ 用新 token 重试原请求一次
- 使用 `asyncio.Lock` 保证并发协程仅触发一次重登录

### 13.14 响应格式统一

博云平台有两种响应包装格式，Client 层需统一处理：
- **登录/服务树等接口**：`{state: "success"/"error", code: 200/..., data: ..., message: ..., entity: ...}`
- **业务查询接口**：`{success: true/false, currPageNum, pageSize, totalCount, pageCount, rows: [...], message, data}`

Service 层返回：
- 单对象：直接返回 Pydantic 模型（解析 `data` 或 `rows[0]`）
- 列表：返回 `ListResult[T]`，包含 `items`、`page`、`page_size`、`total`、`page_count`

**已确认项：**
1. `systemId` 默认值为 `"1"`，通过配置项 `BOC_SYSTEM_ID` 可覆盖
2. Token 仅通过 Header 传递，请求 Body 中无需携带 token 字段
3. 当前接口清单基于 2022-09 版 PDF（58 个只读接口），后续接口补充按相同模式扩展
4. refreshToken 无刷新端点，token 失效时走"重新登录 ②③ 步"流程

