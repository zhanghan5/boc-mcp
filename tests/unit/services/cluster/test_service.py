import pytest
from boc_mcp.services.cluster.service import ClusterService
from boc_mcp.models.common import ListResult
from boc_mcp.services.cluster.models import ClusterSummary, ClusterNode, ClusterPartition

class FakeClient:
    def __init__(self): self.calls=[]; self.payloads={}
    def seed(self, key, resp): self.payloads[key] = resp
    async def get(self, path, *, params=None):
        self.calls.append(("get",path,params))
        for k,v in self.payloads.items():
            if k in path: return v
        return {}
    async def post(self, path, *, json=None):
        self.calls.append(("post",path,json))
        for k,v in self.payloads.items():
            if k in path: return v
        return {"rows":[],"totalCount":0,"currPageNum":1,"pageSize":20,"pageCount":0}

@pytest.mark.asyncio
async def test_list_clusters():
    c = FakeClient()
    c.seed("/cluster/v2.3/list", {"rows":[{"id":1,"name":"c1"},{"id":2,"name":"c2"}],
        "totalCount":2,"currPageNum":1,"pageSize":20,"pageCount":1})
    svc = ClusterService(c)
    r = await svc.list_clusters()
    assert r.total == 2
    assert len(r.items) == 2
    assert isinstance(r.items[0], ClusterSummary)

@pytest.mark.asyncio
async def test_list_all_clusters():
    c = FakeClient()
    c.seed("/cluster/v2.3/listAll", {"data":[{"id":1,"name":"c1"}]})
    svc = ClusterService(c)
    r = await svc.list_all_clusters()
    assert isinstance(r, list) and len(r) == 1

@pytest.mark.asyncio
async def test_list_base_info():
    c = FakeClient()
    c.seed("/cluster/v3.0/listBaseInfo", {"rows":[{"id":1}],"totalCount":1})
    svc = ClusterService(c)
    r = await svc.list_base_info()
    assert r.total == 1

@pytest.mark.asyncio
async def test_get_monitor_info():
    c = FakeClient()
    c.seed("/cluster/v3.0/listMonitorInfo/42", {"data":{"cpu":0.5}})
    svc = ClusterService(c)
    r = await svc.get_monitor_info(42)
    assert r["cpu"] == 0.5

@pytest.mark.asyncio
async def test_get_cluster_state():
    c = FakeClient()
    c.seed("getClusterState/7", {"data":{"state":"running"}})
    svc = ClusterService(c)
    r = await svc.get_state(7)
    assert r["state"] == "running"

@pytest.mark.asyncio
async def test_list_nodes():
    c = FakeClient()
    c.seed("getClusterNodes", {"rows":[{"id":1,"name":"n1","ip":"10.0.0.1"}],"totalCount":1})
    svc = ClusterService(c)
    r = await svc.list_nodes(cluster_id=5)
    assert r.total == 1
    assert isinstance(r.items[0], ClusterNode)
    body = c.calls[-1][2]
    assert body["clusterId"] == 5

@pytest.mark.asyncio
async def test_list_platform_partitions():
    c = FakeClient()
    c.seed("getPartition", {"rows":[{"id":1,"name":"p1"}],"totalCount":1})
    svc = ClusterService(c)
    r = await svc.list_platform_partitions(cluster_id=5)
    assert isinstance(r.items[0], ClusterPartition)

@pytest.mark.asyncio
async def test_get_partition_resource():
    c = FakeClient()
    c.seed("clusterPartitionResource/1,2", {"data":{"cpuTotal":100,"memTotal":200}})
    svc = ClusterService(c)
    r = await svc.get_partition_resource("1,2")
    assert r.cpu_total == 100
    assert r.mem_total == 200

@pytest.mark.asyncio
async def test_list_clusters_by_env():
    c = FakeClient()
    c.seed("getClusterByEnvId/3", {"data":[{"id":1}]})
    svc = ClusterService(c)
    r = await svc.list_clusters_by_env(3)
    assert isinstance(r, list) and len(r) == 1

@pytest.mark.asyncio
async def test_list_available_partitions():
    c = FakeClient()
    c.seed("clusterPartition", {"rows":[{"id":1,"name":"p1"}],"totalCount":1})
    svc = ClusterService(c)
    r = await svc.list_available_partitions()
    assert r.total == 1
