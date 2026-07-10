# -*- coding: utf-8 -*-
import re, sys, io, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
with open(r'D:\项目\boc-mcp\docs\_full_pdf_text.txt', 'r', encoding='utf-8') as f:
    text = f.read()

# Find all section headings. The document has module names like:
# 应用, 集群查询, 分区, 网络分区, 节点监控, 租户, 镜像, 仓库, 应用, 服务, 版本, 容器, 实例, ConfigMap, Secret, ...
# Let's look at lines that appear to be module titles (short, on their own, before a list of APIs).

# First, let's find every "URL" occurrence and extract URL even if missing leading slash or split across lines.
# Join lines that look like URL continuations: if a line ends with partial URL and next starts with path segment, join.
lines = text.split('\n')
# Rejoin lines: lines that are continuations of URL (start with lowercase letters/numbers, no "请求方" etc.)
joined = []
i = 0
while i < len(lines):
    line = lines[i]
    joined.append(line)
    i += 1
re_text = '\n'.join(joined)

# Match URL with optional leading slash (PDF sometimes misses it due to formatting)
pat = re.compile(r'URL\s+(/?[a-zA-Z][a-zA-Z0-9_./{}-]*(?:\?[^\s]*)?)', re.MULTILINE)
apis = []
for m in pat.finditer(re_text):
    url = m.group(1).strip()
    if not url.startswith('/'):
        url = '/' + url
    # strip trailing comma, period
    url = url.rstrip(',，。；;、')
    # strip parenthetical notes
    url = re.sub(r'[（(][^)）]*[)）]\s*$', '', url)
    # find method - look around
    start = max(0, m.start()-200)
    end = min(len(re_text), m.end()+100)
    window = re_text[start:end]
    mm = re.search(r'请求方[式法]?\s*(GET|POST|PUT|DELETE|PATCH|get|post|put|delete|patch)', window)
    method = mm.group(1).upper() if mm else 'POST'  # default POST since most boc APIs are POST
    # description
    dm = re.search(r'接口描\s*述\s*([^\n|]+)', window)
    desc = dm.group(1).strip() if dm else ''
    desc = re.split(r'URL|请求方', desc)[0].strip()
    # section/module - look backward for heading (Chinese text on its own line, ending with management-ish words)
    pre_text = re_text[max(0,m.start()-1000):m.start()]
    # find last line that is a section heading - typically lines like "Pod 管理" or "1）查询 Pod"
    section = ''
    # try to find numbered title like "N）XXXX" before the URL
    sm = re.findall(r'\d+[）\)]\s*([^\n=|]{2,30})', pre_text)
    if sm:
        section = sm[-1].strip()
    apis.append({'method': method, 'url': url, 'desc': desc or section, 'section': section})

# dedupe by (method, url)
seen = {}
for a in apis:
    key = (a['method'], a['url'].split('?')[0])
    if key not in seen:
        seen[key] = a
    else:
        # prefer longer desc
        if len(a.get('desc','')) > len(seen[key].get('desc','')):
            seen[key] = a
unique = sorted(seen.values(), key=lambda x: x['url'])
print(f'Total API refs: {len(apis)}, unique: {len(unique)}')
for a in unique:
    print(f"{a['method']:6} {a['url']:70} {a['desc'][:50]}")

with open(r'D:\项目\boc-mcp\docs\_raw_apis.json', 'w', encoding='utf-8') as f:
    json.dump(unique, f, ensure_ascii=False, indent=2)