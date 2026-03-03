from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class BriefingRequest(BaseModel):
    transcript: str = Field(..., description="Raw meeting transcript in plain text.")


class ActionItem(BaseModel):
    owner: str = Field(..., min_length=1)
    task: str = Field(..., min_length=1)
    due_date: str | None = Field(None, description="Optional due date as free text.")


class BriefingMeta(BaseModel):
    provider: str
    request_id: str
    warnings: list[str] = Field(default_factory=list)


class BriefingResponse(BaseModel):
    summary: str
    action_items: list[ActionItem] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)
    next_steps: list[str] = Field(default_factory=list)
    meta: BriefingMeta

    # Allow forward compatibility for candidates who add fields intentionally.
    model_config = {"extra": "allow"}

    @classmethod
    def from_untrusted(cls, data: Any) -> "BriefingResponse":
        # NOTE: This intentionally does almost no validation/normalization besides Pydantic defaults.
        # Part of the exercise is to improve how untrusted model output is parsed and validated.
        return cls.model_validate(data)
