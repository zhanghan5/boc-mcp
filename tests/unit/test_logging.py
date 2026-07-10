import logging, json
from boc_mcp.logging_setup import setup_logging, _SensitiveFilter

def test_setup_logging_produces_json_in_prod(capsys, monkeypatch):
    for k in ("BOC_DEV","DEV"):
        monkeypatch.delenv(k, raising=False)
    setup_logging(level="INFO")
    logger = logging.getLogger("boc_mcp.test")
    logger.info("hello", extra={"path": "/x", "status": 200})
    out = capsys.readouterr().err
    line = [l for l in out.splitlines() if "hello" in l][0]
    rec = json.loads(line)
    assert rec["message"] == "hello"
    assert rec["level"] == "INFO"
    assert rec["path"] == "/x"

def test_sensitive_filter_masks_password():
    f = _SensitiveFilter()
    rec = logging.LogRecord("x", logging.INFO, "", 0, "password=secret123 token=abc", (), None)
    f.filter(rec)
    assert "secret123" not in rec.getMessage()
    assert "abc" not in rec.getMessage()
