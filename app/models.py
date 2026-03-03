from __future__ import annotations

from typing import Any
from pydantic import BaseModel, Field, field_validator



class BriefingRequest(BaseModel):
    transcript: str = Field(..., min_length=1, description="Raw meeting transcript in plain text.")


class ActionItem(BaseModel):
    owner: str = Field(..., min_length=1, max_length=100, description="Person responsible for the action item.")
    task: str = Field(..., min_length=1, max_length=1000, description="Description of the task to be done.")
    due_date: str | None = Field(None, description="Optional due date as free text.")

    @field_validator("due_date")
    @classmethod
    def normalize_empty_due_date(cls, v: str | None) -> str | None:
        """Normalize empty strings to None."""
        if v == "":
            return None
        return v


class BriefingMeta(BaseModel):
    provider: str = Field(..., min_length=1,description="Name of the LLM provider used to generate this briefing.")
    request_id: str = Field(..., min_length=1, description="Unique identifier for the request, useful for tracing and debugging.")
    warnings: list[str] = Field(default_factory=list)


class BriefingResponse(BaseModel):
    summary: str = Field(..., min_length=1, max_length=5000, description="Concise summary of the meeting.")
    action_items: list[ActionItem] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)
    next_steps: list[str] = Field(default_factory=list)
    meta: BriefingMeta

    # The LLM could inject arbitrary fields (__proto__, unexpected keys) that get serialised into the response. Change to "ignore"
    model_config = {"extra": "ignore"}

    @classmethod
    def from_untrusted(cls, data: Any) -> "BriefingResponse":
        """Validate and normalise untrusted LLM output into a BriefingResponse."""
        if not isinstance(data, dict):
            raise ValueError(f"Expected dict from LLM, got {type(data).__name__}")

        data.setdefault("risks", [])
        data.setdefault("next_steps", [])
        data.setdefault("action_items", [])

        # Coerce list fields – LLM sometimes returns a bare string
        for list_field in ("risks", "next_steps"):
            if isinstance(data[list_field], str):
                data[list_field] = [data[list_field]] if data[list_field] else []

        # Normalise empty due_date strings inside action_items
        for item in data.get("action_items", []):
            if isinstance(item, dict) and item.get("due_date") == "":
                item["due_date"] = None

        return cls.model_validate(data)
