import pytest

from boc_mcp.models.common import ListResult
from boc_mcp.services.partition.models import HostNode, Partition, PartitionNode
from boc_mcp.services.partition.service import PartitionService


class FakeClient:
    def __init__(self):
        self.calls = []
        self.payloads = {}

    def seed(self, key, resp):
        self.payloads[key] = resp

    async def get(self, path, *, params=None):
        self.calls.append(("get", path, params))
        for k, v in self.payloads.items():
            if k in path:
                return v
        return {}

    async def post(self, path, *, json=None):
        self.calls.append(("post", path, json))
        for k, v in self.payloads.items():
            if k in path:
                return v
        return {"rows": [], "totalCount": 0, "currPageNum": 1, "pageSize": 20, "pageCount": 0}


@pytest.mark.asyncio
async def test_list_partitions():
    c = FakeClient()
    c.seed(
        "/partition/v2.3/list",
        {
            "rows": [{"id": 1, "name": "p1"}, {"id": 2, "name": "p2"}],
            "totalCount": 2,
            "currPageNum": 1,
            "pageSize": 20,
            "pageCount": 1,
        },
    )
    svc = PartitionService(c)
    r = await svc.list_partitions()
    assert isinstance(r, ListResult)
    assert r.total == 2
    assert len(r.items) == 2
    assert isinstance(r.items[0], Partition)
    assert r.items[0].id == 1


@pytest.mark.asyncio
async def test_list_partitions_page_size_capped():
    c = FakeClient()
    c.seed(
        "/partition/v2.3/list",
        {"rows": [], "totalCount": 0, "currPageNum": 1, "pageSize": 100, "pageCount": 0},
    )
    svc = PartitionService(c)
    await svc.list_partitions(page_size=500)
    assert c.calls[-1][2]["pageSize"] == 100


@pytest.mark.asyncio
async def test_get_default_partition():
    c = FakeClient()
    c.seed("/partition/v3.3/getDefaultPartition/7", {"data": {"id": 11, "name": "default"}})
    svc = PartitionService(c)
    r = await svc.get_default_partition(7)
    assert c.calls[-1][0] == "get"
    assert r["id"] == 11
    assert r["name"] == "default"


@pytest.mark.asyncio
async def test_get_partition_meta():
    c = FakeClient()
    c.seed("/partition/v2.3/getPartitionMeta", {"data": {"k": "v"}})
    svc = PartitionService(c)
    r = await svc.get_partition_meta(filters={"partId": 1})
    assert r == {"k": "v"}
    assert c.calls[-1][2] == {"partId": 1}


@pytest.mark.asyncio
async def test_list_default_partitions():
    c = FakeClient()
    c.seed("/partition/v2.3/listByKind", {"data": [{"id": 1, "name": "d1"}]})
    svc = PartitionService(c)
    r = await svc.list_default_partitions()
    assert isinstance(r, list) and len(r) == 1
    assert isinstance(r[0], Partition)


@pytest.mark.asyncio
async def test_list_nodes():
    c = FakeClient()
    c.seed("/partition/v2.3/nodelist", {"data": [{"id": 1, "name": "n1", "ip": "10.0.0.1"}]})
    svc = PartitionService(c)
    r = await svc.list_nodes()
    assert isinstance(r, list) and len(r) == 1
    assert isinstance(r[0], PartitionNode)
    assert r[0].ip == "10.0.0.1"


@pytest.mark.asyncio
async def test_list_all_hosts_with_cluster():
    c = FakeClient()
    c.seed("/partition/v3.3/getAllHost", {"data": [{"id": 1, "name": "h1", "ip": "1.1.1.1"}]})
    svc = PartitionService(c)
    r = await svc.list_all_hosts(cluster_id=9)
    assert len(r) == 1 and isinstance(r[0], HostNode)
    assert c.calls[-1][2] == {"clusterId": 9}


@pytest.mark.asyncio
async def test_list_all_hosts_no_arg():
    c = FakeClient()
    c.seed("/partition/v3.3/getAllHost", {"data": []})
    svc = PartitionService(c)
    r = await svc.list_all_hosts()
    assert r == []
    assert c.calls[-1][2] == {}


@pytest.mark.asyncio
async def test_all_info_pagination_and_fields():
    c = FakeClient()
    c.seed(
        "/partition/v2.3/allInfo",
        {
            "rows": [{"id": 1, "name": "h1", "ip": "2.2.2.2"}],
            "totalCount": 1,
            "currPageNum": 2,
            "pageSize": 10,
            "pageCount": 1,
        },
    )
    svc = PartitionService(c)
    r = await svc.all_info(
        cluster_id=3, env_id=4, host_ip="2.2.2.2", node_name="n1", page=2, page_size=10
    )
    assert isinstance(r, ListResult)
    assert r.total == 1
    assert isinstance(r.items[0], HostNode)
    body = c.calls[-1][2]
    assert body["clusterId"] == 3
    assert body["envId"] == 4
    assert body["hostIp"] == "2.2.2.2"
    assert body["nodeName"] == "n1"
    assert body["currPageNum"] == 2


@pytest.mark.asyncio
async def test_detail_by_condition():
    c = FakeClient()
    c.seed("/partition/v2.3/detailByCondition", {"data": {"id": 1, "detail": True}})
    svc = PartitionService(c)
    r = await svc.detail_by_condition(filters={"id": 1})
    assert r["detail"] is True
    assert c.calls[-1][2] == {"id": 1}


@pytest.mark.asyncio
async def test_list_available():
    c = FakeClient()
    c.seed(
        "/partition/v2.3/clusterPartition",
        {
            "rows": [{"id": 8, "name": "avail"}],
            "totalCount": 1,
            "currPageNum": 1,
            "pageSize": 20,
            "pageCount": 1,
        },
    )
    svc = PartitionService(c)
    r = await svc.list_available()
    assert isinstance(r, ListResult)
    assert r.total == 1
    assert isinstance(r.items[0], Partition)
    assert r.items[0].name == "avail"


@pytest.mark.asyncio
async def test_direct_data_list_form():
    c = FakeClient()
    c.seed("/partition/v2.3/clusterPartition", {"data": [{"id": 1}, {"id": 2}]})
    svc = PartitionService(c)
    r = await svc.list_available()
    assert r.total == 2
    assert r.page_count == 1
