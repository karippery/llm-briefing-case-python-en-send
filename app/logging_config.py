from __future__ import annotations

import json
import logging
import sys
from typing import Any

# Fields that must never appear in logs, regardless of who adds them.
_BLOCKED_FIELDS = frozenset({
    "transcript",
    "api_key",
    "secret",
    "token",
    "password",
    "authorization",
})

# Internal LogRecord attributes we don't want to re-emit as extra fields.
_LOGRECORD_BUILTINS = frozenset({
    "msg", "args", "levelname", "levelno", "name", "pathname", "filename",
    "module", "exc_info", "exc_text", "stack_info", "lineno", "funcName",
    "created", "msecs", "relativeCreated", "thread", "threadName",
    "processName", "process", "message", "taskName",
})


class _JsonFormatter(logging.Formatter):
    """Emit one JSON object per log line — machine-parseable and privacy-safe."""

    def format(self, record: logging.LogRecord) -> str:
        # Always-present fields
        entry: dict[str, Any] = {
            "ts": self.formatTime(record, datefmt="%Y-%m-%dT%H:%M:%S"),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Attach caller extras, skip builtins and blocked privacy fields
        for key, value in record.__dict__.items():
            if key in _LOGRECORD_BUILTINS or key.startswith("_"):
                continue
            if key in _BLOCKED_FIELDS:
                entry[key] = "[REDACTED]"   # warn rather than silently drop
                continue
            entry[key] = value

        # Include exception type + message, but NOT the full traceback
        # (local variable values in tracebacks can contain PII)
        if record.exc_info and record.exc_info[0] is not None:
            entry["exc_type"] = record.exc_info[0].__name__
            raw_msg = str(record.exc_info[1])
            entry["exc_message"] = raw_msg[:200]

        return json.dumps(entry, default=str)


class _PrivacyFilter(logging.Filter):
    """
    Last-resort guard: redact blocked fields on any record before it is emitted,
    even if the formatter is swapped out later.
    """

    def filter(self, record: logging.LogRecord) -> bool:
        for key in _BLOCKED_FIELDS:
            if hasattr(record, key):
                setattr(record, key, "[REDACTED]")
        return True  # always emit — redact, don't suppress


def configure_logging(level: str = "INFO") -> None:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(_JsonFormatter())

    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.addFilter(_PrivacyFilter())
    root.setLevel(level.upper())


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)


def with_context(logger: logging.Logger, **extra: Any) -> logging.LoggerAdapter:
    return logging.LoggerAdapter(logger, extra)