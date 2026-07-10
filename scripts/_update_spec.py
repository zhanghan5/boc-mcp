# -*- coding: utf-8 -*-
"""Rebuild the spec file with corrected modules + API inventory (§13)."""
import json, io, sys, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def _tool_name(url):
    u = url.split('?')[0].rstrip('/')
    segs = [s for s in u.split('/') if s and not s.startswith('{')]
    out = []
    for s in segs:
        if s.startswith('v') and len(s) <= 5 and s[1:].replace('.','').isdigit():
            continue
        out.append(s)
    name = '_'.join(out).replace('-','_')
    return 'boc_' + name
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
    if 'queryyaml' in u or 'version' in u or 'imagegroup' in u or 'dispatchversion' in u or 'undispatchversion' in u or 'versionidbyversionname' in u or 'versionimagegroup' in u: return 'version'
    if 'monitor' in u or '/query/v1.8/queryprojectstatus' in u or 'batchprojectstatus' in u: return 'monitor'
    return 'workload'

from collections import OrderedDict
MODULES = OrderedDict([
    ('auth',            'auth（登录认证）'),
    ('service_tree',    'service_tree（服务树）'),
    ('application',     'application（应用/项目）'),
    ('cluster',         'cluster（集群管理）'),
    ('partition',       'partition（分区与节点）'),
    ('network',         'network（网络分区）'),
    ('workload',        'workload（工作负载/服务/容器/实例）'),
    ('monitor',         'monitor（监控数据）'),
    ('version',         'version（版本/镜像/YAML）'),
    ('scan',            'scan（安全扫描）'),
    ('config_secret',   'config_secret（Secret 查询）'),
])

by_mod = {k: [] for k in MODULES}
for a in apis:
    m = classify(a['url'])
    by_mod.setdefault(m, []).append(a)

# Build the API inventory markdown
lines = []
lines.append('## 13. 接口清单（基于博云容器接口文档.pdf）\n')
lines.append('> 文档共包含 58 个 HTTP 接口，均为**查询（GET/POST 只读）**操作；无创建/更新/删除/伸缩等写操作。\n')
lines.append('> 登录流程为 3 步：① `GET /upmstreeapi/bocPortal/getMenus` 获取 clientId → ② `POST /upmstreeapi/login`（用户名+密码+clientId）获取 code → ③ `GET /upmstreeapi/accessToken?code=...` 获取 token + refreshToken。\n')
lines.append('> 后续请求通过 HTTP header 传递认证信息（header 名以接口文档为准：`token`、`refreshToken`、`systemId`）。\n')
total = 0
for mod_key, mod_label in MODULES.items():
    items = by_mod.get(mod_key, [])
    if not items:
        continue
    total += len(items)
    lines.append(f'\n### 13.{list(MODULES).index(mod_key)+1} {mod_label}（{len(items)} 个接口）\n')
    lines.append('| 工具名（暂定） | 方法 | 路径 | 说明 | 关键参数 |')
    lines.append('|---|---|---|---|---|')
    for a in items:
        method = a['method']
        url = a['url']
        title = (a.get('title') or '').replace('|','/').replace('\n',' ').strip()
        # generate tool name
        tool = _tool_name(url)
        # key params: required first, then up to 6 total
        req_p = [p['name'] for p in a['params'] if p['required']]
        opt_p = [p['name'] for p in a['params'] if not p['required']]
        shown = req_p + opt_p
        key_p = ', '.join(shown[:8])
        if len(shown) > 8:
            key_p += ', ...'
        if req_p:
            key_p = '**' + ', '.join(req_p[:5]) + '**' + (', ...' if len(req_p)>5 else '')
            if opt_p:
                key_p += '; ' + ', '.join(opt_p[:3])
                if len(opt_p) > 3: key_p += ', ...'
        lines.append(f'| `{tool}` | {method} | `{url}` | {title} | {key_p} |')
lines.append(f'\n**合计：{total} 个 MCP 工具。**\n')

lines.append('''
### 13.12 工具命名约定

- 所有工具加 `boc_` 前缀
- 命名格式：`boc_<module>_<action>`，例如：
  - `boc_cluster_list`、`boc_cluster_get_nodes`
  - `boc_workload_query_pods`、`boc_workload_query_containers`
  - `boc_monitor_query_pod`、`boc_monitor_batch_app`
- 分页类工具统一保留 `page`、`page_size` 参数，`page_size` 默认 20、最大 100
- 路径参数（如 `{clusterId}`、`{id}`、`{envId}`）作为工具必填参数
- POST body 参数作为工具可选/必填参数映射（按接口文档"是否必填"）

### 13.13 登录流程与 Token 管理（修订）

根据接口文档，博云平台登录分 3 步，与原设计 §2 不同，修订为：

1. **获取 clientId**：`GET /upmstreeapi/bocPortal/getMenus` → 返回 `data.redirectLoginUrl` 中 query 参数包含 `clientId`
2. **登录**：`POST /upmstreeapi/login`，body `{typeConfigId: 0, userName, password, clientId}` → 返回 `data.code`（注意：此处 `code` 字段在响应的 `data` 对象中，不是顶层 code）
3. **获取 token**：`GET /upmstreeapi/accessToken?code=<data.code>` → 返回 `data.token`、`data.refreshToken`、`data.expiredTime`

**后续请求 Header**：
- `token: <token>`
- `refreshToken: <refreshToken>`
- `systemId: <string>`（按接口文档示例，具体值待确认）

**Token 失效处理**：
- 当任意 API 返回 `state: "error"` 且 `message` 指示 token 失效时，重新走步骤 2→3（不需要重新获取 clientId，clientId 可长期复用）
- 不做提前刷新；401/error → invalidate → 重新登录一次 → 重试原请求

config_secret 模块目前文档只覆盖了 Secret 列表查询（1 个接口）；ConfigMap 查询和写操作接口若后续提供再行补充。
''')

inventory_md = '\n'.join(lines)

# Now rebuild the entire spec file, replacing §12 and adding §13
spec_path = r'D:\项目\boc-mcp\docs\superpowers\specs\2026-07-08-boc-mcp-design.md'
with open(spec_path, 'r', encoding='utf-8') as f:
    spec = f.read()

# Update §4 directory structure to match actual modules
old_tree_endmarker = '## 5. 工具命名与注册约定'
# Trim to drop old §12 and replace
# Find "## 12" 
idx12 = spec.find('## 12.')
if idx12 > 0:
    spec = spec[:idx12]

# Replace service modules listing in §4 to match actual interface modules
spec = spec.replace(
    '│       ├── cluster/           # 集群/节点\n'
    '│       ├── workload/          # Deployment/Pod/Service/StatefulSet/DaemonSet/Job/CronJob\n'
    '│       ├── namespace/         # Namespace/租户/项目\n'
    '│       ├── image/             # 镜像仓库/镜像\n'
    '│       ├── ops/               # 日志/事件/监控/告警\n'
    '│       ├── cicd/              # 流水线/构建\n'
    '│       └── config_secret/     # ConfigMap/Secret',
    '│       ├── auth/              # 登录流程（clientId/login/accessToken）\n'
    '│       ├── service_tree/      # 服务树\n'
    '│       ├── application/       # 应用（Project）详情/列表\n'
    '│       ├── cluster/           # 集群查询/状态/节点/分区/监控\n'
    '│       ├── partition/         # 分区/节点/YAML\n'
    '│       ├── network/           # 网络分区\n'
    '│       ├── workload/          # 服务/容器/实例/内部负载/kubectlPod\n'
    '│       ├── monitor/           # 监控数据（应用/服务/容器/实例/状态）\n'
    '│       ├── version/           # 版本/镜像组/发布集群\n'
    '│       ├── scan/              # 安全扫描策略/报告\n'
    '│       └── config_secret/     # Secret 查询'
)

# Update §2 auth (3-step login)
spec = spec.replace(
    '- 登录机制：用户名 + 密码登录换取 token（具体登录端点、token 字段名、token header 名以接口文档为准）\n'
    '- Token 特性：会过期，无 refresh 接口，平台自带过期判断\n'
    '- 管理策略：\n'
    '  - Lazy login：首次 API 请求时触发登录，缓存 token 至内存\n'
    '  - 自动重试：请求返回 401 时，清空缓存 → 重新登录 → 用新 token 重试原请求一次（仅一次，防止死循环）\n'
    '  - 并发保护：使用 asyncio.Lock 保证多个协程同时触发失效时只发一次登录请求\n'
    '  - 不做提前刷新（平台无 refresh API）',
    '- 登录机制：3 步登录——①获取 clientId → ②用户名+密码+clientId 登录换 code → ③code 换 token/refreshToken（详见 §13.13）\n'
    '- Token 特性：会过期，接口返回 `expiredTime`；有 refreshToken 但文档中未提供 refresh 端点\n'
    '- 管理策略：\n'
    '  - Lazy login：首次 API 请求时触发完整 3 步登录，缓存 token + refreshToken + clientId（clientId 可长期复用）\n'
    '  - 自动重试：请求返回 token 失效（401 或 state=error 提示登录失效）时，重新走步骤 ②③ 换新 token → 重试原请求一次\n'
    '  - 并发保护：使用 asyncio.Lock 保证多个协程同时触发失效时只发一次登录请求\n'
    '  - 不做提前刷新'
)

# Update §5 tools header note
spec = spec.replace(
    '- MCP `instructions`（系统提示）描述博云平台基本概念、工具使用建议、常见工作流指引',
    '- MCP `instructions`（系统提示）描述博云平台基本概念、工具使用建议、常见工作流指引\n- 所有工具均为只读查询（接口文档未提供写操作），工具描述里明确告知 LLM 本 MCP 仅支持查询'
)

# Update §6 header injection
spec = spec.replace(
    '- 每次请求自动注入 token header（具体 header 名以接口文档为准）',
    '- 每次请求自动注入 3 个 header：`token`、`refreshToken`、`systemId`（值由配置或登录流程确定）'
)

# Append §12 (updated) and §13
spec += '''
## 12. 下一步前置依赖

- 接口文档已解析完成（见 §13），所有 58 个接口已按模块整理为工具清单
- 待确认：
  - `systemId` header 的值如何获取/配置
  - refreshToken 是否存在刷新端点（文档未提供，按"重登"处理）
  - 后续若有写操作接口（创建/伸缩/删除等）补充，按相同模式扩展 service 子包
- 架构层和基础设施层（auth 三步登录/client/config/logging/middleware/health/server 入口/CI/Dockerfile）可直接开工

'''
spec += inventory_md

with open(spec_path, 'w', encoding='utf-8') as f:
    f.write(spec)
print('spec updated, size:', os.path.getsize(spec_path))

# Helper

def _tool_name(url):
    u = url.split('?')[0].rstrip('/')
    segs = [s for s in u.split('/') if s and not s.startswith('{')]
    # skip version/prefix
    out = []
    for s in segs:
        # drop version like v1.8, v2.3
        if s.startswith('v') and len(s) <= 5 and s[1:].replace('.','').isdigit():
            continue
        out.append(s)
    name = '_'.join(out).replace('-','_')
    # collapse common prefixes
    return 'boc_' + name
