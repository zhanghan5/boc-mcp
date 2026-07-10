# -*- coding: utf-8 -*-
import re, sys, io, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
with open(r'D:\项目\boc-mcp\docs\_full_pdf_text.txt', 'r', encoding='utf-8') as f:
    text = f.read()

# Split text into API blocks. Each block starts with a URL and ends just before the next URL or end of section.
url_pat = re.compile(r'URL\s+(/?[a-zA-Z][a-zA-Z0-9_./{}\-?=&#%]*)', re.MULTILINE)
matches = list(url_pat.finditer(text))
print(f'Found {len(matches)} URL matches')

apis = []
for i, m in enumerate(matches):
    url = m.group(1).strip()
    if not url.startswith('/'):
        url = '/' + url
    url = url.rstrip(',，。；;、')
    url = re.sub(r'[（(][^)）]*[)）]\s*$', '', url)
    block_end = matches[i+1].start() if i+1 < len(matches) else len(text)
    block = text[m.start():block_end]
    
    # Method
    mm = re.search(r'请求方[式法]?\s*(GET|POST|PUT|DELETE|PATCH|get|post|put|delete|patch)', block)
    method = mm.group(1).upper() if mm else 'POST'
    
    # Description: title before URL (in text before m within same block header)
    pre_block = text[max(0,m.start()-300):m.start()]
    # find "N）XXX" or "N)XXX" just before 接口描述
    title_m = list(re.finditer(r'\d+[）\)]\s*([^\n|=]{2,80})', pre_block))
    title = ''
    if title_m:
        # take closest one
        title = title_m[-1].group(1).strip()
    # cleanup title
    title = re.split(r'接口描|URL|请求方', title)[0].strip()
    
    # "接口描述 XXX" line
    dm = re.search(r'接口描\s*述\s*([^\n|]+)', block)
    desc = dm.group(1).strip() if dm else ''
    desc = re.split(r'URL|请求方', desc)[0].strip()
    
    # Extract parameters: lines after 参数名 with pattern "N(.N)*.name type location required description"
    # Typical param lines: "1.1.clusterName string query N 集群名称" or "1.id integer(int64) path Y 应用 id"
    # Due to PDF line breaks, params may be split across lines. Let's find param entries.
    params = []
    # Look for params section
    param_section = block
    # Find "参数名" header
    pm = re.search(r'参数名\s+数据类型\s+参数类型\s+是否必[填需]?\s+说明', param_section)
    if pm:
        param_text = param_section[pm.end():]
        # Stop at 返回 or 示例
        stop = re.search(r'返回(?:属性|属|值|示例)|示例\s*请求', param_text)
        if stop:
            param_text = param_text[:stop.start()]
        # Parameters are numbered like 1.xxx, 1.1.xxx, 2.xxx
        # Extract each param entry
        # param names end up broken like "clu|sterNam|e" due to PDF column wrapping. We'll do best-effort extraction.
        # Remove newlines between column fragments (heuristic: lines ending mid-word with next line starting with lowercase continue)
        param_lines = [l.strip() for l in param_text.split('\n') if l.strip()]
        # Find parameter entries by looking for pattern: number.name type ...
        # Collect all potential param starts
        full = ' '.join(param_lines)
        # Pattern: (digit(.digit)*).name_chars type_chars [query|path|body|form]? [Y|N] description
        p_iter = re.finditer(
            r'(\d+(?:\.\d+)*)\.([a-zA-Z_][a-zA-Z0-9_]*)\s+'
            r'((?:integer|string|boolean|object|array|number|int|long|float|double|varchar|byte|file)[\w(){}<>\[\],/\-]*)\s+'
            r'(query|path|body|form|header)?\s*'
            r'(Y|N|是|否)?\s*'
            r'([^0-9]*)',
            full
        )
        seen_p = set()
        for pm2 in p_iter:
            pname = pm2.group(2)
            if pname in seen_p:
                continue
            seen_p.add(pname)
            ptype = pm2.group(3).strip()
            ploc = pm2.group(4) or 'body'
            preq = pm2.group(5) or 'N'
            preq = 'Y' if preq in ('Y','是') else 'N'
            pdesc = pm2.group(6).strip()
            # Trim garbage
            pdesc = re.sub(r'\s+', ' ', pdesc)[:80]
            params.append({
                'name': pname,
                'type': ptype,
                'location': ploc,
                'required': preq == 'Y',
                'desc': pdesc
            })
    
    apis.append({
        'method': method,
        'url': url,
        'title': title or desc,
        'params': params
    })

# Dedupe
seen = set()
uniq = []
for a in apis:
    key = (a['method'], a['url'].split('?')[0])
    if key in seen:
        continue
    seen.add(key)
    uniq.append(a)

print(f'Unique APIs with params: {len(uniq)}')
for a in uniq:
    pnames = ', '.join(p['name'] for p in a['params'][:8])
    if len(a['params']) > 8:
        pnames += '...'
    print(f"  {a['method']:6} {a['url']:65} params=[{pnames}]")

with open(r'D:\项目\boc-mcp\docs\apis_with_params.json', 'w', encoding='utf-8') as f:
    json.dump(uniq, f, ensure_ascii=False, indent=2)
print('written')