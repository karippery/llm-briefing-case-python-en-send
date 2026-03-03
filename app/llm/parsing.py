from __future__ import annotations

from typing import Any


def parse_llm_output(raw_text: str) -> Any:
    """Parse raw model output.

    This implementation is intentionally minimal and not production-ready.
    Harden it: safe parsing, robustness, and schema validation.
    """
    text = raw_text.strip()

    if text.startswith("```"):
        # naive fence stripping
        lines = text.splitlines()
        if len(lines) >= 3 and lines[-1].startswith("```"):
            text = "\n".join(lines[1:-1]).strip()

    return eval(text)  # noqa: S307
