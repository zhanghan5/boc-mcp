import json, os, textwrap

ROOT = r"D:\项目\boc-mcp"

MODULES = {
    "service_tree": {
        "desc_cn": "服务树",
        "tools": [
            {
                "tool_name": "boc_service_tree",
                "method": "get",
                "path": "/service-tree",
                "desc_zh": "查询服务树（按数据权限返回），可按父类型/父id/类型筛选。",
                "params": [
                    {"name":"p_type","py":"str | None = None","body":"pType","required":False,"desc":"父级类型"},
                    {"name":"pid","py":"int | None = None","body":"pid","required":False,"desc":"父节点 id"},
                    {"name":"type_","py":"str | None = None","body":"type","required":False,"desc":"节点类型"},
                ],
                "returns_list": True,
                "returns_paginated": False,
                "model_name": "ServiceTreeNode",
                "model_fields": [("has_children","bool | None",None),("id","int | None",None),("name","str",'""'),("pid","int | None",None),("ptype","str | None",None),("type","str | None",None)],
            },
        ],
    },
    "application": {
        "desc_cn": "应用/项目",
        "tools": [
            {"tool_name":"boc_app_get","method":"get","path":"/applications/{id}","desc_zh":"查询指定 id 的应用详情。","params":[{"name":"app_id","py":"int","body":"id","required":True,"desc":"应用 id","path_param":True}],"returns_list":False,"model_name":"ApplicationDetail"},
            {"tool_name":"boc_app_list","method":"get","path":"/bocApplication/projects/list","desc_zh":"分页查询应用（项目）列表，可按集群 id 和应用名过滤。","params":[{"name":"cluster_id","py":"str | None = None","body":"clusterId","required":False},{"name":"project_name","py":"str | None = None","body":"projectName","required":False},{"name":"page","py":"int = 1","body":"currPageNum","required":False},{"name":"page_size","py":"int = 20","body":"pageSize","required":False}],"returns_list":True,"returns_paginated":True,"model_name":"ApplicationSummary"},
        ],
        "default_model_fields": [("id","int | None",None),("name","str",'""')],
    },
    "partition": {
        "desc_cn": "分区与节点",
        "tools": [
            {"tool_name":"boc_partition_list","method":"post","path":"/partition/v2.3/list","desc_zh":"分页查询分区列表。","params":[{"name":"page","py":"int = 1","body":"currPageNum","required":False},{"name":"page_size","py":"int = 20","body":"pageSize","required":False}],"returns_paginated":True,"model_name":"Partition"},
            {"tool_name":"boc_partition_get_default","method":"post","path":"/partition/v3.3/getDefaultPartition/{cluster_id}","desc_zh":"查询集群默认分区。","params":[{"name":"cluster_id","py":"int","body":"cluster_id","required":True,"path_param":True}],"model_name":"Partition"},
            {"tool_name":"boc_partition_get_meta","method":"post","path":"/partition/v2.3/getPartitionMeta","desc_zh":"条件查询分区元信息。","params":[],"model_name":"PartitionMeta"},
            {"tool_name":"boc_partition_list_default","method":"post","path":"/partition/v2.3/listByKind","desc_zh":"查询普通-默认分区。","params":[],"returns_list":True,"model_name":"Partition"},
            {"tool_name":"boc_partition_list_nodes","method":"post","path":"/partition/v2.3/nodelist","desc_zh":"查询分区节点列表。","params":[],"returns_list":True,"model_name":"PartitionNode"},
            {"tool_name":"boc_partition_list_all_hosts","method":"post","path":"/partition/v3.3/getAllHost","desc_zh":"查询集群下所有节点。","params":[{"name":"cluster_id","py":"int | None = None","body":"clusterId","required":False}],"returns_list":True,"model_name":"HostNode"},
            {"tool_name":"boc_partition_all_info","method":"post","path":"/partition/v2.3/allInfo","desc_zh":"查询租户集群下所有节点信息（可过滤）。","params":[{"name":"cluster_id","py":"int | None = None","body":"clusterId","required":False},{"name":"env_id","py":"int | None = None","body":"envId","required":False},{"name":"host_ip","py":"str | None = None","body":"hostIp","required":False},{"name":"node_name","py":"str | None = None","body":"nodeName","required":False},{"name":"page","py":"int = 1","body":"currPageNum","required":False},{"name":"page_size","py":"int = 20","body":"pageSize","required":False}],"returns_paginated":True,"model_name":"HostNode"},
            {"tool_name":"boc_partition_detail","method":"post","path":"/partition/v2.3/detailByCondition","desc_zh":"根据条件获取分区实例详情。","params":[],"model_name":"PartitionDetail"},
            {"tool_name":"boc_version_get_yaml","method":"post","path":"/map/v1.8/queryYaml","desc_zh":"查询指定资源的 YAML 定义。","params":[{"name":"kind","py":"str","body":"kind","required":True},{"name":"name","py":"str","body":"name","required":True}],"returns_dict":True},
        ],
    },
    "network": {
        "desc_cn": "网络分区",
        "tools": [
            {"tool_name":"boc_network_list_by_name","method":"get","path":"/partitionNetwork/getListByNetWorkName","desc_zh":"按网络名获取网络分区。","params":[{"name":"id","py":"int | None = None","body":"id","required":False},{"name":"ips","py":"str | None = None","body":"ips","required":False}],"returns_list":True,"model_name":"NetworkPartition"},
            {"tool_name":"boc_network_list_available","method":"get","path":"/partitionNetwork/getUnUseredList","desc_zh":"获取可用网络列表。","params":[{"name":"cluster_id","py":"int | None = None","body":"clusterId","required":False}],"returns_list":True,"model_name":"NetworkPartition"},
            {"tool_name":"boc_network_list_by_env","method":"post","path":"/partitionNetwork/v2.3/getNetworkListByEnvId","desc_zh":"按租户 id 获取网络列表。","params":[{"name":"env_id","py":"int | None = None","body":"envId","required":False}],"returns_list":True,"model_name":"NetworkPartition"},
        ],
    },
    "scan": {
        "desc_cn": "安全扫描",
        "tools": [
            {"tool_name":"boc_scan_list_strategies","method":"post","path":"/strategy/v3.3/list","desc_zh":"分页查询安全扫描策略列表。","params":[{"name":"page","py":"int = 1","body":"currPageNum","required":False},{"name":"page_size","py":"int = 20","body":"pageSize","required":False}],"returns_paginated":True,"model_name":"ScanStrategy"},
            {"tool_name":"boc_scan_get_report","method":"get","path":"/report/v3.3/detail/{id}","desc_zh":"查询安全扫描报告详情。","params":[{"name":"report_id","py":"int","body":"id","required":True,"path_param":True}],"model_name":"ScanReport"},
            {"tool_name":"boc_scan_list_reports","method":"post","path":"/report/v3.3/list","desc_zh":"分页查询安全扫描报告列表。","params":[{"name":"page","py":"int = 1","body":"currPageNum","required":False},{"name":"page_size","py":"int = 20","body":"pageSize","required":False}],"returns_paginated":True,"model_name":"ScanReport"},
        ],
    },
}pass

