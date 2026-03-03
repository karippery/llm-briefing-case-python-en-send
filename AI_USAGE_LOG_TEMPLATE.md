# AI Usage Log (template)

AI usage is allowed. Please keep this short (2–8 bullets).

- Tool(s) used: Claude Code (free tier), GitHub Copilot (free tier)
- What I used them for:Claude Code: code review, identifying bugs, and discussing fixes for parsing, logging privacy, and HTTP status   
    code correctness
- One example where I accepted AI output as-is: The structured JSON logging formatter and privacy filter in `logging_config.py`
    the design matched what I needed and I applied it after reviewing it
- One example where I modified or rejected AI output: Rejected or rewrote AI suggestions for the brace counter fix, `[badjson]`
    stub behavior, and several error handling paths in `main.py` — in each case
    the AI output was either incorrect, didn't match actual runtime behavior I
    observed through manual testing, or didn't fit the existing code structure.
    I wrote the final versions myself after understanding the root cause
- How I verified correctness (tests, manual checks, etc.):
 - Ran the service locally with `uvicorn` and tested all stub markers manually
    (`[fence]`, `[preamble]`, `[badjson]`, `[timeout]`) via curl
 - Ran the full test suite with `pytest -q` and verified all tests passed offline
