# -*- coding: utf-8 -*-
"""Parse extracted PDF text into structured API list."""
import re, json, sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

with open(r'D:\项目\boc-mcp\docs\_full_pdf_text.txt', 'r', encoding='utf-8') as f:
    text = f.read()

# Strategy: The document seems organized with "URL /path" + "请求方式 get/post/..."
# Extract each API block. Blocks are separated by page markers or by the next "URL" occurrence.
# First, find all (method, url, desc) triplets.

# Let me look at how APIs are introduced. Looking at sample:
# "接口描述 获取 clientId"
# "URL /upmstreeapi/bocPortal/getMenus"
# "请求方式 get"
# Then params table, then returns.

# We'll iterate line by line.
lines = text.split('\n')

apis = []
i = 0
while i < len(lines):
    line = lines[i].strip()
    # Look for URL line
    m = re.match(r'^URL\s+(/\S+)', line)
    if m:
        url = m.group(1).rstrip(',，。；;')
        # strip trailing parenthetical notes like "(此处 code 为上个接口返回的 code 值)"
        url = re.sub(r'[（(].*?[)）]', '', url).strip()
        # method: look at previous and next few lines for 请求方式
        method = 'GET'
        desc = ''
        # search window
        window_start = max(0, i-10)
        window_end = min(len(lines), i+5)
        window = '\n'.join(lines[window_start:window_end])
        mm = re.search(r'请求方[式式法]?\s*(GET|POST|PUT|DELETE|PATCH|get|post|put|delete|patch)', window)
        if mm:
            method = mm.group(1).upper()
        # description: look before URL for 接口描述 ...
        dm = re.search(r'接口描\s*述\s*(.+)', window)
        if dm:
            desc = dm.group(1).strip()
            # cut at "URL" or "请求方式"
            desc = re.split(r'URL|请求方', desc)[0].strip()
        # If desc is empty or too short, look at the header line (title repeated before 接口描述)
        if not desc or len(desc) < 2:
            # Take the line right before "接口描述" if it's a non-parameter line
            for back in range(i-1, window_start-1, -1):
                cand = lines[back].strip()
                if cand and not cand.startswith('=====') and '接口描述' not in cand and 'URL' not in cand and '请求方式' not in cand and not re.match(r'^\d+[）\)]', cand) and '参数名' not in cand and '返回' not in cand:
                    desc = cand
                    break
        apis.append({'method': method, 'url': url, 'desc': desc})
    i += 1

# Normalize and dedupe
def normalize_url(u):
    # remove query string for dedup
    return u.split('?')[0]

seen = set()
unique = []
for a in apis:
    key = (a['method'], normalize_url(a['url']))
    if key in seen:
        # if existing has empty desc and this has desc, update
        for u in unique:
            if (u['method'], normalize_url(u['url'])) == key and not u['desc'] and a['desc']:
                u['desc'] = a['desc']
                break
        continue
    seen.add(key)
    unique.append(a)

# Sort by URL
unique.sort(key=lambda x: (x['url'], x['method']))

print(f'Total API entries found: {len(apis)}, unique: {len(unique)}')
for a in unique:
    print(f"{a['method']:6} {a['url']:80} {a['desc'][:40]}")

out = r'D:\项目\boc-mcp\docs\_raw_apis.json'
with open(out, 'w', encoding='utf-8') as f:
    json.dump(unique, f, ensure_ascii=False, indent=2)
print('written to', out)