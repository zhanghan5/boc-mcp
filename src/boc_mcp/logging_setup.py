from __future__ import annotations

import json
import logging
import os
import sys
from typing import Any

_SENSITIVE_KEYS = ("password", "token", "refreshtoken", "authorization", "secret")


class _JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": self.formatTime(record, "%Y-%m-%dT%H:%M:%S"),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        skip = {"args","asctime","created","exc_info","exc_text","filename","funcName",
                "levelname","levelno","lineno","module","msecs","message","msg","name",
                "pathname","process","processName","relativeCreated","stack_info","thread",
                "threadName"}
        for k, v in record.__dict__.items():
            if k not in skip:
                payload[k] = v
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=False, default=str)


class _SensitiveFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        try:
            msg = record.getMessage()
        except Exception:
            return True
        low = msg.lower()
        for key in _SENSITIVE_KEYS:
            idx = low.find(key)
            if idx >= 0:
                msg = msg[:idx] + key + "=***"
        record.msg = msg
        record.args = ()
        return True


def setup_logging(level: str = "INFO") -> None:
    is_dev = os.environ.get("BOC_DEV") == "1" or os.environ.get("DEV") == "1"
    handler = logging.StreamHandler(sys.stderr)
    if is_dev:
        handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s"))
    else:
        handler.setFormatter(_JsonFormatter())
    handler.addFilter(_SensitiveFilter())
    root = logging.getLogger("boc_mcp")
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(getattr(logging, level.upper(), logging.INFO))
    root.propagate = False
