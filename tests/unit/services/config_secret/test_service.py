import pytest

from boc_mcp.models.common import ListResult
from boc_mcp.services.config_secret.models import SecretItem
from boc_mcp.services.config_secret.service import ConfigSecretService


class FakeClient:
    def __init__(self):
        self.calls: list[tuple] = []
        self.payloads: dict[str, dict] = {}

    def seed(self, key: str, resp: dict) -> None:
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
async def test_list_secrets_returns_parsed_items():
    c = FakeClient()
    c.seed(
        "/secret/v2.3/list",
        {
            "rows": [
                {"name": "s1", "namespace": "default", "type": "Opaque"},
                {"name": "s2", "namespace": "default", "type": "kubernetes.io/tls"},
            ],
            "totalCount": 2,
            "currPageNum": 1,
            "pageSize": 20,
            "pageCount": 1,
        },
    )
    svc = ConfigSecretService(c)
    r = await svc.list_secrets(master_ip="10.0.0.1", namespace="default")
    assert isinstance(r, ListResult)
    assert r.total == 2
    assert len(r.items) == 2
    assert all(isinstance(i, SecretItem) for i in r.items)
    assert r.items[0].name == "s1"
    assert r.items[0].namespace == "default"
    assert r.items[0].type == "Opaque"


@pytest.mark.asyncio
async def test_list_secrets_body_contains_required_and_optional_fields():
    c = FakeClient()
    c.seed(
        "/secret/v2.3/list",
        {"rows": [], "totalCount": 0, "currPageNum": 1, "pageSize": 20, "pageCount": 0},
    )
    svc = ConfigSecretService(c)
    await svc.list_secrets(
        master_ip="10.0.0.1",
        namespace="ns1",
        master_port=6443,
        master_type="https",
        master_version="v2.3",
        name="mysecret",
        env_id=5,
        project_ids="1,2",
        registry_id=9,
        registry_type="harbor",
        type_="Opaque",
        data={"key": "value"},
        label={"app": "demo"},
        page=2,
        page_size=50,
    )
    method, path, body = c.calls[-1]
    assert method == "post"
    assert path == "/secret/v2.3/list"
    assert body["masterIp"] == "10.0.0.1"
    assert body["namespace"] == "ns1"
    assert body["masterPort"] == 6443
    assert body["masterType"] == "https"
    assert body["masterVersion"] == "v2.3"
    assert body["name"] == "mysecret"
    assert body["envId"] == 5
    assert body["projectIds"] == "1,2"
    assert body["registryId"] == 9
    assert body["registryType"] == "harbor"
    assert body["type"] == "Opaque"
    assert body["data"] == {"key": "value"}
    assert body["label"] == {"app": "demo"}
    assert body["currPageNum"] == 2
    assert body["pageSize"] == 50
    assert "token" not in body


@pytest.mark.asyncio
async def test_list_secrets_default_pagination_and_caps_page_size():
    c = FakeClient()
    c.seed(
        "/secret/v2.3/list",
        {"rows": [], "totalCount": 0, "currPageNum": 1, "pageSize": 100, "pageCount": 0},
    )
    svc = ConfigSecretService(c)
    await svc.list_secrets(master_ip="10.0.0.1", namespace="default", page_size=500)
    _, _, body = c.calls[-1]
    assert body["currPageNum"] == 1
    assert body["pageSize"] == 100


@pytest.mark.asyncio
async def test_list_secrets_direct_data_list_response():
    c = FakeClient()
    c.seed("/secret/v2.3/list", {"data": [{"name": "s1", "namespace": "default"}]})
    svc = ConfigSecretService(c)
    r = await svc.list_secrets(master_ip="10.0.0.1", namespace="default")
    assert r.total == 1
    assert r.items[0].name == "s1"
