# 博云容器云平台 MCP — 接口清单

> 来源：博云容器接口文档.pdf（2022-09 版）

## 13. 接口清单（基于博云容器接口文档.pdf）

> 文档共包含 **58 个 HTTP 接口**，均为**查询（GET/POST 只读）**操作；无创建/更新/删除/伸缩等写操作接口。

> 登录流程为 3 步：① `GET /upmstreeapi/bocPortal/getMenus` 获取 clientId → ② `POST /upmstreeapi/login`（typeConfigId=0 + userName + password + clientId）获取 code（在响应 data.code 字段）→ ③ `GET /upmstreeapi/accessToken?code=<code>` 获取 token + refreshToken + expiredTime。

> 后续请求通过 HTTP header 传递认证：`token`、`refreshToken`、`systemId`（systemId 默认 `"1"`，可通过 `BOC_SYSTEM_ID` 配置）。Token 仅放在 Header 中，Body 无需传 token。


### 13.1 auth（登录认证）（3 个工具）

| 工具名 | 方法 | 路径 | 说明 | 必填参数 |
|---|---|---|---|---|
| `boc_auth_get_client_id` | GET | `/upmstreeapi/bocPortal/getMenus` | 获取 clientId | — |
| `boc_auth_login` | POST | `/upmstreeapi/login` | 登录 | `typeConfigId`, `userName`, `password`, `clientId` |
| `boc_auth_get_token` | GET | `/upmstreeapi/accessToken` | 获取 token | — |

### 13.2 service_tree（服务树）（1 个工具）

| 工具名 | 方法 | 路径 | 说明 | 必填参数 |
|---|---|---|---|---|
| `boc_service_tree` | GET | `/service-tree` | 服务树右侧菜单，有数据权限控制 | — |

### 13.3 application（应用/项目）（2 个工具）

| 工具名 | 方法 | 路径 | 说明 | 必填参数 |
|---|---|---|---|---|
| `boc_app_get` | GET | `/applications/{id}` | 详情 | `id` |
| `boc_app_list` | GET | `/bocApplication/projects/list` | 列表 | — |

### 13.4 cluster（集群管理）（10 个工具）

| 工具名 | 方法 | 路径 | 说明 | 必填参数 |
|---|---|---|---|---|
| `boc_cluster_list` | POST | `/cluster/v2.3/list` | 查询集群 | — |
| `boc_cluster_list_all` | POST | `/cluster/v2.3/listAll` | 查询所有集群 | — |
| `boc_cluster_list_base_info` | POST | `/cluster/v3.0/listBaseInfo` | 查询集群基本信息 | `currPageNum`, `pageSize` |
| `boc_cluster_get_monitor` | GET | `/cluster/v3.0/listMonitorInfo/{clusterId}` | 查询集群监控信息 | — |
| `boc_cluster_get_state` | GET | `/platformCluster/v2.3/getClusterState/{clusterId}` | 获得集群状态 | — |
| `boc_cluster_list_nodes` | POST | `/platformCluster/v2.3/getClusterNodes` | 获取集群节点 | `currPageNum`, `pageSize`, `clusterId` |
| `boc_cluster_list_partitions` | POST | `/platformCluster/v2.3/getPartition` | 获取集群分区 | `clusterId`, `currPageNum`, `pageSize` |
| `boc_cluster_partition_resource` | GET | `/cluster/v2.3/clusterPartitionResource/{hostIds}` | 分区 CPU，MEM 查询 | `hostIds` |
| `boc_cluster_list_by_env` | GET | `/platformCluster/v2.3/getClusterByEnvId/{envId}` | 租户下集群 | — |
| `boc_partition_list_available` | POST | `/partition/v2.3/clusterPartition` | 查询当前租户下集群可用分区 | — |

### 13.5 partition（分区与节点）（9 个工具）

| 工具名 | 方法 | 路径 | 说明 | 必填参数 |
|---|---|---|---|---|
| `boc_partition_list` | POST | `/partition/v2.3/list` | 查询分区 | — |
| `boc_partition_get_default` | POST | `/partition/v3.3/getDefaultPartition/{clusterId}` | 查询集群默认分区 | — |
| `boc_partition_get_meta` | POST | `/partition/v2.3/getPartitionMeta` | 条件查询分区信息 | — |
| `boc_partition_list_default` | POST | `/partition/v2.3/listByKind` | 查询普通-默认分区 | — |
| `boc_partition_list_nodes` | POST | `/partition/v2.3/nodelist` | 分区节点列表 | — |
| `boc_partition_list_all_hosts` | POST | `/partition/v3.3/getAllHost` | 查询集群分区下所有节点 | — |
| `boc_partition_all_info` | POST | `/partition/v2.3/allInfo` | 租户集群下所有节点 | `clusterId`, `envId` |
| `boc_partition_detail` | POST | `/partition/v2.3/detailByCondition` | 获取分区实例信息 | — |
| `boc_version_get_yaml` | POST | `/map/v1.8/queryYaml` | 查询 YAML | `kind`, `name` |

### 13.6 network（网络分区）（3 个工具）

| 工具名 | 方法 | 路径 | 说明 | 必填参数 |
|---|---|---|---|---|
| `boc_network_list_by_name` | GET | `/partitionNetwork/getListByNetWorkName` | 获取网络分区 | `id`, `ips` |
| `boc_network_list_available` | GET | `/partitionNetwork/getUnUseredList` | 获取可用网络 | `clusterId` |
| `boc_network_list_by_env` | POST | `/partitionNetwork/v2.3/getNetworkListByEnvId` | 获取租户网络 | — |

### 13.7 workload（工作负载/服务/容器/实例）（12 个工具）

| 工具名 | 方法 | 路径 | 说明 | 必填参数 |
|---|---|---|---|---|
| `boc_workload_list_projects` | POST | `/query/v1.8/queryProject` | 查询应用 | — |
| `boc_workload_list_projects_and_apps` | POST | `/query/v1.8/queryProjectAndApplication` | 查询应用和服务 | `clusterId`, `envId`, `userId` |
| `boc_workload_list_applications` | POST | `/query/v1.8/queryApplication` | 查询服务或任务 | `currPageNum`, `envId`, `pageSize`, `projectId`, `resourceType` |
| `boc_workload_get_app_networks` | POST | `/query/v2.3/getNetworkByApplicationId` | 获取服务下网络信息 | `applicationId`, `clusterId` |
| `boc_workload_list_containers` | POST | `/query/v1.8/queryContainer` | 查询容器 | `currPageNum`, `envId`, `pageSize`, `podId`, `prometheusUrl`, `resourceType` |
| `boc_workload_list_pods` | POST | `/query/v1.8/queryPod` | 查询实例 | `applicationId`, `clusterId`, `currPageNum`, `envId`, `hostName`, `pageSize` ... |
| `boc_workload_list_kubectl_pods` | POST | `/query/v3.0/queryKubectlPods` | 查询 kubectlPod | `masterIp`, `resourceType` |
| `boc_workload_check_service` | POST | `/service/v2.3/checkService` | 查看内部负载是否存在 | `applicationId`, `clusterId`, `namespace` |
| `boc_workload_get_service_by_app` | POST | `/service/v2.3/getServiceByApplicationId` | 根据服务 id 获取内部负载 | `masterMap`, `projectId`, `projectName`, `platformType`, `applicationName` |
| `boc_workload_list_services_by_app` | POST | `/query/v2.3/queryServiceByApplicationId` | 获取服务下内部负载 | `masterIp`, `masterMap`, `platformType`, `projectId`, `projectName` |
| `boc_workload_list_services` | POST | `/service/v2.3/listServiceByPage` | 获分页获取内部负载 | `clusterId`, `namespace`, `pageSize` |
| `boc_workload_query_service` | POST | `/query/v1.8/queryService` | 内部负载查询 | — |

### 13.8 monitor（监控数据）（8 个工具）

| 工具名 | 方法 | 路径 | 说明 | 必填参数 |
|---|---|---|---|---|
| `boc_monitor_get_project_status` | POST | `/query/v1.8/queryProjectStatus` | 查询应用状态 | `projectId` |
| `boc_monitor_batch_project` | POST | `/query/v1.8/queryBatchProjectMonitor` | 查询应用监控数据 | — |
| `boc_monitor_batch_project_status` | POST | `/query/v1.8/queryBatchProjectStatus` | 查询服务状态 | — |
| `boc_monitor_get_app` | POST | `/query/v1.8/queryApplicationMonitor` | 查询服务或任务监控数据 | `applicationContainerName`, `applicationNamespace`, `applicationPodName`, `clusterId`, `id`, `kubernetesVersion` ... |
| `boc_monitor_batch_app` | POST | `/query/v1.8/queryBatchApplicationMonitor` | 查询服务监控数据 | — |
| `boc_monitor_get_pod` | POST | `/query/v1.8/queryPodMonitor` | 查询容器实例监控数据 | `applicationContainerName`, `applicationNamespace`, `applicationPodName`, `containerId`, `kubernetesVersion`, `prometheusUrl` ... |
| `boc_monitor_batch_container` | POST | `/query/v1.8/queryBatchContainerMonitor` | 查询容器监控数据 | — |
| `boc_monitor_batch_pod` | POST | `/query/v1.8/queryBatchPodMonitor` | 查询实例监控数据 | — |

### 13.9 version（版本/镜像/YAML）（6 个工具）

| 工具名 | 方法 | 路径 | 说明 | 必填参数 |
|---|---|---|---|---|
| `boc_version_list` | POST | `/query/v1.6/queryVersion` | 版本查询 | `appId`, `isTask` |
| `boc_version_get_id_by_name` | POST | `/query/v2.3/queryVersionIdByVersionName` | 查询版本 Id | `appId`, `clusterId`, `versionName` |
| `boc_version_list_image_groups` | POST | `/query/v1.8/queryVersionImageGroupByApplicationId` | 查询版本镜像组 | `appId`, `clusterId` |
| `boc_version_list_dispatched_clusters` | POST | `/query/v2.3/queryDispatchVersionByVersionName` | 获取版本下已发布的集群 | `applicationId` |
| `boc_version_list_undispatched_clusters` | POST | `/query/v2.3/queryUnDispatchVersionByVersionName` | 获取版本下未发布的集群 | `applicationId`, `projectId`, `versionName` |
| `boc_version_get_image_group` | POST | `/query/v2.3/queryImageGroup` | ImageGroup 查询 | `applicationName`, `projectId`, `resourceType` |

### 13.10 scan（安全扫描）（3 个工具）

| 工具名 | 方法 | 路径 | 说明 | 必填参数 |
|---|---|---|---|---|
| `boc_scan_list_strategies` | POST | `/strategy/v3.3/list` | 扫描策略列表<分页> | — |
| `boc_scan_get_report` | GET | `/report/v3.3/detail/{id}` | 扫描报告详情 | `id` |
| `boc_scan_list_reports` | POST | `/report/v3.3/list` | 扫描报告列表<分页> | — |

### 13.11 config_secret（Secret）（1 个工具）

| 工具名 | 方法 | 路径 | 说明 | 必填参数 |
|---|---|---|---|---|
| `boc_secret_list` | POST | `/secret/v2.3/list` | 查询 secret 列表 | — |

**合计：58 个 MCP 工具。**


