# Review (fill this in)

## 1) Time spent
- Approximate total time spent (hh:mm):
- What you focused on first (why):

## 2) Top 3 security/stability issues in the original starter
For each item: (a) why it matters, (b) how you fixed/mitigated it, (c) what you would do next in production.

1) Issue:
- Why it matters:
- Fix/mitigation:
- Next step (prod):

2) Issue:
- Why it matters:
- Fix/mitigation:
- Next step (prod):

3) Issue:
- Why it matters:
- Fix/mitigation:
- Next step (prod):

## 3) Prompt changes (LLM awareness)
- What did you change in `app/llm/prompt.py`?
- Why should this improve schema adherence or reduce parsing failures?
- Any prompt-injection considerations?

## 4) Cost / input limits
- What limit did you implement (and where)?
- Why did you pick this limit (rough reasoning is fine)?

## 5) Testing strategy
- What do your most important tests cover?
- What did you intentionally not test (and why)?

## 6) Architecture question (short, 1–2 paragraphs)
Imagine you need to:
1) query **multiple LLM providers** in parallel and select the “best” result, and
2) continuously measure **output quality** and **cost** in production.

How would you extend this service? What components and decisions are critical (e.g., interfaces, fallbacks, evaluation, observability)?

## 7) AI usage log (optional)
- Tools used (if any):
- What you used them for:
- What you manually verified/changed:
