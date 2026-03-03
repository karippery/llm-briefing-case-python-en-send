from __future__ import annotations

import uuid
from typing import Any

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.config import settings
from app.llm.parsing import parse_llm_output
from app.llm.prompt import build_briefing_prompt
from app.llm.provider import build_provider
from app.logging_config import configure_logging, get_logger
from app.models import BriefingRequest, BriefingResponse
from contextlib import asynccontextmanager
from typing import AsyncGenerator

configure_logging(settings.log_level)
logger = get_logger("app")

app = FastAPI(title="LLM Briefing Service", version="0.1.0")

provider = build_provider(settings.llm_provider, settings.llm_api_key)


# @app.on_event("startup")
# def _startup() -> None:
#     logger.info("startup", extra={"settings": repr(settings), "provider": provider.name})

# modern lifespan pattern
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    logger.info("startup", extra={"settings": repr(settings), "provider": provider.name})
    yield
    logger.info("shutdown")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "provider": provider.name}


@app.post("/v1/briefings", response_model=None)
def create_briefing(req: BriefingRequest, request: Request) -> dict[str, Any] | JSONResponse:
    request_id = request.headers.get("X-Request-Id") or str(uuid.uuid4())

    logger.info("briefing_request", extra={"request_id": request_id, "transcript": req.transcript})

    try:
        prompt = build_briefing_prompt(req.transcript)
        raw = provider.generate(prompt)
        data = parse_llm_output(raw)

        if isinstance(data, dict):
            data["meta"] = {"provider": provider.name, "request_id": request_id, "warnings": []}

        briefing = BriefingResponse.from_untrusted(data)
        return briefing.model_dump()

    except Exception as e:  # noqa: BLE001
        logger.exception("briefing_failed", extra={"request_id": request_id})
        return JSONResponse(status_code=200, content={"error": str(e), "request_id": request_id})
