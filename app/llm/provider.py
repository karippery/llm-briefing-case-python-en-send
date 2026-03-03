from __future__ import annotations

import json
import time
import logging
from dataclasses import dataclass, field
from typing import Protocol

logger = logging.getLogger(__name__)


class LLMProvider(Protocol):
    name: str

    def generate(self, prompt: str) -> str:
        """Return raw model output as text."""
        ...


@dataclass
class StubProvider:
    """Deterministic offline provider used for development and tests.

    Depending on the prompt content, it may return non-JSON wrappers or raise errors.
    """

    name: str = "stub"

    def generate(self, prompt: str) -> str:
        time.sleep(0.05)

        transcript = prompt.split("Transcript:", 1)[-1].strip()
        summary = (transcript.splitlines()[0] if transcript else "").strip()
        summary = summary or "No content."

        payload = {
            "summary": summary[:180],
            "action_items": [
                {"owner": "TBD", "task": "Send meeting notes to participants", "due_date": ""}
            ],
            "risks": [],
            "next_steps": ["Schedule follow-up meeting"],
        }
        raw = json.dumps(payload)

        # Markers to simulate typical messy responses:
        if "[fence]" in prompt:
            return f"```json\n{raw}\n```\n"
        if "[preamble]" in prompt:
            return f"Sure, here is the JSON you requested:\n{raw}\n"
        if "[badjson]" in prompt:
            return raw + ","
        if "[timeout]" in prompt:
            raise TimeoutError("Simulated provider timeout")

        return raw


@dataclass
class RetryingProvider:
    """
    Wraps any LLMProvider and retries transient errors with exponential back-off.

    Transient errors: TimeoutError, ConnectionError, OSError.
    Non-transient errors (e.g. ValueError) are re-raised immediately.
    """

    inner: LLMProvider
    max_attempts: int = 3
    base_delay: float = 0.5  # seconds; doubles each attempt

    @property
    def name(self) -> str:
        return self.inner.name

    def generate(self, prompt: str) -> str:
        delay = self.base_delay
        last_exc: Exception | None = None

        for attempt in range(1, self.max_attempts + 1):
            try:
                return self.inner.generate(prompt)
            except (TimeoutError, ConnectionError, OSError) as exc:
                last_exc = exc
                if attempt < self.max_attempts:
                    logger.warning(
                        "provider_transient_error",
                        extra={"attempt": attempt, "delay": delay, "error": str(exc)},
                    )
                    time.sleep(delay)
                    delay *= 2
            except Exception:
                raise  # non-transient – propagate immediately

        raise RuntimeError(
            f"Provider failed after {self.max_attempts} attempts"
        ) from last_exc


def build_provider(provider_name: str, api_key: str | None) -> LLMProvider:
    stub = StubProvider()
    return RetryingProvider(inner=stub)