# Review (fill this in)

## 1) Time spent
- Approximate total time spent (hh:mm):06:00
- What you focused on first (why):focus on parsing and response json structure, testing, privacy and security issues

## 2) Top 3 security/stability issues in the original starter
For each item: (a) why it matters, (b) how you fixed/mitigated it, (c) what you would do next in production.

1) Issue: Privacy Leak in Logging
- Why it matters:  Logs full transcript — may contain PII, secrets, sensitive business info
- Fix/mitigation: Log Only Metadata
- Next step (prod): update logging settings

2) Issue: eval() in parse_llm_output()  Remote Code Execution Risk
- Why it matters: If a malicious actor (or buggy LLM) returns __import__('os').system('rm -rf /'), your server executes it.
- Fix/mitigation: Safe JSON Parsing with Fallbacks
- Next step (prod): 

3) Issue: Incorrect HTTP Status Codes
- Why it matters: standard error handling
- Fix/mitigation: Use Proper HTTP Semantics
- Next step (prod): Never expose raw exception strings (str(e)) to clients — could leak stack traces or internal details.

## 3) Prompt changes (LLM awareness)
- What did you change in `app/llm/prompt.py`?
    Replaced bullet list with literal JSON template showing exact structure, nesting, and key names
    Added "string or null" for due_date to clarify optional fields	
    Used {{ }} to escape literal braces in the f-string
- Why should this improve schema adherence or reduce parsing failures?   	
    LLMs are pattern-matchers — showing a concrete JSON template is more effective than describing it abstractly. Reduces structural errors like missing keys or wrong nesting.
- Any prompt-injection considerations?
Yes — transcript is interpolated directly. Mitigated via downstream parsing, Pydantic validation, safe logging, and structured errors. Optional: add delimiters + explicit "ignore instructions" guardrail


## 4) Cost / input limits
- What limit did you implement (and where)? MAX_TRANSCRIPTION_LENGTH = 35000
- Why did you pick this limit (rough reasoning is fine)? Without a limit, an attacker could send 10MB+ payloads, consuming memory, CPU (parsing/LLM), and bandwidth. 50KB is small enough to mitigate this.	Even with the stub provider, a real LLM would charge per token. 35K chars ≈ 10K–15K tokens — reasonable for a single request without exploding costs.Larger inputs = longer processing time. 35KB keeps latency predictable for synchronous HTTP requests.

## 5) Testing strategy
- What do your most important tests cover? Critical Path Coverage ,  Error Handling & Edge Cases,  Security & Privacy, Unit-Level Validation. I need make sure i have atleast 80% test coverage before push code. this code base total test coverage is 93%
- What did you intentionally not test (and why)? Real LLM provider,Authentication / rate limiting

## 6) Architecture question (short, 1–2 paragraphs)
Imagine you need to:
1) query **multiple LLM providers** in parallel and select the “best” result, and
2) continuously measure **output quality** and **cost** in production.

To support parallel querying, I would extend the existing LLMProvider Protocol to be async-compatible and use asyncio.gather within the service layer to fire requests to multiple providers concurrently. A "selector" component would then evaluate the responses using a lightweight scoring mechanism (e.g., a smaller judge model, heuristic validation, or majority voting) to pick the best result before returning it to the client, ensuring total latency is bounded by the fastest provider plus the evaluation overhead.

For production observability, I would implement structured logging to capture provider-specific latency, token usage, and cost metadata for every request, exporting these metrics to a dashboard (e.g., Prometheus/Datadog) for real-time cost tracking. Output quality would be measured via a feedback loop combining implicit signals (user edits, acceptance rates) and explicit automated evals (sampling responses against a golden dataset), enabling dynamic provider routing based on evolving cost-performance tradeoffs.

How would you extend this service? What components and decisions are critical (e.g., interfaces, fallbacks, evaluation, observability)?
I would extend the LLMProvider Protocol to support async operations, enabling a router component that queries multiple providers concurrently (for comparison) or sequentially (for fallbacks) based on cost/latency SLAs. Critical to this is implementing a circuit breaker pattern to automatically cascade requests (e.g., GPT-4 → Claude → Stub) during outages, ensuring high availability without manual intervention.
For production readiness, I'd integrate OpenTelemetry for distributed tracing to correlate request IDs across services and log structured metrics (token usage, cost, latency) to a time-series database for real-time cost monitoring. Quality would be managed via an evaluation pipeline that samples outputs for automated scoring (using a judge model) and human feedback, allowing dynamic provider routing based on evolving quality-vs-cost tradeoffs.

## 7) AI usage log (optional)
- Tools used (if any): Claude code free version, copilot for autocomplet
- What you used them for: Claude as a coding assistant for code review, specific bug fixes, and implementation guidance
- What you manually verified/changed: Integrated fixes into the existing codebase and confirmed the service ran correctly. Reviewed and accepted/rejected each suggested change rather than applying blindly
