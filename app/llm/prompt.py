from __future__ import annotations


def build_briefing_prompt(transcript: str) -> str:
    # Intentionally minimal prompt. Candidates may improve structure/guardrails.
    return f"""You are a helpful assistant. Create a structured meeting briefing.

Return ONLY valid JSON with the following keys:
- summary: string
- action_items: array of objects with keys (owner, task, due_date)
- risks: array of strings
- next_steps: array of strings

Transcript:
{transcript}
"""
