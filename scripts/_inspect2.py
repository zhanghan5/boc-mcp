# -*- coding: utf-8 -*-
import re, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
with open(r'D:\项目\boc-mcp\docs\_full_pdf_text.txt', 'r', encoding='utf-8') as f:
    text = f.read()
# Check for k8s-style APIs: paths with api/v1, apis/apps, namespaces, etc.
patterns = [
    r'/api/v1/\S+',
    r'/apis/\S+',
    r'/namespaces/\S+',
    r'/api/v\S+',
]
found = set()
for pat in patterns:
    for m in re.finditer(pat, text):
        s = m.group(0).rstrip(',，。；;)）"\\')
        if len(s) > 8:
            found.add(s)
print('k8s-style paths found:', len(found))
for s in sorted(found)[:100]:
    print(s)