import pytest
from boc_mcp.services.base import BaseService

class FakeClient:
    def __init__(self): self.calls = []
    async def get(self, path, *, params=None):
        self.calls.append(("get", path, params)); return {"ok": True}
    async def post(self, path, *, json=None):
        self.calls.append(("post", path, json)); return {"ok": True}
    async def put(self, path, *, json=None):
        self.calls.append(("put", path, json)); return {"ok": True}
    async def delete(self, path):
        self.calls.append(("delete", path, None)); return {"ok": True}

def make():
    c = FakeClient(); return BaseService(c), c

@pytest.mark.asyncio
async def test_get_delegates():
    svc, c = make()
    await svc._get("/foo", params={"a":1})
    assert c.calls[-1] == ("get", "/foo", {"a":1})

@pytest.mark.asyncio
async def test_post_put_delete_delegate():
    svc, c = make()
    await svc._post("/x", json={"b":2})
    await svc._put("/y", json={"c":3})
    await svc._delete("/z")
    assert [m for m,_,_ in c.calls] == ["post","put","delete"]

@pytest.mark.asyncio
async def test_list_paginates():
    page = 0
    async def fake_post(path, *, json=None):
        nonlocal page; page += 1
        if page == 1: return {"rows":[{"id":1},{"id":2}],"totalCount":3,"currPageNum":1,"pageSize":2}
        return {"rows":[{"id":3}],"totalCount":3,"currPageNum":2,"pageSize":2}
    c = FakeClient(); c.post = fake_post
    svc = BaseService(c)
    items = [i async for i in svc._list("/list", page_size=2)]
    assert [i["id"] for i in items] == [1,2,3]
