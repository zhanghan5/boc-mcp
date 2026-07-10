# -*- coding: utf-8 -*-
import re, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
with open(r'D:\项目\boc-mcp\docs\_full_pdf_text.txt', 'r', encoding='utf-8') as f:
    text = f.read()
pages = re.split(r'===== PAGE (\d+) =====', text)
# Print last 15 pages content (truncated) to see if there are configmap endpoints beyond secret
for idx in range(1, len(pages), 2):
    pnum = int(pages[idx])
    if pnum < 363:
        continue
    content = pages[idx+1]
    # truncate to first 2000 chars
    print(f'===== PAGE {pnum} =====')
    print(content[:1500])
    print()