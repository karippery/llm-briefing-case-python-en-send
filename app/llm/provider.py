from __future__ import annotations

import json
import time
from dataclasses import dataclass
from typing import Protocol


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
        # Simulate latency
        time.sleep(0.05)

        # Very naive "extraction" from the prompt for deterministic outputs.
        transcript = prompt.split("Transcript:", 1)[-1].strip()
        summary = (transcript.splitlines()[0] if transcript else "").strip()
        if not summary:
            summary = "No content."

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
            return raw + ","  # invalid JSON
        if "[timeout]" in prompt:
            raise TimeoutError("Simulated provider timeout")

        return raw


def build_provider(provider_name: str, api_key: str | None) -> LLMProvider:
    """Build the provider implementation.

    For this take-home, we intentionally run **offline** and always use StubProvider.
    The parameters exist only to reflect a realistic interface.
    """
    return StubProvider()
