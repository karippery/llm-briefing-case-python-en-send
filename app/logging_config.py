from __future__ import annotations

import logging
import sys
from typing import Any


def configure_logging(level: str) -> None:
    # Intentionally minimal. Candidates may improve structure, context and privacy controls.
    logging.basicConfig(
        level=level,
        stream=sys.stdout,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)


def with_context(logger: logging.Logger, **extra: Any) -> logging.LoggerAdapter:
    return logging.LoggerAdapter(logger, extra)
