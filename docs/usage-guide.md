# boc-mcp 使用说明

本文档面向使用 boc-mcp 的运维/开发人员，介绍从安装、配置、启动、接入 MCP 客户端到常见查询场景的完整流程。

---

## 1. 环境要求

- Python ≥ 3.12
- 可访问博云 BeyondContainer 平台（HTTP/HTTPS 网络可达）
- 有效的博云平台账号（用户名 + 密码）

---

## 2. 安装与启动

### 2.1 从源码安装

```bash
git clone <internal-repo>/boc-mcp.git
cd boc-mcp
python -m venv .venv
.venv\Scripts\activate      # Windows PowerShell
# source .venv/bin/activate # Linux / macOS
pip install -e ".[dev]"
```

### 2.2 配置（三选一）

**方式 A：环境变量（推荐生产）**

```bash
# 必填
export BOC_BASE_URL="https://boc.your-company.com"
export BOC_USERNAME="admin"
export BOC_PASSWORD="your-password"
# 可选
export BOC_SYSTEM_ID="1"
export BOC_VERIFY_SSL="true"
export BOC_REQUEST_TIMEOUT="30"
export BOC_MAX_RETRIES="3"
export BOC_LOG_LEVEL="INFO"
export BOC_MCP__HOST="0.0.0.0"
export BOC_MCP__PORT="8000"
# 开发模式彩色日志
export BOC_DEV="1"
```

**方式 B：YAML 配置文件**

复制 `config/config.example.yaml` 为 `config.yaml`（放在项目根目录或 `~/.boc-mcp/config.yaml`）：

```yaml
base_url: "https://boc.your-company.com"
username: "admin"
password: "your-password"
verify_ssl: true
request_timeout: 30
max_retries: 3
log_level: "INFO"
system_id: "1"
mcp:
  host: "0.0.0.0"
  port: 8000
```

也可以通过 `BOC_CONFIG_FILE=/path/to/custom.yaml` 指定任意路径。

**方式 C：环境变量 + YAML 混合**

环境变量优先级高于 YAML，因此可以把通用配置写在 YAML，密码等敏感字段用环境变量覆盖。

### 2.3 启动

```bash
python -m boc_mcp
```

启动日志示例：

```
INFO  boc_mcp.server  Starting boc-mcp 0.1.0 on 0.0.0.0:8000
INFO  boc_mcp.auth.token_manager  Logging in as admin
INFO  boc_mcp.auth.token_manager  Login successful, token expires at ...
INFO:     Started server process [12345]
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

健康检查：

```bash
curl http://localhost:8000/healthz         # 存活 {"status":"ok"}
curl http://localhost:8000/healthz/ready    # 就绪 {"status":"ready",...}
```

---

## 3. 接入 MCP 客户端

### 3.1 Codex CLI / Claude Desktop（Streamable HTTP 模式，推荐）

在 MCP 客户端配置文件中加入：

```json
{
  "mcpServers": {
    "boc-mcp": {
      "url": "http://localhost:8000/mcp"
    }
  }
}
```

### 3.2 stdio 模式（无需预先启动服务）

```json
{
  "mcpServers": {
    "boc-mcp": {
      "command": "python",
      "args": ["-m", "boc_mcp"],
      "cwd": "D:\\项目\\boc-mcp",
      "env": {
        "BOC_BASE_URL": "https://boc.your-company.com",
        "BOC_USERNAME": "admin",
        "BOC_PASSWORD": "your-password"
      }
    }
  }
}
```

### 3.3 Docker 运行

```bash
docker build -t boc-mcp:0.1.0 .
docker run -d -p 8000:8000 \
  -e BOC_BASE_URL=https://boc.your-company.com \
  -e BOC_USERNAME=admin \
  -e BOC_PASSWORD=your-password \
  --name boc-mcp boc-mcp:0.1.0
```

容器内置 `HEALTHCHECK` 会请求 `/healthz` 监控存活状态。

---

## 4. 常用查询场景

所有工具都接受 snake_case 参数（如 `cluster_id`），返回驼峰 JSON。

### 4.1 登录/认证

```
boc_auth_status()
boc_auth_refresh()
```

第一次业务请求会自动触发登录。`boc_auth_status` 可查看当前是否已登录、过期时间；token 失效时服务会自动重登，无需人工干预，除非账号密码错误。`boc_auth_refresh` 可以强制重新登录（例如切换账号后）。

### 4.2 查询集群信息

```
# 列出所有集群（简表，不分页）
boc_cluster_list_all()

# 按名称关键字分页搜索
boc_cluster_list(keyword="prod", page=1, page_size=20)

# 查询某个集群的节点
boc_cluster_list_nodes(cluster_id=12, page=1, page_size=50)

# 查询集群状态
boc_cluster_get_state(cluster_id=12)

# 查询集群监控
boc_cluster_get_monitor(cluster_id=12)
```

### 4.3 查询租户下的资源

```
# 查租户下有哪些集群
boc_cluster_list_by_env(env_id=3)

# 查租户下的网络
boc_network_by_env(env_id=3)

# 查租户可用分区
boc_partition_list_available()
```

### 4.4 查询工作负载

```
# 分页查应用（Project）
boc_workload_project_list(cluster_id=12, env_id=3, keyword="order", page=1, page_size=20)

# 分页查服务/任务
boc_workload_application_list(cluster_id=12, env_id=3, keyword="api", page=1, page_size=20)

# 查 Pod 实例
boc_workload_list_pods(cluster_id=12, namespace="default", page=1, page_size=50)

# 查容器
boc_workload_container_list(cluster_id=12, application_id=12345, page=1, page_size=50)

# 查内部 Service
boc_workload_list_services(namespace="default", name="order-service", page=1, page_size=20)
```

### 4.5 查询监控数据

监控接口通过 `params` 字典透传时间范围、指标等扩展参数（具体字段按博云接口规范填写）：

```
boc_monitor_get_project_status(
  application_id=12345,
  cluster_id=12,
  params={"start": 1719900000, "end": 1719986400, "metrics": ["cpu","mem"]}
)

boc_monitor_batch_app(params={"clusterId": 12, "start": ..., "end": ...})
boc_monitor_get_pod(application_id=12345, cluster_id=12)
```

### 4.6 查询版本/镜像/YAML

```
boc_version_list(project_id=100, page=1, page_size=20)
boc_version_get_id_by_name(version_name="v1.2.3")
boc_version_list_image_groups(version_id=999)
boc_version_get_yaml(version_id=999, kind="Deployment", name="order-api")
```

### 4.7 查询服务树与安全扫描

```
boc_service_tree(parent_type="env", parent_id=3, node_type="project")
boc_scan_list_strategies(page=1, page_size=20)
boc_scan_list_reports(page=1, page_size=20)
boc_scan_get_report(report_id=42)
```

### 4.8 查询 Secret 与网络

```
boc_secret_list(master_ip="10.0.0.1", namespace="default", name="db-cred")
boc_network_list_by_name(name="prod-net")
boc_network_available(cluster_id=12)
```

---

## 5. 鉴权与 Token 行为

- 服务启动时**不主动登录**，第一次需要鉴权的请求会触发三步登录（getMenus 取 clientId → login 取 code → accessToken 取 token/refreshToken/expiredTime）。
- Token 缓存于内存，通过 `asyncio.Lock` 保证并发登录安全。
- 业务请求遇到 HTTP 401 或响应体包含博云平台的 token 失效文案时，Token 会被 `invalidate()` 并自动重新登录，原请求自动重试一次。
- Token 自然过期后由 401 逻辑触发重登，无需手动处理。
- `systemId` 默认 `1`，可通过 `BOC_SYSTEM_ID` 修改。

---

## 6. 日志与排错

- 生产日志为 JSON 格式；设置 `BOC_DEV=1` 切换为彩色可读格式。
- 密码、Token、refreshToken 会被自动脱敏替换为 `***`。
- 常见问题：

| 现象 | 可能原因 | 排查 |
| --- | --- | --- |
| 启动后报 "Missing required config: base_url, username, password" | 三个必填项没配 | 检查 `BOC_*` 环境变量或 `config.yaml` |
| 健康检查 `/healthz/ready` 返回 503 | Token 未登录或平台不可达 | 看日志里 `login failed`/`get token failed` 详细信息 |
| 工具返回 -32003 错误 | 账号/密码错误或 Token 已被踢 | 检查密码；调用 `boc_auth_refresh()` 强制重登 |
| 工具返回 -32603 错误 | 网络超时、平台 5xx | 检查 `BOC_BASE_URL` 可达性，适当调大 `BOC_REQUEST_TIMEOUT` |
| HTTPS 证书报错 | 自签证书 | 设置 `BOC_VERIFY_SSL=false`（测试用，生产不推荐） |

---

## 7. 配置项完整列表

| 环境变量 | YAML 键 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `BOC_BASE_URL` | `base_url` | —（必填） | 博云平台根地址 |
| `BOC_USERNAME` | `username` | —（必填） | 登录用户名 |
| `BOC_PASSWORD` | `password` | —（必填） | 登录密码 |
| `BOC_SYSTEM_ID` | `system_id` | `"1"` | 系统 ID |
| `BOC_VERIFY_SSL` | `verify_ssl` | `true` | 是否校验 HTTPS 证书 |
| `BOC_REQUEST_TIMEOUT` | `request_timeout` | `30` | 单次请求超时秒数 |
| `BOC_MAX_RETRIES` | `max_retries` | `3` | 网络错误重试次数 |
| `BOC_LOG_LEVEL` | `log_level` | `"INFO"` | 日志级别 |
| `BOC_CONFIG_FILE` | — | — | 指定 YAML 路径 |
| `BOC_DEV` | — | 未设置 | 设为 `1` 启用开发日志 |
| `BOC_MCP__HOST` | `mcp.host` | `"0.0.0.0"` | 监听地址 |
| `BOC_MCP__PORT` | `mcp.port` | `8000` | 监听端口 |

---

## 8. 完整工具索引

见 [`api-reference.md`](./api-reference.md) 以及 [`test-cases.md`](./test-cases.md)。