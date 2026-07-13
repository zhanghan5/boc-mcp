import json
import logging

from boc_mcp.logging_setup import _SensitiveFilter, setup_logging


def test_setup_logging_produces_json_in_prod(capsys, monkeypatch):
    for k in ("BOC_DEV", "DEV"):
        monkeypatch.delenv(k, raising=False)
    setup_logging(level="INFO")
    logger = logging.getLogger("boc_mcp.test")
    logger.info("hello", extra={"path": "/x", "status": 200})
    out = capsys.readouterr().err
    matches = [ln for ln in out.splitlines() if "hello" in ln]
    rec = json.loads(matches[0])
    assert rec["message"] == "hello"
    assert rec["level"] == "INFO"
    assert rec["path"] == "/x"


def test_sensitive_filter_masks_password():
    f = _SensitiveFilter()
    rec = logging.LogRecord("x", logging.INFO, "", 0, "password=secret123 token=abc", (), None)
    f.filter(rec)
    assert "secret123" not in rec.getMessage()
    assert "abc" not in rec.getMessage()
