from __future__ import annotations

import uuid
from typing import Any

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi import status
from pydantic import ValidationError

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


# @app.on_event("startup")
# def _startup() -> None:
#     logger.info("startup", extra={"settings": repr(settings), "provider": provider.name})

# modern lifespan pattern
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    logger.info(
        "service_startup",
        extra={"provider": settings.llm_provider, "log_level": settings.log_level}
    )
    yield
    logger.info("service_shutdown")

app = FastAPI(title="LLM Briefing Service", version="0.1.0", lifespan=lifespan)
provider = build_provider(settings.llm_provider, settings.llm_api_key)

@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "provider": provider.name}


@app.post("/v1/briefings", response_model=None)
def create_briefing(req: BriefingRequest, request: Request) -> dict[str, Any] | JSONResponse:
    request_id = request.headers.get("X-Request-Id") or str(uuid.uuid4())

    if len(req.transcript) > settings.max_transcription_length:
        return JSONResponse(
            status_code=413,
            content={"error": {"code": "transcript_too_large", "request_id": request_id}}
        )


    logger.info("briefing_request", extra={"request_id": request_id, "transcript_length": len(req.transcript)})

    try:
        prompt = build_briefing_prompt(req.transcript)
        raw = provider.generate(prompt)
        data = parse_llm_output(raw)

        if isinstance(data, dict):
            data["meta"] = {"provider": provider.name, "request_id": request_id, "warnings": []}

        briefing = BriefingResponse.from_untrusted(data)
        response = JSONResponse(content=briefing.model_dump())
        response.headers["X-Request-Id"] = request_id
        return response

    except ValidationError as e:
        logger.warning(
            "briefing_validation_failed",
            extra={"request_id": request_id, "error_type": "validation"}
        )
        response = JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"error": {"code": "validation_error", "request_id": request_id}}
        )
        response.headers["X-Request-Id"] = request_id
        return response

    except ValueError as e:
        logger.warning(
            "briefing_parse_failed",
            extra={"request_id": request_id, "error_type": "parse"}
        )
        response = JSONResponse(
            status_code=status.HTTP_502_BAD_GATEWAY,  # ← This is what the test expects!
            content={"error": {"code": "parse_error", "request_id": request_id}}
        )
        response.headers["X-Request-Id"] = request_id
        return response

    except TimeoutError as e:
        # 504: Provider timeout
        logger.warning(
            "briefing_provider_timeout",
            extra={"request_id": request_id}
        )
        return JSONResponse(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            content={"error": "provider_timeout", "request_id": request_id}
        )

    except Exception as e:
        # 500: Unexpected server error (no stack trace leaked!)
        logger.exception(
            "briefing_unexpected_error",
            extra={"request_id": request_id}
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": "internal_error", "request_id": request_id}
        )
