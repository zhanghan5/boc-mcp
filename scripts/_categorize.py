# -*- coding: utf-8 -*-
import json, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
with open(r'D:\项目\boc-mcp\docs\apis_with_params.json', 'r', encoding='utf-8') as f:
    apis = json.load(f)

# Categorize APIs into service modules
modules = {
    'auth': '认证登录',
    'service_tree': '服务树',
    'application': '应用（Project）',
    'cluster': '集群',
    'partition': '分区与节点',
    'network': '网络分区',
    'scan': '安全扫描',
    'version': '版本/镜像/YAML',
    'workload': '工作负载/服务/实例/容器',
    'monitor': '监控数据',
    'config_secret': 'Secret',
}

def classify(url):
    u = url.lower()
    if 'upmstreeapi' in u or 'bocportal' in u: return 'auth'
    if 'service-tree' in u: return 'service_tree'
    if '/applications' in u or 'bocapplication' in u: return 'application'
    if '/cluster' in u or 'platformcluster' in u: return 'cluster'
    if '/partitionnetwork' in u: return 'network'
    if '/partition' in u or '/map/' in u: return 'partition'
    if '/report' in u or '/strategy' in u: return 'scan'
    if '/secret' in u or '/configmap' in u: return 'config_secret'
    if 'queryyaml' in u or 'version' in u or 'imagegroup' in u or 'dispatchversion' in u or 'undispatchversion' in u or 'versionidbyversionname' in u or 'versionimagegroup' in u: return 'version'
    if 'monitor' in u or 'status' in u: return 'monitor'
    if '/service' in u or '/query' in u or 'queryservice' in u or 'checkservice' in u or 'kubectlpod' in u: return 'workload'
    return 'other'

from collections import defaultdict
by_module = defaultdict(list)
for a in apis:
    by_module[classify(a['url'])].append(a)

for mod, label in modules.items():
    items = by_module.get(mod, [])
    print(f'## {label} ({len(items)})')
    for a in items:
        p = ', '.join(x['name'] for x in a['params'][:10])
        if len(a['params'])>10: p += '...'
        print(f"  {a['method']:5} {a['url']}")
        print(f"      {a['title'][:50]}")
        if p: print(f"      params: {p}")
    print()