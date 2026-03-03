from __future__ import annotations


def build_briefing_prompt(transcript: str) -> str:
    """Build a structured prompt with strong JSON guardrails."""
    return f"""You are a helpful assistant. Create a structured meeting briefing.

Required JSON structure:
{{
  "summary": "string (1-2 sentence summary)",
  "action_items": [{{"owner": "string", "task": "string", "due_date": "string or null"}}],
  "risks": ["string"],
  "next_steps": ["string"]
}}

Transcript:
{transcript}
"""
