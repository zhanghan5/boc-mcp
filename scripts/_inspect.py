# -*- coding: utf-8 -*-
import re, sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
with open(r'D:\项目\boc-mcp\docs\_full_pdf_text.txt', 'r', encoding='utf-8') as f:
    text = f.read()
print('total length:', len(text))
# Count occurrences of "URL"
print('"URL" count:', len(re.findall(r'\bURL\b', text)))
# Count occurrences of "请求方式"
print('"请求方式" count:', len(re.findall(r'请求方式', text)))
print('"接口描述" count:', len(re.findall(r'接口描', text)))
# Show a few contexts around each URL
for i, m in enumerate(re.finditer(r'\bURL\b', text)):
    if i > 70:
        break
    s = max(0, m.start()-60)
    e = min(len(text), m.end()+180)
    snippet = text[s:e].replace('\n', ' | ')
    print(f'--- #{i+1} ---')
    print(snippet)