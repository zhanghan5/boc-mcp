# boc-mcp 测试用例

本文档包含两部分：
1. **自动化测试索引**：项目中已实现的单元/E2E测试用例清单。
2. **手工测试用例**：连接真实博云平台时用于验证功能的端到端场景，供 QA/运维在部署后执行。

## 1. 自动化测试

运行方式：

```bash
# 单元测试（默认）
python -m pytest
# 全量（含 E2E）+ 覆盖率阈值 80%
python -m pytest --cov=boc_mcp --cov-fail-under=80
# 仅 E2E（启动真实 ASGI app）
python -m pytest tests/e2e -m e2e
# 代码检查 + 类型检查
ruff check src tests
ruff format --check src tests
mypy src/boc_mcp
```

### 1.1 核心模块

#### 配置 (config)
文件：`tests/unit/test_config.py`

| 用例 | 说明 |
| --- | --- |
| `test_no_env_no_file_raises` | 无环境变量无配置文件时抛出 ValueError |
| `test_env_only_minimal` | 仅环境变量最小配置加载成功，默认值正确 |
| `test_yaml_file` | YAML 配置加载成功 |
| `test_env_overrides_yaml` | 环境变量覆盖 YAML 值 |
| `test_config_file_env` | BOC_CONFIG_FILE 指定路径生效 |
| `test_base_url_trailing_slash_stripped` | base_url 末尾斜杠被去除 |

#### 日志 (logging)
文件：`tests/unit/test_logging.py`

| 用例 | 说明 |
| --- | --- |
| `test_setup_logging_produces_json_in_prod` | 生产模式日志为 JSON |
| `test_sensitive_filter_masks_password` | 敏感字段过滤器脱敏 password/token |

#### 错误/中间件 (middleware)
文件：`tests/unit/test_middleware.py`

| 用例 | 说明 |
| --- | --- |
| `test_error_mapping` | 各 BocMcpError 子类映射到正确 JSON-RPC 错误码 |
| `test_non_boc_error_wrapped_as_internal` | 非 BocMcp 异常被包装为 -32603 |

#### 健康检查 (health)
文件：`tests/unit/test_health.py`

| 用例 | 说明 |
| --- | --- |
| `test_liveness` | /healthz 返回 200 ok |
| `test_readiness_ok` | /healthz/ready 客户端可用返回 200 ready |
| `test_readiness_fail` | /healthz/ready 客户端异常返回 503 |
| `test_readiness_no_client_is_ready` | 未注入客户端时就绪返回 200 |

#### Token 管理器
文件：`tests/unit/auth/test_token_manager.py`

| 用例 | 说明 |
| --- | --- |
| `test_lazy_login_performs_3_steps` | 首次 get_token 执行三步登录 |
| `test_client_id_cached_after_relogin` | clientId 在重登录时复用缓存 |
| `test_second_get_uses_cache` | 第二次 get_token 使用缓存不重复登录 |
| `test_invalidate_relogs` | invalidate() 后重新登录 |
| `test_concurrent_invalidate_only_relogs_once` | 并发失效时只登录一次(asyncio.Lock) |
| `test_login_failure_raises_auth_error` | 登录失败抛出 AuthError |
| `test_system_id_from_config` | systemId 取自配置 |

#### HTTP 客户端
文件：`tests/unit/client/test_boc_client.py`

| 用例 | 说明 |
| --- | --- |
| `test_get_injects_auth_headers` | GET 自动注入 token/refreshToken/systemId Header |
| `test_401_triggers_relogin_and_retry` | 401 触发 invalidate+重登+重试一次 |
| `test_401_only_retries_once` | 401 重试最多一次 |
| `test_http_errors_map` | HTTP 4xx/5xx 映射到对应 BocMcpError 子类 |
| `test_timeout_raises_timeout_error` | 超时映射 RequestTimeoutError |
| `test_client_error_raises_network_error` | aiohttp 异常映射 NetworkError |
| `test_path_joining` | 路径拼接正确处理前后斜杠 |

#### 错误类型
文件：`tests/unit/client/test_errors.py`

| 用例 | 说明 |
| --- | --- |
| `test_is_token_invalid_message` | 博云 token 失效文案识别正确 |

#### 分页迭代器
文件：`tests/unit/client/test_pagination.py`

| 用例 | 说明 |
| --- | --- |
| `test_paginate_yields_all_items` | paginate() 自动翻页获取全部条目 |
| `test_paginate_handles_empty` | 空结果正确处理 |

#### 通用模型
文件：`tests/unit/models/test_common.py`

| 用例 | 说明 |
| --- | --- |
| `test_list_result_from_legacy` | ListResult.from_legacy 解析 rows 分页信封 |
| `test_list_result_single_object_envelope` | 单对象信封 data 为 list 时正确解析 |

#### BaseService
文件：`tests/unit/services/base/test_base_service.py`

| 用例 | 说明 |
| --- | --- |
| `test_get_delegates` | _get 委托到 client.get |
| `test_post_put_delete_delegate` | _post/_put/_delete 委托到 client |
| `test_list_paginates` | _list 调用 paginate 迭代 |

### 1.2 领域服务

#### 集群 (cluster)
目录：`tests/unit/services/cluster/`，共 10 个用例，覆盖列表/详情/分页/参数过滤/两种响应信封（直返/legacy rows）。

#### 分区 (partition)
目录：`tests/unit/services/partition/`，共 12 个用例，覆盖列表/详情/分页/参数过滤/两种响应信封（直返/legacy rows）。

#### 应用 (application)
目录：`tests/unit/services/application/`，共 5 个用例，覆盖列表/详情/分页/参数过滤/两种响应信封（直返/legacy rows）。

#### 安全扫描 (scan)
目录：`tests/unit/services/scan/`，共 10 个用例，覆盖列表/详情/分页/参数过滤/两种响应信封（直返/legacy rows）。

#### 服务树 (service_tree)
目录：`tests/unit/services/service_tree/`，共 4 个用例，覆盖列表/详情/分页/参数过滤/两种响应信封（直返/legacy rows）。

#### 配置/密钥 (config_secret)
目录：`tests/unit/services/config_secret/`，共 4 个用例，覆盖列表/详情/分页/参数过滤/两种响应信封（直返/legacy rows）。

#### 监控 (monitor)
目录：`tests/unit/services/monitor/`，共 3 个用例，覆盖列表/详情/分页/参数过滤/两种响应信封（直返/legacy rows）。

### 1.3 工具注册与完整性

- `tests/unit/test_all_tools.py`：验证 11 个模块共注册 58 个工具(`test_total_tool_count`)，且每个工具描述为中文(`test_all_tool_descriptions_are_chinese`)。
- `tests/unit/test_server.py`：验证 `create_app()` 返回 FastMCP，auth 工具与自定义健康路由注册成功。
- 各服务目录下 `test_tools.py`：验证该服务工具正确注册到 mcp。

### 1.4 E2E 测试

文件：`tests/e2e/test_server_live.py`(标记 `@pytest.mark.e2e`)，默认不跑。

- `test_healthz_liveness_returns_200`：通过 Starlette TestClient 启动真实 ASGI app，访问 `/healthz` 返回 200。
- `test_healthz_ready_returns_200`：`/healthz/ready` 返回 200 或 503。

## 2. 手工测试用例（连接真实平台）

以下用例用于在连接真实博云平台时验证 MCP 服务端到端功能。执行前确保：

- `BOC_BASE_URL`/`BOC_USERNAME`/`BOC_PASSWORD` 配置正确；
- 服务已启动：`python -m boc_mcp`，监听 8000 端口；
- 已通过 MCP 客户端（Codex/Claude Desktop）连接到 `http://localhost:8000/mcp`。

### 2.1 认证与会话

| 用例 ID | 步骤 | 预期结果 |
| --- | --- | --- |
| TC-AUTH-01 | 启动服务后首次调用 `boc_auth_status()` | 返回 logged_in=true，含用户名、systemId、过期时间 |
| TC-AUTH-02 | 调用 `boc_auth_refresh()` | 返回 relogin successful，再查状态过期时间更新 |
| TC-AUTH-03 | 使用错误密码启动后调用任意工具 | 返回错误码 -32003，消息含 login failed |

### 2.2 集群查询

| 用例 ID | 步骤 | 预期结果 |
| --- | --- | --- |
| TC-CLUSTER-01 | `boc_cluster_list_all()` | 返回非空 list，每项含 id/name/kind/status |
| TC-CLUSTER-02 | `boc_cluster_list(keyword="", page=1, page_size=5)` | 返回分页对象，items<=5，total/pageCount 正确 |
| TC-CLUSTER-03 | 取第一个集群 id 调 `boc_cluster_get_state(X)` 和 `boc_cluster_get_monitor(X)` | 返回 dict，无错误 |
| TC-CLUSTER-04 | `boc_cluster_list_nodes(cluster_id=X, page=1, page_size=10)` | 返回分页节点列表 |
| TC-CLUSTER-05 | `boc_cluster_list_partitions(cluster_id=X, page=1, page_size=10)` | 返回分页分区列表 |

### 2.3 工作负载

| 用例 ID | 步骤 | 预期结果 |
| --- | --- | --- |
| TC-WORKLOAD-01 | `boc_workload_project_list(cluster_id=X, page=1, page_size=10)` | 返回应用分页列表 |
| TC-WORKLOAD-02 | `boc_workload_list_pods(cluster_id=X, page=1, page_size=20)` | 返回 Pod 列表，items[0] 含 name/namespace/status |
| TC-WORKLOAD-03 | `boc_workload_container_list(cluster_id=X, page=1, page_size=20)` | 返回容器列表 |
| TC-WORKLOAD-04 | `boc_workload_list_services(namespace="default", page=1, page_size=20)` | 返回 Service 列表 |

### 2.4 分区与网络

| 用例 ID | 步骤 | 预期结果 |
| --- | --- | --- |
| TC-PART-01 | `boc_partition_list_all_hosts(cluster_id=X)` | 返回主机节点 list |
| TC-PART-02 | `boc_network_available(cluster_id=X)` | 返回可用网络 list |
| TC-PART-03 | `boc_service_tree(parent_type="env", parent_id=ENV_ID, node_type="project")` | 返回服务树节点列表 |

### 2.5 监控

| 用例 ID | 步骤 | 预期结果 |
| --- | --- | --- |
| TC-MON-01 | `boc_monitor_batch_project(params={"clusterId": X})` | 返回批量项目监控 dict |
| TC-MON-02 | `boc_monitor_batch_app(params={"clusterId": X})` | 返回批量应用监控 dict |
| TC-MON-03 | `boc_monitor_batch_pod(params={"clusterId": X})` | 返回批量 Pod 监控 dict |

### 2.6 版本镜像与安全扫描

| 用例 ID | 步骤 | 预期结果 |
| --- | --- | --- |
| TC-VER-01 | `boc_version_list(page=1, page_size=10)` | 返回版本分页列表 |
| TC-SCAN-01 | `boc_scan_list_strategies(page=1, page_size=10)` | 返回扫描策略分页列表 |
| TC-SCAN-02 | `boc_scan_list_reports(page=1, page_size=10)` | 返回扫描报告分页列表 |

### 2.7 错误与边界

| 用例 ID | 步骤 | 预期结果 |
| --- | --- | --- |
| TC-ERR-01 | 调工具传入不存在 cluster_id（如 999999999） | 返回正常 dict（博云平台一般返回空 data），不抛未处理异常 |
| TC-ERR-02 | 不填必填参数（如 `boc_app_get()` 不传 app_id） | MCP 返回参数错误 -32602 |
| TC-ERR-03 | page_size 传 500 | 结果按 100 条分页返回（page_size 上限 100） |
| TC-ERR-04 | GET http://localhost:8000/healthz | 返回 200 {"status":"ok"} |

## 3. CI 流水线

`.github/workflows/ci.yml` 配置 GitHub Actions CI，每次 push/PR 自动执行：

1. 安装 Python 3.12 与 uv；
2. `uv sync --extra dev` 安装依赖；
3. `ruff check src tests`；
4. `ruff format --check src tests`；
5. `mypy src/boc_mcp`；
6. `pytest --cov=boc_mcp --cov-fail-under=80`（覆盖率 >= 80%）；
7. `uv build` 构建 wheel/sdist。

## 4. 测试数据与 Mock 策略

- 单元测试全部使用 Fake Client 实现 BocApiClient Protocol，返回预设响应字典，不发起真实网络。
- 401 重试通过 Fake Client 两次返回不同结果验证。
- 分页通过 Fake Client 返回指定 total/pageSize 记录，验证 paginate 迭代次数。
- 日志脱敏通过直接处理 LogRecord 验证。
- E2E 测试用 Starlette TestClient 启动完整 ASGI app，不走网络。
- 集成测试（`@pytest.mark.integration`）默认跳过，用于真实平台冒烟。
