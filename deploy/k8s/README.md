# boc-mcp Kubernetes 部署指南

本目录包含将 boc-mcp 部署到 Kubernetes 集群的清单。

## 文件说明

| 文件 | 说明 |
| --- | --- |
| `00-namespace.yaml` | 创建 `boc-mcp` 命名空间 |
| `01-config.yaml` | ConfigMap（非敏感配置）+ Secret（用户名/密码） |
| `02-deployment.yaml` | Deployment（2 副本、滚动升级、探针、安全上下文）+ Service（ClusterIP:8000） |
| `03-ingress.yaml` | 可选：Ingress（nginx，TLS） |
| `04-production.yaml` | 可选：PDB（最小 1 可用）、HPA（2~6 副本，CPU 70%/内存 75%）、NetworkPolicy |
| `kustomization.yaml` | kustomize 入口 |

## 前置条件

- Kubernetes ≥ 1.25
- 可访问镜像仓库（替换 `newName` 为你的仓库地址）
- 若使用 Ingress：集群安装 ingress-nginx
- 若使用 HPA：集群安装 metrics-server
- 若使用 NetworkPolicy：集群启用 CNI NetworkPolicy 支持（Calico/Cilium 等）

## 第一步：构建并推送镜像

```bash
# 本地构建
docker build -t registry.your-company.com/boc-mcp/boc-mcp:0.1.0 .
docker push registry.your-company.com/boc-mcp/boc-mcp:0.1.0
```

## 第二步：修改配置

### 2.1 修改镜像地址

编辑 `kustomization.yaml` 中的 `images.newName` 为实际镜像仓库地址。

### 2.2 填写博云平台地址

编辑 `01-config.yaml` 中 ConfigMap 的 `BOC_BASE_URL`，改为实际博云平台地址。

### 2.3 填写账号密码（强烈推荐使用外部 Secret 管理）

**方式 A：明文 Secret（仅测试用）**

直接编辑 `01-config.yaml` 的 Secret 中 `username`/`password`，再执行：

```bash
kubectl apply -k deploy/k8s
```

**方式 B：Sealed Secrets / External Secrets（生产推荐）**

删除 `01-config.yaml` 中的 Secret 部分，改用你的密钥管理方案：

- Sealed Secrets：`kubeseal` 加密后提交；
- External Secrets Operator：对接 Vault/AKV/ASM 等；
- 或直接 `kubectl create secret generic` 手动创建，不提交 Git：

```bash
kubectl create secret generic boc-mcp-credentials \
  --namespace boc-mcp \
  --from-literal=username=admin \
  --from-literal=password='your-password'
```

### 2.4（可选）启用 Ingress

取消 `kustomization.yaml` 中 `03-ingress.yaml` 的注释，编辑 `03-ingress.yaml` 中的 `hosts` 和 TLS secret。

### 2.5（可选）启用 PDB/HPA/NetworkPolicy

在 `kustomization.yaml` 的 `resources:` 列表中追加 `04-production.yaml`。NetworkPolicy 中 Egress 默认放通 443/80 出站到公网，若博云平台在内网可按实际 CIDR 收窄。

## 第三步：部署

```bash
# 用 kustomize 一键部署
kubectl apply -k deploy/k8s

# 查看状态
kubectl -n boc-mcp get pods
kubectl -n boc-mcp get svc
kubectl -n boc-mcp get ingress

# 查看日志
kubectl -n boc-mcp logs -l app.kubernetes.io/name=boc-mcp -f
```

## 第四步：验证

```bash
# 端口转发本地验证
kubectl -n boc-mcp port-forward svc/boc-mcp 8000:8000
curl http://127.0.0.1:8000/healthz
# 应返回 {"status":"ok"}

curl http://127.0.0.1:8000/healthz/ready
# 应返回 {"status":"ready",...}
```

配置 Codex/Claude Desktop 的 MCP 客户端时，把 URL 设为 Ingress 域名（例如 `https://boc-mcp.example.com/mcp`），或集群内 Service 地址 `http://boc-mcp.boc-mcp.svc.cluster.local:8000/mcp`。

## 第五步：MCP 客户端配置

Codex / Claude Desktop 配置（集群外通过 Ingress 访问）：

```json
{
  "mcpServers": {
    "boc-mcp": {
      "url": "https://boc-mcp.example.com/mcp"
    }
  }
}
```

集群内 Pod 直接通过 Service 访问时：

```json
{
  "mcpServers": {
    "boc-mcp": {
      "url": "http://boc-mcp.boc-mcp.svc.cluster.local:8000/mcp"
    }
  }
}
```

## 安全建议

- 生产环境务必用 SealedSecret/ExternalSecret 管理密码，不要把明文 Secret 提交到 Git。
- Deployment 已配置 `runAsNonRoot`、`readOnlyRootFilesystem`、`drop ALL capabilities`、`seccompProfile: RuntimeDefault`，镜像以 uid 10001 运行。
- NetworkPolicy 默认只允许 ingress-nginx 命名空间访问 8000，出站仅放通 DNS + 80/443，可按需调整。
- 启用 TLS（Ingress tls.secretName）保护 MCP HTTP 传输。

## 升级与回滚

```bash
# 滚动升级（修改 image tag 后）
kubectl -n boc-mcp set image deployment/boc-mcp boc-mcp=registry.your-company.com/boc-mcp/boc-mcp:0.2.0

# 查看升级状态
kubectl -n boc-mcp rollout status deploy/boc-mcp

# 回滚
kubectl -n boc-mcp rollout undo deploy/boc-mcp
```

## 常见问题

| 现象 | 排查 |
| --- | --- |
| Pod CrashLoopBackOff | `kubectl logs` 查日志，通常是 BOC_BASE_URL/账号密码缺失或错误 |
| `/healthz/ready` 503 | 博云平台不可达或 Token 登录失败；检查网络策略出站规则与 BOC_VERIFY_SSL |
| MCP 客户端连不上 | Ingress/Service 是否正常，`kubectl exec` 进 Pod 访问 127.0.0.1:8000/healthz |
| HPA 不生效 | 集群是否安装 metrics-server |