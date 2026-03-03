from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    app_env: str = os.getenv("APP_ENV", "dev")
    log_level: str = os.getenv("LOG_LEVEL", "INFO")

    #max_transcription_length
    max_transcription_length: int = int(os.getenv("MAX_TRANSCRIPTION_LENGTH", "35000"))

    # In this take-home, the service runs offline with the StubProvider.
    # This env var is kept to reflect a realistic configuration surface.
    llm_provider: str = os.getenv("LLM_PROVIDER", "stub")

    # Optional secret for real providers (not used in this take-home).
    # WARNING: do not log this.
    llm_api_key: str | None = os.getenv("LLM_API_KEY")

    # Optional knobs candidates may choose to use (or ignore) for resilience.
    request_timeout_seconds: float = float(os.getenv("REQUEST_TIMEOUT_SECONDS", "10"))
    llm_retries: int = int(os.getenv("LLM_RETRIES", "2"))


settings = Settings()
