# -*- coding: utf-8 -*-
import sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

for path in [
    r'D:\项目\boc-mcp\docs\superpowers\specs\2026-07-08-boc-mcp-design.md',
]:
    with open(path, 'r', encoding='utf-8') as f:
        s = f.read()
    
    # 1. Add system_id to configuration table in §7.1
    s = s.replace(
        '| `mcp.port` | `BOC_MCP_PORT` | HTTP 监听端口 | `8000` |\n| `config_file`',
        '| `mcp.port` | `BOC_MCP_PORT` | HTTP 监听端口 | `8000` |\n| `system_id` | `BOC_SYSTEM_ID` | 请求头 systemId 值 | `"1"` |\n| `config_file`'
    )
    
    # 2. Fix §13.13: systemId default 1, token header only
    s = s.replace(
        '**后续业务请求 Header**（按接口文档示例）：\n- `token: <token>`\n- `refreshToken: <refreshToken>`\n- `systemId: <值待定>`（接口示例出现此 header，具体含义/来源待确认；初始版本可由配置项 `boc_system_id` 传入，缺省为空字符串）',
        '**后续业务请求 Header**：\n- `token: <token>`\n- `refreshToken: <refreshToken>`\n- `systemId: <system_id>`（默认 `"1"`，可通过 `BOC_SYSTEM_ID` 配置项覆盖）\n- Token 仅通过 Header 传递，请求 Body 中无需携带 token 字段'
    )
    
    # 3. Update §6: header injection note
    s = s.replace(
        '- 每次请求自动注入 3 个 header：`token`、`refreshToken`、`systemId`（值由配置或登录流程确定）',
        '- 每次请求自动注入 3 个 header：`token`、`refreshToken`、`systemId`（token/refreshToken 来自登录流程，systemId 默认 "1"，可配置）'
    )
    
    # 4. Update §13.14 pending items
    s = s.replace(
        '''**待确认项：**
1. `systemId` header 的值与来源（当前由配置项传入）
2. 是否存在 v2.x 最新接口文档（当前 PDF 为 2022-09 版本，部分接口路径版本为 v1.6~v3.3）
3. 是否有写操作接口（创建/伸缩/删除/重启等）未在本 PDF 中，后续拿到再扩展
4. refreshToken 是否存在刷新端点（文档未提供，当前按"重登"处理）''',
        '''**已确认项：**
1. `systemId` 默认值为 `"1"`，通过配置项 `BOC_SYSTEM_ID` 可覆盖
2. Token 仅通过 Header 传递，请求 Body 中无需携带 token 字段
3. 当前接口清单基于 2022-09 版 PDF（58 个只读接口），后续接口补充按相同模式扩展
4. refreshToken 无刷新端点，token 失效时走"重新登录 ②③ 步"流程'''
    )
    
    # 5. Update §2 auth to mention system_id default
    s = s.replace(
        '  - Lazy login：首次 API 请求时触发完整 3 步登录，缓存 token + refreshToken + clientId（clientId 可长期复用）',
        '  - Lazy login：首次 API 请求时触发完整 3 步登录，缓存 token + refreshToken + clientId（clientId 可长期复用），systemId 从配置读取（默认 "1"）'
    )
    
    with open(path, 'w', encoding='utf-8') as f:
        f.write(s)
    print('finalized:', path, os.path.getsize(path))

# Also update standalone api-inventory.md header defaults
inv_path = r'D:\项目\boc-mcp\docs\api-inventory.md'
with open(inv_path, 'r', encoding='utf-8') as f:
    s = f.read()
s = s.replace(
    '> 后续请求通过 HTTP header 传递认证：`token`、`refreshToken`、`systemId`。',
    '> 后续请求通过 HTTP header 传递认证：`token`、`refreshToken`、`systemId`（systemId 默认 `"1"`，可通过 `BOC_SYSTEM_ID` 配置）。Token 仅放在 Header 中，Body 无需传 token。'
)
with open(inv_path, 'w', encoding='utf-8') as f:
    f.write(s)
print('finalized inventory:', inv_path, os.path.getsize(inv_path))