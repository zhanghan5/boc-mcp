import pytest
from boc_mcp.client.pagination import paginate

@pytest.mark.asyncio
async def test_paginate_yields_all_items():
    pages = [
        {"rows":[{"id":1},{"id":2}],"totalCount":5,"currPageNum":1,"pageSize":2},
        {"rows":[{"id":3},{"id":4}],"totalCount":5,"currPageNum":2,"pageSize":2},
        {"rows":[{"id":5}],"totalCount":5,"currPageNum":3,"pageSize":2},
    ]
    idx = 0
    async def fetch(**kw):
        nonlocal idx
        assert kw["currPageNum"] == idx + 1
        p = pages[idx]; idx += 1; return p
    items = [i async for i in paginate(fetch, size=2)]
    assert [i["id"] for i in items] == [1,2,3,4,5]

@pytest.mark.asyncio
async def test_paginate_handles_empty():
    async def fetch(**kw):
        return {"rows":[],"totalCount":0}
    assert [i async for i in paginate(fetch)] == []
