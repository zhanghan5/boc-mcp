import pytest

from boc_mcp.config import AppConfig
from boc_mcp.server import create_app


@pytest.fixture(scope="module")
def app():
    return create_app(AppConfig(base_url="https://boc.test", username="u", password="p"))


EXPECTED = {
    "auth": ["boc_auth_status", "boc_auth_refresh"],
    "application": ["boc_app_get", "boc_app_list"],
    "cluster": [
        "boc_cluster_list",
        "boc_cluster_list_all",
        "boc_cluster_list_base_info",
        "boc_cluster_get_monitor",
        "boc_cluster_get_state",
        "boc_cluster_list_nodes",
        "boc_cluster_list_partitions",
        "boc_cluster_get_partition_resource",
        "boc_cluster_list_by_env",
        "boc_cluster_list_available_partitions",
    ],
    "network": [
        "boc_network_list_by_name",
        "boc_network_list_available",
        "boc_network_list_by_env",
    ],
    "scan": ["boc_scan_list_strategies", "boc_scan_get_report", "boc_scan_list_reports"],
    "service_tree": ["boc_service_tree"],
    "config_secret": ["boc_secret_list"],
    "partition": [
        "boc_partition_list",
        "boc_partition_get_default",
        "boc_partition_get_meta",
        "boc_partition_list_default",
        "boc_partition_list_nodes",
        "boc_partition_list_all_hosts",
        "boc_partition_all_info",
        "boc_partition_detail",
        "boc_partition_list_available",
    ],
    "monitor": [
        "boc_monitor_get_project_status",
        "boc_monitor_batch_project",
        "boc_monitor_batch_project_status",
        "boc_monitor_get_app",
        "boc_monitor_batch_app",
        "boc_monitor_get_pod",
        "boc_monitor_batch_container",
        "boc_monitor_batch_pod",
    ],
    "version": [
        "boc_version_list",
        "boc_version_get_id_by_name",
        "boc_version_list_image_groups",
        "boc_version_list_dispatched_clusters",
        "boc_version_list_undispatched_clusters",
        "boc_version_get_image_group",
        "boc_version_get_yaml",
    ],
    "workload": [
        "boc_workload_list_projects",
        "boc_workload_list_projects_and_apps",
        "boc_workload_list_applications",
        "boc_workload_get_app_networks",
        "boc_workload_list_containers",
        "boc_workload_list_pods",
        "boc_workload_list_kubectl_pods",
        "boc_workload_check_service",
        "boc_workload_get_service_by_app",
        "boc_workload_list_services_by_app",
        "boc_workload_list_services",
        "boc_workload_query_service",
    ],
}


@pytest.mark.parametrize("module,tools", [(m, t) for m, t in EXPECTED.items()])
def test_module_tools_registered(app, module, tools):
    registered = app._tool_manager._tools
    for t in tools:
        assert t in registered, f"{t} missing from module {module}"


def test_total_tool_count(app):
    expected = sum(len(t) for t in EXPECTED.values())
    assert len(app._tool_manager._tools) == expected, (
        f"expected {expected} tools, got {len(app._tool_manager._tools)}"
    )


def test_all_tool_descriptions_are_chinese(app):
    import re

    han = re.compile(r"[\u4e00-\u9fff]")
    for name, tool in app._tool_manager._tools.items():
        assert tool.description, f"{name} has no description"
        assert han.search(tool.description), f"{name} description must contain Chinese"
