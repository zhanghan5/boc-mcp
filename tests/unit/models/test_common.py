from boc_mcp.models.common import ListResult, ActionResult

def test_list_result_from_legacy():
    payload = {"currPageNum": 1, "pageSize": 10, "totalCount": 25, "pageCount": 3, "rows": [{"id": 1}, {"id": 2}]}
    r = ListResult[dict].from_legacy(payload, items_key="rows")
    assert r.page == 1
    assert r.page_size == 10
    assert r.total == 25
    assert r.page_count == 3
    assert r.items == [{"id": 1}, {"id": 2}]

def test_list_result_single_object_envelope():
    payload = {"state": "success", "code": 200, "data": {"a": 1}}
    r = ListResult[dict].from_legacy(payload, items_key="rows")
    assert r.items == []
    assert r.total == 0

def test_action_result_default_success():
    r = ActionResult()
    assert r.success is True
    assert r.message == ""
