# boc-mcp ????

> ???0.1.0  
> ???Streamable HTTP?MCP ?? `http://<host>:8000/mcp`  
> ???MCP ?????????????????? `BOC_USERNAME`/`BOC_PASSWORD` ????????? Token?

## ????

- ?????? `boc_` ???? **58** ??????????
- ????????? `page`?? 1 ???? `page_size`??? 20??? 100??
- ?????????? `ListResult` ??????????
  ```json
  {"items": [...], "page": 1, "pageSize": 20, "total": 100, "pageCount": 5}
  ```
- ??????/???????????? / ???
- ???? MCP ???????????-32602 (????)?-32001 (???)?-32002 (???)?-32003 (???)?-32603 (??/????)?
- ?? ID ???`clusterId` ???`envId` ??/???`projectId` ???`applicationId` ??/???`namespace` ?????`hostId`/`masterIp` ???

## ????

### ?? (auth)

#### `boc_auth_status`
查询博云平台登录状态：是否已登录、登录用户、systemId、token 过期时间。

????

**??**?`object`

#### `boc_auth_refresh`
强制重新登录博云平台（当 token 异常或需要切换账号时使用）。

????

**??**?`string`

### ?? (application)

#### `boc_app_get`
根据应用 ID 查询单个应用的详细信息。

| ?? | ?? | ?? | ??? | ?? |
| --- | --- | --- | --- | --- |
| `app_id` | `int` | ? |  | |

**??**?`object`

#### `boc_app_list`
分页查询应用列表，可按集群 ID 和应用名称过滤。

| ?? | ?? | ?? | ??? | ?? |
| --- | --- | --- | --- | --- |
| `cluster_id` | `str ? None` | ? | None | |
| `project_name` | `str ? None` | ? | None | |
| `page` | `int` | ? | 1 | |
| `page_size` | `int` | ? | 20 | |

**??**?`object`

### ?? (cluster)

#### `boc_cluster_list`
查询博云平台集群列表，可按名称关键字过滤，支持分页。

| ?? | ?? | ?? | ??? | ?? |
| --- | --- | --- | --- | --- |
| `keyword` | `str ? None` | ? | None | |
| `page` | `int` | ? | 1 | |
| `page_size` | `int` | ? | 20 | |

**??**?`object`

#### `boc_cluster_list_all`
查询所有集群（不分页，返回简单列表）。

????

**??**?`array`

#### `boc_cluster_list_base_info`
查询集群基本信息，可按类型、名称、版本过滤，支持分页。

| ?? | ?? | ?? | ??? | ?? |
| --- | --- | --- | --- | --- |
| `cluster_kind` | `str ? None` | ? | None | |
| `cluster_name` | `str ? None` | ? | None | |
| `source_type` | `str ? None` | ? | None | |
| `version` | `str ? None` | ? | None | |
| `page` | `int` | ? | 1 | |
| `page_size` | `int` | ? | 20 | |

**??**?`object`

#### `boc_cluster_get_monitor`
查询指定集群的监控信息。

| ?? | ?? | ?? | ??? | ?? |
| --- | --- | --- | --- | --- |
| `cluster_id` | `int` | ? |  | |

**??**?`object`

#### `boc_cluster_get_state`
查询指定集群的运行状态。

| ?? | ?? | ?? | ??? | ?? |
| --- | --- | --- | --- | --- |
| `cluster_id` | `int` | ? |  | |

**??**?`object`

#### `boc_cluster_list_nodes`
分页查询指定集群下的节点列表。

| ?? | ?? | ?? | ??? | ?? |
| --- | --- | --- | --- | --- |
| `cluster_id` | `int` | ? |  | |
| `node_type` | `str ? None` | ? | None | |
| `page` | `int` | ? | 1 | |
| `page_size` | `int` | ? | 20 | |

**??**?`object`

#### `boc_cluster_list_partitions`
分页查询指定集群的分区列表。

| ?? | ?? | ?? | ??? | ?? |
| --- | --- | --- | --- | --- |
| `cluster_id` | `int` | ? |  | |
| `page` | `int` | ? | 1 | |
| `page_size` | `int` | ? | 20 | |

**??**?`object`

#### `boc_cluster_get_partition_resource`
查询指定 hostId 列表的分区 CPU/内存资源使用情况，hostIds 为逗号分隔的 id 字符串。

| ?? | ?? | ?? | ??? | ?? |
| --- | --- | --- | --- | --- |
| `host_ids` | `str` | ? |  | |

**??**?`object`

#### `boc_cluster_list_by_env`
查询指定租户（envId）下的集群列表。

| ?? | ?? | ?? | ??? | ?? |
| --- | --- | --- | --- | --- |
| `env_id` | `int` | ? |  | |

**??**?`array`

#### `boc_cluster_list_available_partitions`
查询当前租户下集群可用分区。

????

**??**?`object`

### ??? (service_tree)

#### `boc_service_tree`
查询服务树节点（有数据权限控制），可按父类型、父 id、节点类型筛选。返回树节点列表。

| ?? | ?? | ?? | ??? | ?? |
| --- | --- | --- | --- | --- |
| `p_type` | `str ? None` | ? | None | |
| `pid` | `int ? None` | ? | None | |
| `type_` | `str ? None` | ? | None | |

**??**?`list[dict]`

### ???? (scan)

#### `boc_scan_list_strategies`
分页查询安全扫描策略列表。

| ?? | ?? | ?? | ??? | ?? |
| --- | --- | --- | --- | --- |
| `page` | `int` | ? | 1 | |
| `page_size` | `int` | ? | 20 | |

**??**?`object`

#### `boc_scan_get_report`
查询指定安全扫描报告的详情。

| ?? | ?? | ?? | ??? | ?? |
| --- | --- | --- | --- | --- |
| `report_id` | `int` | ? |  | |

**??**?`object`

#### `boc_scan_list_reports`
分页查询安全扫描报告列表。

| ?? | ?? | ?? | ??? | ?? |
| --- | --- | --- | --- | --- |
| `page` | `int` | ? | 1 | |
| `page_size` | `int` | ? | 20 | |

**??**?`object`

### ??/?? (config_secret)

#### `boc_secret_list`
查询指定集群和命名空间下的 Secret 列表，支持按名称/类型过滤，分页返回。

| ?? | ?? | ?? | ??? | ?? |
| --- | --- | --- | --- | --- |
| `master_ip` | `str` | ? |  | |
| `namespace` | `str` | ? |  | |
| `master_port` | `int ? None` | ? | None | |
| `master_type` | `str` | ? | 'https' | |
| `master_version` | `str ? None` | ? | None | |
| `name` | `str ? None` | ? | None | |
| `env_id` | `int ? None` | ? | None | |
| `project_ids` | `str ? None` | ? | None | |
| `registry_id` | `int ? None` | ? | None | |
| `registry_type` | `str ? None` | ? | None | |
| `type_` | `str ? None` | ? | None | |
| `data` | `object` | ? | None | |
| `label` | `object` | ? | None | |
| `page` | `int` | ? | 1 | |
| `page_size` | `int` | ? | 20 | |

**??**?`object`

### ?? (network)

#### `boc_network_list_by_name`
按名称或 IP 查询网络分区列表。

| ?? | ?? | ?? | ??? | ?? |
| --- | --- | --- | --- | --- |
| `id` | `int ? None` | ? | None | |
| `ips` | `str ? None` | ? | None | |

**??**?`array`

#### `boc_network_available`  ?  ???

#### `boc_network_by_env`  ?  ???

### ?? (partition)

#### `boc_partition_list`
分页查询平台分区列表。

| ?? | ?? | ?? | ??? | ?? |
| --- | --- | --- | --- | --- |
| `page` | `int` | ? | 1 | |
| `page_size` | `int` | ? | 20 | |

**??**?`object`

#### `boc_partition_get_default`
查询指定集群的默认分区。

| ?? | ?? | ?? | ??? | ?? |
| --- | --- | --- | --- | --- |
| `cluster_id` | `int` | ? |  | |

**??**?`object`

#### `boc_partition_get_meta`
按任意过滤条件查询分区元数据，filters 为可选过滤字典。

| ?? | ?? | ?? | ??? | ?? |
| --- | --- | --- | --- | --- |
| `filters` | `object` | ? | None | |

**??**?`object`

#### `boc_partition_list_default`
查询默认分区列表（不分页）。

????

**??**?`array`

#### `boc_partition_list_nodes`
查询分区节点列表，可传入 filters 字典进行过滤。

| ?? | ?? | ?? | ??? | ?? |
| --- | --- | --- | --- | --- |
| `filters` | `object` | ? | None | |

**??**?`array`

#### `boc_partition_list_all_hosts`
查询所有主机节点列表，可按 clusterId 过滤。

| ?? | ?? | ?? | ??? | ?? |
| --- | --- | --- | --- | --- |
| `cluster_id` | `int ? None` | ? | None | |

**??**?`array`

#### `boc_partition_all_info`
分页查询主机全量信息，可按集群、租户、主机 IP、节点名称过滤。

| ?? | ?? | ?? | ??? | ?? |
| --- | --- | --- | --- | --- |
| `cluster_id` | `int ? None` | ? | None | |
| `env_id` | `int ? None` | ? | None | |
| `host_ip` | `str ? None` | ? | None | |
| `node_name` | `str ? None` | ? | None | |
| `page` | `int` | ? | 1 | |
| `page_size` | `int` | ? | 20 | |

**??**?`object`

#### `boc_partition_detail`
按条件查询分区详情，filters 为可选过滤字典。

| ?? | ?? | ?? | ??? | ?? |
| --- | --- | --- | --- | --- |
| `filters` | `object` | ? | None | |

**??**?`object`

#### `boc_partition_list_available`
分页查询当前租户可用的集群分区。

????

**??**?`object`

### ?? (monitor)

#### `boc_monitor_get_project_status`
查询单个应用（项目/服务）的实时监控状态，支持按 applicationId、clusterId、projectId 过滤，可通过 params 传入时间范围等扩展参数。

| ?? | ?? | ?? | ??? | ?? |
| --- | --- | --- | --- | --- |
| `application_id` | `int ? None` | ? | None | |
| `cluster_id` | `int ? None` | ? | None | |
| `project_id` | `int ? None` | ? | None | |
| `params` | `object` | ? | None | |

**??**?`object`

#### `boc_monitor_batch_project`
批量查询项目监控数据，params 传入集群、时间范围、指标等过滤条件。

| ?? | ?? | ?? | ??? | ?? |
| --- | --- | --- | --- | --- |
| `params` | `object` | ? | None | |

**??**?`object`

#### `boc_monitor_batch_project_status`
批量查询项目状态监控数据，params 传入集群、时间范围、指标等过滤条件。

| ?? | ?? | ?? | ??? | ?? |
| --- | --- | --- | --- | --- |
| `params` | `object` | ? | None | |

**??**?`object`

#### `boc_monitor_get_app`
查询单个应用（服务）的监控数据，支持按 applicationId、clusterId 过滤，可通过 params 传入时间范围等扩展参数。

| ?? | ?? | ?? | ??? | ?? |
| --- | --- | --- | --- | --- |
| `application_id` | `int ? None` | ? | None | |
| `cluster_id` | `int ? None` | ? | None | |
| `params` | `object` | ? | None | |

**??**?`object`

#### `boc_monitor_batch_app`
批量查询应用监控数据，params 传入集群、时间范围、指标等过滤条件。

| ?? | ?? | ?? | ??? | ?? |
| --- | --- | --- | --- | --- |
| `params` | `object` | ? | None | |

**??**?`object`

#### `boc_monitor_get_pod`
查询 Pod 监控数据，支持按 applicationId、clusterId 过滤，可通过 params 传入时间范围等扩展参数。

| ?? | ?? | ?? | ??? | ?? |
| --- | --- | --- | --- | --- |
| `application_id` | `int ? None` | ? | None | |
| `cluster_id` | `int ? None` | ? | None | |
| `params` | `object` | ? | None | |

**??**?`object`

#### `boc_monitor_batch_container`
批量查询容器监控数据，params 传入集群、时间范围、指标等过滤条件。

| ?? | ?? | ?? | ??? | ?? |
| --- | --- | --- | --- | --- |
| `params` | `object` | ? | None | |

**??**?`object`

#### `boc_monitor_batch_pod`
批量查询 Pod 监控数据，params 传入集群、时间范围、指标等过滤条件。

| ?? | ?? | ?? | ??? | ?? |
| --- | --- | --- | --- | --- |
| `params` | `object` | ? | None | |

**??**?`object`

### ??/?? (version)

#### `boc_version_list`
查询版本列表，支持按应用/项目/集群/租户过滤。

| ?? | ?? | ?? | ??? | ?? |
| --- | --- | --- | --- | --- |
| `app_id` | `int ? None` | ? | None | |
| `project_id` | `int ? None` | ? | None | |
| `cluster_id` | `int ? None` | ? | None | |
| `env_id` | `int ? None` | ? | None | |
| `is_task` | `bool ? None` | ? | None | |
| `version_id` | `int ? None` | ? | None | |
| `page_size` | `int` | ? | 20 | |

**??**?`object`

#### `boc_version_get_id_by_name`
根据版本名称查询版本 id。

| ?? | ?? | ?? | ??? | ?? |
| --- | --- | --- | --- | --- |
| `version_name` | `str` | ? |  | |
| `app_id` | `int ? None` | ? | None | |
| `application_id` | `int ? None` | ? | None | |
| `project_id` | `int ? None` | ? | None | |
| `cluster_id` | `int ? None` | ? | None | |
| `current_version_id` | `int ? None` | ? | None | |
| `env_id` | `int ? None` | ? | None | |
| `is_task` | `bool ? None` | ? | None | |
| `page` | `int` | ? | 1 | |
| `page_size` | `int` | ? | 20 | |

**??**?`object`

#### `boc_version_list_image_groups`
查询版本的镜像组列表。

| ?? | ?? | ?? | ??? | ?? |
| --- | --- | --- | --- | --- |
| `app_id` | `int ? None` | ? | None | |
| `application_id` | `int ? None` | ? | None | |
| `project_id` | `int ? None` | ? | None | |
| `cluster_id` | `int ? None` | ? | None | |
| `current_version_id` | `int ? None` | ? | None | |
| `env_id` | `int ? None` | ? | None | |
| `is_task` | `bool ? None` | ? | None | |
| `page` | `int` | ? | 1 | |
| `page_size` | `int` | ? | 20 | |

**??**?`object`

#### `boc_version_list_dispatched_clusters`
查询指定版本下已发布的集群列表。

| ?? | ?? | ?? | ??? | ?? |
| --- | --- | --- | --- | --- |
| `application_id` | `int` | ? |  | |
| `cluster_id` | `int ? None` | ? | None | |
| `version_name` | `str ? None` | ? | None | |

**??**?`array`

#### `boc_version_list_undispatched_clusters`
查询指定版本下未发布的集群列表，分页返回。

| ?? | ?? | ?? | ??? | ?? |
| --- | --- | --- | --- | --- |
| `version_name` | `str` | ? |  | |
| `app_id` | `int ? None` | ? | None | |
| `application_id` | `int ? None` | ? | None | |
| `project_id` | `int ? None` | ? | None | |
| `cluster_id` | `int ? None` | ? | None | |
| `current_version_id` | `int ? None` | ? | None | |
| `env_id` | `int ? None` | ? | None | |
| `is_task` | `bool ? None` | ? | None | |
| `page` | `int` | ? | 1 | |
| `page_size` | `int` | ? | 20 | |

**??**?`object`

#### `boc_version_get_image_group`
查询镜像组信息。

| ?? | ?? | ?? | ??? | ?? |
| --- | --- | --- | --- | --- |
| `application_name` | `str ? None` | ? | None | |
| `project_id` | `int ? None` | ? | None | |
| `app_id` | `int ? None` | ? | None | |
| `resource_type` | `str` | ? | 'queryImageGroup' | |

**??**?`array`

#### `boc_version_get_yaml`
查询指定 Kubernetes 资源（kind/name）的 YAML 定义。

| ?? | ?? | ?? | ??? | ?? |
| --- | --- | --- | --- | --- |
| `kind` | `str` | ? |  | |
| `name` | `str` | ? |  | |

**??**?`object`

### ???? (workload)

#### `boc_workload_project_list`  ?  ???

#### `boc_workload_app_list`  ?  ???

#### `boc_workload_application_list`  ?  ???

#### `boc_workload_service_network`  ?  ???

#### `boc_workload_container_list`  ?  ???

#### `boc_workload_list_pods`
分页查询实例（Pod）列表，支持按集群、租户、服务、命名空间、容器、主机过滤。

| ?? | ?? | ?? | ??? | ?? |
| --- | --- | --- | --- | --- |
| `cluster_id` | `int ? None` | ? | None | |
| `env_id` | `int ? None` | ? | None | |
| `application_id` | `int ? None` | ? | None | |
| `namespace` | `str ? None` | ? | None | |
| `container_name` | `str ? None` | ? | None | |
| `host_name` | `str ? None` | ? | None | |
| `is_task` | `bool ? None` | ? | None | |
| `page` | `int` | ? | 1 | |
| `page_size` | `int` | ? | 20 | |

**??**?`object`

#### `boc_workload_list_kubectl_pods`
查询 kubectl 可访问的 Pod 列表（需要 master_ip 和资源类型）。

| ?? | ?? | ?? | ??? | ?? |
| --- | --- | --- | --- | --- |
| `master_ip` | `str` | ? |  | |
| `resource_type` | `str` | ? |  | |
| `page` | `int` | ? | 1 | |
| `page_size` | `int` | ? | 20 | |

**??**?`object`

#### `boc_workload_check_service`
检查指定命名空间下内部服务是否存在。

| ?? | ?? | ?? | ??? | ?? |
| --- | --- | --- | --- | --- |
| `application_id` | `int` | ? |  | |
| `cluster_id` | `int` | ? |  | |
| `namespace` | `str` | ? |  | |
| `name` | `str ? None` | ? | None | |

**??**?`object`

#### `boc_workload_get_service_by_app`
根据服务 id 获取内部负载详情。

| ?? | ?? | ?? | ??? | ?? |
| --- | --- | --- | --- | --- |
| `application_name` | `str` | ? |  | |
| `project_id` | `int` | ? |  | |
| `project_name` | `str` | ? |  | |
| `platform_type` | `str` | ? | 'kubernetes' | |
| `master_map` | `object` | ? | None | |

**??**?`array`

#### `boc_workload_list_services_by_app`
获取指定服务下的内部负载列表。

| ?? | ?? | ?? | ??? | ?? |
| --- | --- | --- | --- | --- |
| `application_name` | `str` | ? |  | |
| `project_id` | `int` | ? |  | |
| `project_name` | `str` | ? |  | |
| `master_ip` | `str` | ? |  | |
| `platform_type` | `str` | ? | 'kubernetes' | |
| `service_name` | `str ? None` | ? | None | |
| `master_map` | `object` | ? | None | |

**??**?`array`

#### `boc_workload_list_services`
分页查询内部负载（Service）列表，支持按集群、租户、命名空间、名称过滤。

| ?? | ?? | ?? | ??? | ?? |
| --- | --- | --- | --- | --- |
| `cluster_id` | `int ? None` | ? | None | |
| `env_id` | `int ? None` | ? | None | |
| `namespace` | `str ? None` | ? | None | |
| `name` | `str ? None` | ? | None | |
| `page` | `int` | ? | 1 | |
| `page_size` | `int` | ? | 20 | |

**??**?`object`

#### `boc_workload_query_service`
查询内部负载详情（通用 Service 查询接口）。

| ?? | ?? | ?? | ??? | ?? |
| --- | --- | --- | --- | --- |
| `application_name` | `str` | ? |  | |
| `master_ip` | `str` | ? |  | |
| `project_name` | `str` | ? |  | |
| `platform_type` | `str` | ? | 'kubernetes' | |
| `service_name` | `str ? None` | ? | None | |
| `master_map` | `object` | ? | None | |
| `project_id` | `int ? None` | ? | None | |

**??**?`object`
