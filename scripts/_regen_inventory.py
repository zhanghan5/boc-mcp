# -*- coding: utf-8 -*-
"""Regenerate §13 of the spec with better semantic tool names."""
import json, io, sys, os, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

with open(r'D:\项目\boc-mcp\docs\apis_with_params.json', 'r', encoding='utf-8') as f:
    apis = json.load(f)

def classify(u):
    u = u.lower()
    if 'upmstreeapi' in u or 'bocportal' in u: return 'auth'
    if 'service-tree' in u: return 'service_tree'
    if '/applications' in u or 'bocapplication' in u: return 'application'
    if 'partitionnetwork' in u: return 'network'
    if '/secret' in u: return 'config_secret'
    if '/report' in u or '/strategy' in u: return 'scan'
    if '/cluster' in u or 'platformcluster' in u: return 'cluster'
    if '/partition' in u or '/map/' in u: return 'partition'
    if 'queryyaml' in u: return 'version'  # YAML query fits with version
    if 'version' in u or 'imagegroup' in u or 'dispatchversion' in u or 'undispatchversion' in u: return 'version'
    if 'monitor' in u or 'projectstatus' in u or 'batchprojectstatus' in u: return 'monitor'
    return 'workload'

from collections import OrderedDict
MODULES = OrderedDict([
    ('auth',            ('auth', '登录认证', [
        ('/bocPortal/getMenus', 'boc_auth_get_client_id', '获取 clientId'),
        ('/login', 'boc_auth_login', '登录（获取 code）'),
        ('/accessToken', 'boc_auth_get_token', '用 code 换 token/refreshToken'),
    ])),
    ('service_tree',    ('service_tree', '服务树', [])),
    ('application',     ('application', '应用/项目', [])),
    ('cluster',         ('cluster', '集群管理', [])),
    ('partition',       ('partition', '分区与节点', [])),
    ('network',         ('network', '网络分区', [])),
    ('workload',        ('workload', '工作负载/服务/容器/实例', [])),
    ('monitor',         ('monitor', '监控数据', [])),
    ('version',         ('version', '版本/镜像/YAML', [])),
    ('scan',            ('scan', '安全扫描', [])),
    ('config_secret',   ('config_secret', 'Secret', [])),
])

# Semantic tool-name overrides for known endpoints
NAME_OVERRIDES = {
    '/upmstreeapi/bocPortal/getMenus': 'boc_auth_get_client_id',
    '/upmstreeapi/login': 'boc_auth_login',
    '/upmstreeapi/accessToken': 'boc_auth_get_token',
    '/service-tree': 'boc_service_tree',
    '/applications/{id}': 'boc_app_get',
    '/bocApplication/projects/list': 'boc_app_list',
    '/cluster/v2.3/list': 'boc_cluster_list',
    '/cluster/v2.3/listAll': 'boc_cluster_list_all',
    '/cluster/v3.0/listBaseInfo': 'boc_cluster_list_base_info',
    '/cluster/v3.0/listMonitorInfo/{clusterId}': 'boc_cluster_get_monitor',
    '/platformCluster/v2.3/getClusterState/{clusterId}': 'boc_cluster_get_state',
    '/platformCluster/v2.3/getClusterNodes': 'boc_cluster_list_nodes',
    '/platformCluster/v2.3/getPartition': 'boc_cluster_list_partitions',
    '/cluster/v2.3/clusterPartitionResource/{hostIds}': 'boc_cluster_partition_resource',
    '/platformCluster/v2.3/getClusterByEnvId/{envId}': 'boc_cluster_list_by_env',
    '/partition/v2.3/list': 'boc_partition_list',
    '/partition/v3.3/getDefaultPartition/{clusterId}': 'boc_partition_get_default',
    '/partition/v2.3/getPartitionMeta': 'boc_partition_get_meta',
    '/partition/v2.3/listByKind': 'boc_partition_list_default',
    '/partition/v2.3/nodelist': 'boc_partition_list_nodes',
    '/partition/v3.3/getAllHost': 'boc_partition_list_all_hosts',
    '/partition/v2.3/allInfo': 'boc_partition_all_info',
    '/partition/v2.3/detailByCondition': 'boc_partition_detail',
    '/partition/v2.3/clusterPartition': 'boc_partition_list_available',
    '/partitionNetwork/getListByNetWorkName': 'boc_network_list_by_name',
    '/partitionNetwork/getUnUseredList': 'boc_network_list_available',
    '/partitionNetwork/v2.3/getNetworkListByEnvId': 'boc_network_list_by_env',
    '/strategy/v3.3/list': 'boc_scan_list_strategies',
    '/report/v3.3/detail/{id}': 'boc_scan_get_report',
    '/report/v3.3/list': 'boc_scan_list_reports',
    '/query/v1.8/queryProject': 'boc_workload_list_projects',
    '/query/v1.8/queryProjectAndApplication': 'boc_workload_list_projects_and_apps',
    '/query/v1.8/queryApplication': 'boc_workload_list_applications',
    '/query/v2.3/getNetworkByApplicationId': 'boc_workload_get_app_networks',
    '/query/v1.8/queryContainer': 'boc_workload_list_containers',
    '/query/v1.8/queryPod': 'boc_workload_list_pods',
    '/query/v3.0/queryKubectlPods': 'boc_workload_list_kubectl_pods',
    '/service/v2.3/checkService': 'boc_workload_check_service',
    '/service/v2.3/getServiceByApplicationId': 'boc_workload_get_service_by_app',
    '/query/v2.3/queryServiceByApplicationId': 'boc_workload_list_services_by_app',
    '/service/v2.3/listServiceByPage': 'boc_workload_list_services',
    '/query/v1.8/queryService': 'boc_workload_query_service',
    '/query/v1.8/queryProjectStatus': 'boc_monitor_get_project_status',
    '/query/v1.8/queryBatchProjectMonitor': 'boc_monitor_batch_project',
    '/query/v1.8/queryBatchProjectStatus': 'boc_monitor_batch_project_status',
    '/query/v1.8/queryApplicationMonitor': 'boc_monitor_get_app',
    '/query/v1.8/queryBatchApplicationMonitor': 'boc_monitor_batch_app',
    '/query/v1.8/queryPodMonitor': 'boc_monitor_get_pod',
    '/query/v1.8/queryBatchContainerMonitor': 'boc_monitor_batch_container',
    '/query/v1.8/queryBatchPodMonitor': 'boc_monitor_batch_pod',
    '/query/v1.6/queryVersion': 'boc_version_list',
    '/query/v2.3/queryVersionIdByVersionName': 'boc_version_get_id_by_name',
    '/query/v1.8/queryVersionImageGroupByApplicationId': 'boc_version_list_image_groups',
    '/query/v2.3/queryDispatchVersionByVersionName': 'boc_version_list_dispatched_clusters',
    '/query/v2.3/queryUnDispatchVersionByVersionName': 'boc_version_list_undispatched_clusters',
    '/query/v2.3/queryImageGroup': 'boc_version_get_image_group',
    '/map/v1.8/queryYaml': 'boc_version_get_yaml',
    '/secret/v2.3/list': 'boc_secret_list',
}

by_mod = {k: [] for k in MODULES}
for a in apis:
    url_base = a['url'].split('?')[0]
    m = classify(a['url'])
    by_mod.setdefault(m, []).append(a)

# Build §13
lines = []
lines.append('## 13. 接口清单（基于博云容器接口文档.pdf）\n')
lines.append('> 文档共包含 **58 个 HTTP 接口**，均为**查询（GET/POST 只读）**操作；无创建/更新/删除/伸缩等写操作接口。\n')
lines.append('> 登录流程为 3 步：① `GET /upmstreeapi/bocPortal/getMenus` 获取 clientId → ② `POST /upmstreeapi/login`（typeConfigId=0 + userName + password + clientId）获取 code（在响应 data.code 字段）→ ③ `GET /upmstreeapi/accessToken?code=<code>` 获取 token + refreshToken + expiredTime。\n')
lines.append('> 后续请求通过 HTTP header 传递认证：`token`、`refreshToken`、`systemId`。\n')
total = 0
for mod_key, (mod_pkg, mod_label, _) in MODULES.items():
    items = by_mod.get(mod_key, [])
    if not items:
        continue
    total += len(items)
    idx = list(MODULES).index(mod_key) + 1
    lines.append(f'\n### 13.{idx} {mod_pkg}（{mod_label}）（{len(items)} 个工具）\n')
    lines.append('| 工具名 | 方法 | 路径 | 说明 | 必填参数 |')
    lines.append('|---|---|---|---|---|')
    for a in items:
        method = a['method']
        url = a['url']
        url_base = url.split('?')[0]
        title = (a.get('title') or '').replace('|','/').replace('\n',' ').strip()
        tool = NAME_OVERRIDES.get(url_base, f'boc_{mod_pkg}_generic')
        req_p = [p['name'] for p in a['params'] if p['required']]
        opt_p = [p['name'] for p in a['params'] if not p['required']]
        req_str = ', '.join(f'`{p}`' for p in req_p[:6]) if req_p else '—'
        if len(req_p) > 6: req_str += ' ...'
        lines.append(f'| `{tool}` | {method} | `{url_base}` | {title} | {req_str} |')

lines.append(f'\n**合计：{total} 个 MCP 工具。**\n')

lines.append('''
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

**后续业务请求 Header**（按接口文档示例）：
- `token: <token>`
- `refreshToken: <refreshToken>`
- `systemId: <值待定>`（接口示例出现此 header，具体含义/来源待确认；初始版本可由配置项 `boc_system_id` 传入，缺省为空字符串）

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

**待确认项：**
1. `systemId` header 的值与来源（当前由配置项传入）
2. 是否存在 v2.x 最新接口文档（当前 PDF 为 2022-09 版本，部分接口路径版本为 v1.6~v3.3）
3. 是否有写操作接口（创建/伸缩/删除/重启等）未在本 PDF 中，后续拿到再扩展
4. refreshToken 是否存在刷新端点（文档未提供，当前按"重登"处理）
''')

inventory_md = '\n'.join(lines)

# Write a standalone API inventory file
inv_path = r'D:\项目\boc-mcp\docs\api-inventory.md'
with open(inv_path, 'w', encoding='utf-8') as f:
    f.write('# 博云容器云平台 MCP — 接口清单\n\n')
    f.write('> 来源：博云容器接口文档.pdf（2022-09 版）\n\n')
    # strip section 13.12-13.14 for this file
    inv_content = inventory_md
    f.write(inv_content.split('### 13.12')[0])
print('written inventory:', inv_path)

# Update spec: replace from "## 13." to end with new content
spec_path = r'D:\项目\boc-mcp\docs\superpowers\specs\2026-07-08-boc-mcp-design.md'
with open(spec_path, 'r', encoding='utf-8') as f:
    spec = f.read()

idx13 = spec.find('## 13.')
if idx13 < 0:
    # append
    spec += '\n\n' + inventory_md
else:
    spec = spec[:idx13] + inventory_md

with open(spec_path, 'w', encoding='utf-8') as f:
    f.write(spec)
print('updated spec:', os.path.getsize(spec_path))