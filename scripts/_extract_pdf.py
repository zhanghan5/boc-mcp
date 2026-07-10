# -*- coding: utf-8 -*-
import pypdf, re, json, sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

folder = r'E:\WeChat Files\xwechat_files\zbingling123_944a\msg\file\2022-09'
# find pdf with "boc" or that's ~371 pages by opening the one named "博云容器接口文档.pdf"
import unicodedata
target_name = None
for f in os.listdir(folder):
    if 'boc' in f.lower() or '容器' in f or '接口' in f:
        # verify page count
        try:
            r = pypdf.PdfReader(os.path.join(folder, f))
            if len(r.pages) > 100:
                target_name = f
                break
        except:
            pass
if not target_name:
    # try exact known bytes
    for f in os.listdir(folder):
        if f.endswith('.pdf') and f != '207交叉编译交接文档(2).pdf':
            try:
                r = pypdf.PdfReader(os.path.join(folder, f))
                if len(r.pages) == 371:
                    target_name = f
                    break
            except:
                pass

print('Target PDF:', target_name)
pdf_path = os.path.join(folder, target_name)
r = pypdf.PdfReader(pdf_path)
print('pages:', len(r.pages))
pages = []
for i, p in enumerate(r.pages):
    try:
        t = p.extract_text() or ''
    except Exception as e:
        t = f'[EXTRACT ERROR: {e}]'
    pages.append(t)

full = '\n'.join(f'===== PAGE {i+1} =====\n{t}' for i,t in enumerate(pages))
out_txt = r'D:\项目\boc-mcp\docs\_full_pdf_text.txt'
os.makedirs(os.path.dirname(out_txt), exist_ok=True)
with open(out_txt, 'w', encoding='utf-8') as f:
    f.write(full)
print('total chars:', len(full))
print('written to', out_txt)