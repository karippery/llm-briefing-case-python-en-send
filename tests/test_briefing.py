from fastapi.testclient import TestClient
import app
import json
import pytest
from app.llm.parsing import parse_llm_output

client = TestClient(app)

VALID_TRANSCRIPT = "Alice will send the report by Friday. Risk: budget overrun."

class TestParseCleanJson:
    def test_plain_json(self):
        raw = json.dumps({"summary": "s", "action_items": [], "risks": [], "next_steps": []})
        result = parse_llm_output(raw)
        assert result["summary"] == "s"

    def test_fenced_json(self):
            inner = json.dumps({"summary": "fenced", "action_items": [], "risks": [], "next_steps": []})
            result = parse_llm_output(f"```json\n{inner}\n```")
            assert result["summary"] == "fenced"

    def test_preamble_then_json(self):
        inner = json.dumps({"summary": "p", "action_items": [], "risks": [], "next_steps": []})
        result = parse_llm_output(f"Sure, here is it:\n{inner}")
        assert result["summary"] == "p"
    
    def test_trailing_comma_fixed(self):
        raw = '{"summary": "s", "action_items": [], "risks": [], "next_steps": [],}'
        result = parse_llm_output(raw)
        assert result["summary"] == "s"
    
    def test_unmatched_brace_raises(self):
        with pytest.raises(ValueError, match="[Uu]nmatched"):
            parse_llm_output('{"summary": "s"')