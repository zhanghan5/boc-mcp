# -*- coding: utf-8 -*-
import sys, io, os, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

for path in [
    r'D:\项目\boc-mcp\docs\superpowers\specs\2026-07-08-boc-mcp-design.md',
    r'D:\项目\boc-mcp\docs\api-inventory.md',
]:
    with open(path, 'r', encoding='utf-8') as f:
        s = f.read()
    # fix accessToken row
    s = s.replace('| `boc_auth_get_token` | POST | `/upmstreeapi/accessToken` |',
                  '| `boc_auth_get_token` | GET | `/upmstreeapi/accessToken` |')
    with open(path, 'w', encoding='utf-8') as f:
        f.write(s)
    print('fixed', path, os.path.getsize(path))