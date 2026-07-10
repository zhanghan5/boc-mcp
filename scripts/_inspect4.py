# -*- coding: utf-8 -*-
import re, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
with open(r'D:\项目\boc-mcp\docs\_full_pdf_text.txt', 'r', encoding='utf-8') as f:
    text = f.read()
# List chapter/module headers (top-level sections). Look for lines with "管理", "查询", "相关", bold section markers.
# The PDF seems to have big section headers like "upmsapi", "服务树", "应用", "bocapi", 集群查询, 节点, ...
# Let's find lines that are just a short Chinese phrase (3-10 chars), not containing 接口/URL/参数/返回
pages = re.split(r'===== PAGE (\d+) =====', text)
sections_seen = []
for idx in range(1, len(pages), 2):
    pnum = int(pages[idx])
    content = pages[idx+1]
    for line in content.split('\n'):
        s = line.strip()
        # Skip page header/footer
        if not s or len(s) > 30 or len(s) < 2:
            continue
        if re.search(r'[a-zA-Z]{4,}', s):  # skip lines with English words
            # allow if short Chinese with english
            if re.match(r'^[\u4e00-\u9fff/（）\d\s]+$', s):
                pass
            else:
                continue
        if re.search(r'接口|URL|请求|返回|参数|属性|类型|示例|code|data|message|state|success|error|entity|exception|boolean|integer|string|object|array|====|currPage|pageSize', s):
            continue
        # Skip numbers only
        if re.match(r'^\d+$', s):
            continue
        sections_seen.append((pnum, s))
# Print unique sections in order
seen = set()
for p, s in sections_seen:
    key = s
    if key not in seen:
        seen.add(key)
        print(f'p{p:>3}: {s}')