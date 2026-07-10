# -*- coding: utf-8 -*-
import re, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
with open(r'D:\项目\boc-mcp\docs\_full_pdf_text.txt', 'r', encoding='utf-8') as f:
    text = f.read()
# Find all module headers like "xxx 管理" and top-level sections
pages = re.split(r'===== PAGE (\d+) =====', text)
# Show pages around configmap/secret
for idx in range(1, len(pages), 2):
    pnum = int(pages[idx])
    content = pages[idx+1]
    if 'config' in content.lower() or 'ConfigMap' in content or 'secret' in content.lower() or 'Secret' in content:
        # find module-like Chinese headings containing 管理, ConfigMap, Secret
        for m in re.finditer(r'(?:^|\n)\s*([\u4e00-\u9fff\w]{2,20}(?:管理|ConfigMap|Secret|secret|configmap))', content):
            h = m.group(1).strip()
            if h in ('管理',):
                continue
            if 'Secret' in h or 'secret' in h or 'Config' in h or 'config' in h or '管理' in h:
                ctx = content[max(0,m.start()-50):m.end()+80].replace('\n', ' | ')
                print(f'p{pnum}: {ctx[:300]}')
                print()