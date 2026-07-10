# -*- coding: utf-8 -*-
import re, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
with open(r'D:\项目\boc-mcp\docs\_full_pdf_text.txt', 'r', encoding='utf-8') as f:
    text = f.read()
# Look at last 80 pages content - they seem to have configmap/secret sections
# Print lines that look like section headers (short Chinese lines without URL table words)
# Focus on pages 300+
pages = re.split(r'===== PAGE (\d+) =====', text)
# pages[0] is before first page marker, then alternating page_num, content
for idx in range(1, len(pages), 2):
    pnum = int(pages[idx])
    if pnum < 50:
        continue
    content = pages[idx+1]
    # Find lines that look like module/API titles
    # Pattern: number + ) + Chinese text
    titles = re.findall(r'(?:^|\|)\s*(\d+[）\)]\s*[^\n|=]{2,50})', content)
    if titles:
        # Only show first few per page
        print(f'--- PAGE {pnum} ---')
        for t in titles[:8]:
            print('  ', t.strip()[:80])