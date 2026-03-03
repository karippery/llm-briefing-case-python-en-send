from __future__ import annotations

from typing import Any
from pydantic import BaseModel, Field, field_validator



class BriefingRequest(BaseModel):
    transcript: str = Field(..., min_length=1, max_length=10000, description="Raw meeting transcript in plain text.")


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

    # Allow forward compatibility for candidates who add fields intentionally.
    model_config = {"extra": "allow"}

    @classmethod
    def from_untrusted(cls, data: Any) -> "BriefingResponse":
        """Validate and normalize untrusted LLM output."""
        # Normalize action_items due_date before validation
        if isinstance(data.get("action_items"), list):
            for item in data["action_items"]:
                if isinstance(item, dict) and item.get("due_date") == "":
                    item["due_date"] = None
        
        # Ensure required fields exist with defaults
        data.setdefault("risks", [])
        data.setdefault("next_steps", [])
        data.setdefault("action_items", [])
        
        return cls.model_validate(data)
