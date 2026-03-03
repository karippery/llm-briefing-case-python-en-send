from app.llm.provider import RetryingProvider, StubProvider
from app.models import ActionItem
import pytest
from pydantic import ValidationError
from app.models import BriefingResponse


class TestActionItemModel:
    def test_empty_due_date_normalised_to_none(self):
        item = ActionItem(owner="Bob", task="Write docs", due_date="")
        assert item.due_date is None

    def test_valid_due_date_kept(self):
        item = ActionItem(owner="Bob", task="Write docs", due_date="2025-01-01")
        assert item.due_date == "2025-01-01"


class TestBriefingResponseFromUntrusted:
    def _base(self, **overrides):
        d = {
            "summary": "Meeting summary",
            "action_items": [],
            "risks": [],
            "next_steps": [],
            "meta": {"provider": "stub", "request_id": "req-1", "warnings": []},
        }
        d.update(overrides)
        return d

    def test_valid_data_passes(self):
        br = BriefingResponse.from_untrusted(self._base())
        assert br.summary == "Meeting summary"

    def test_missing_risks_defaulted(self):
        data = self._base()
        del data["risks"]
        br = BriefingResponse.from_untrusted(data)
        assert br.risks == []

    def test_non_dict_raises(self):
        with pytest.raises((ValueError, ValidationError)):
            BriefingResponse.from_untrusted(["not", "a", "dict"])

    def test_string_risks_coerced_to_list(self):
        br = BriefingResponse.from_untrusted(self._base(risks="budget risk"))
        assert br.risks == ["budget risk"]

class TestRetryingProvider:

    def test_succeeds_on_first_attempt(self):
        stub = StubProvider()
        rp = RetryingProvider(inner=stub, max_attempts=3, base_delay=0)
        result = rp.generate("Hello Transcript: world")
        assert isinstance(result, str)

    def test_retries_on_timeout_then_raises(self):
        stub = StubProvider()
        rp = RetryingProvider(inner=stub, max_attempts=2, base_delay=0)
        with pytest.raises(RuntimeError, match="failed after"):
            rp.generate("[timeout] Transcript: test")

    def test_non_transient_error_not_retried(self):
        """A non-transient exception must propagate immediately (no retry)."""
        call_count = 0

        class BombProvider:
            name = "bomb"

            def generate(self, prompt: str) -> str:
                nonlocal call_count
                call_count += 1
                raise ValueError("bad input")

        rp = RetryingProvider(inner=BombProvider(), max_attempts=3, base_delay=0)
        with pytest.raises(ValueError):
            rp.generate("anything")
        assert call_count == 1