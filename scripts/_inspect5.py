# -*- coding: utf-8 -*-
import re, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
with open(r'D:\项目\boc-mcp\docs\_full_pdf_text.txt', 'r', encoding='utf-8') as f:
    text = f.read()
pages = re.split(r'===== PAGE (\d+) =====', text)
# For each page, find numbered titles (N）XXX) to see module structure in last 1/3 of doc (ConfigMap/Secret/扫描 etc.)
all_titles = []
for idx in range(1, len(pages), 2):
    pnum = int(pages[idx])
    content = pages[idx+1]
    # find lines like "数字）xxxx" at top-level (API names)
    for m in re.finditer(r'(?:^|\n)\s*(\d+[）\)]\s*[^\n]{2,80})', content):
        title = m.group(1).strip()
        # filter out field names (like 6.57.1.xxx)
        if re.match(r'^\d+[）\)]', title) and not re.match(r'^\d+\.\d+', title):
            # Clean up weird fragments
            clean = title.split('|')[0].strip()
            if not re.search(r'^[\d）\)\s]+$', clean) and len(clean) > 4:
                all_titles.append((pnum, clean))

# Group by page, dedupe consecutive
last = None
for p, t in all_titles:
    if t == last:
        continue
    last = t
    print(f'p{p:>3}: {t[:80]}')