# Take-Home Case Study (Python) — LLM Briefing Service (Hardening + Tests)

## What you are building
You receive a small **FastAPI** backend that turns a meeting transcript into a **structured briefing**:

- `summary` (string)
- `action_items` (list of `{owner, task, due_date}` objects)
- `risks` (list of strings)
- `next_steps` (list of strings)
- `meta` (provider + request_id + warnings)

The starter code is intentionally **not production-ready**. The goal is to make it safer and more robust: safe parsing, schema validation, correct API behavior, privacy-aware logging, and tests.

## Important constraints
- **Offline only:** do **not** call external LLM APIs. No API keys are required.
- Please **work within the existing stack** (FastAPI + Pydantic). Do not migrate to another framework.
- The repo includes a deterministic `StubProvider` (used by default).
- Prefer clarity and robustness over additional features.

## Suggested effort and deadline
- **Suggested effort:** ~3–4 hours.
- **Deadline:** submit within **48 hours** of receiving the task.
- Please **do not** spend more than ~6 hours. Prioritization and trade-offs are part of the evaluation.
- In `REVIEW.md`, include your **approximate time spent**.

## Getting started

### 1) Create venv + install dependencies
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
```

Or use the Makefile:
```bash
make install
```

### 2) Run tests
```bash
pytest -q
# or
make test
```

### 3) Run the service
```bash
uvicorn app.main:app --reload --port 8000
# or
make run
```

### 4) Try the API
```bash
curl -s http://localhost:8000/health

curl -s -X POST http://localhost:8000/v1/briefings \
  -H "Content-Type: application/json" \
  -d '{"transcript":"Weekly sync: Action: Alice drafts the postmortem. Risk: on-call load."}'
```

## Deliverables (what you submit)
- The updated repository (Git link preferred) or a ZIP of the final code
- Updated `README.md`
- A filled `REVIEW.md`
- Optional: a short AI usage log (see `AI_USAGE_LOG_TEMPLATE.md`)

## Requirements (must-haves)

### 1) Safe parsing + schema validation
- Treat model output as **untrusted input**.
- Parse it safely into Python data structures.
- Make the parser robust against common LLM output noise (e.g., extra non-JSON text, markdown wrappers).
- Validate the result using Pydantic (`BriefingResponse` / `ActionItem`).

### 2) Correct API behavior and safe errors
- Use appropriate HTTP status codes (4xx for invalid client input, 5xx for upstream/server failures).
- Do not leak stack traces or sensitive config in API responses.
- Keep error responses consistent and useful.

### 3) Privacy-aware logging
- Do not log transcripts or secrets.
- Prefer request IDs and minimal metadata (e.g., transcript length, timings).

### 4) Cost / abuse guard (simple input limit)
- Add a hard limit on transcript size (e.g., max characters) and return a clear 4xx error if exceeded.
- Keep it simple and explain your choice in `REVIEW.md`.

### 5) Tests (offline, deterministic)
- Add at least **5 tests** (6+ recommended).
- Include at least **1 integration test** using FastAPI’s `TestClient`.
- Tests must run offline and deterministically.

### 6) Written review + architecture thinking
Fill `REVIEW.md`:
- time spent
- top 3 security/stability issues you identified in the starter (and what you did about them)
- key trade-offs and “what’s next for production”
- an architecture question (multi-provider selection + quality/cost evaluation approach)

## Optional (nice-to-haves)
- Retries/backoff for transient provider failures (e.g., timeouts)
- Request IDs in response headers
- Structured logs (JSON), basic metrics
- Caching (TTL), rate limiting

## Notes on libraries
You may add small libraries if they help (e.g., safe JSON parsing/extraction, schema validation).
Keep the solution offline and reasonably lightweight.
