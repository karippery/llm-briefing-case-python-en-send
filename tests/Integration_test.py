
from tests.test_briefing import VALID_TRANSCRIPT


from fastapi.testclient import TestClient
from app.main import app 

client = TestClient(app)

class TestBriefingEndpoint:
    def test_happy_path_returns_200(self):
        resp = client.post("/v1/briefings", json={"transcript": VALID_TRANSCRIPT})
        assert resp.status_code == 200
        body = resp.json()
        assert "summary" in body
        assert "action_items" in body
        assert "meta" in body
        assert body["meta"]["provider"] == "stub"

    
    def test_request_id_echoed_in_header(self):
        resp = client.post(
            "/v1/briefings",
            json={"transcript": VALID_TRANSCRIPT},
            headers={"X-Request-Id": "test-id-42"},
        )
        assert resp.headers.get("x-request-id") == "test-id-42"

    def test_empty_transcript_returns_422(self):
        resp = client.post("/v1/briefings", json={"transcript": ""})
        assert resp.status_code == 422


    def test_bad_json_from_provider_returns_502(self, monkeypatch):
        """Simulate provider returning garbage; expect 502, not 500 or 200."""
        from app import main as main_module

        class GarbageProvider:
            name = "garbage"

            def generate(self, prompt: str) -> str:
                return "not json at all!!!"

        monkeypatch.setattr(main_module, "provider", GarbageProvider())
        resp = client.post("/v1/briefings", json={"transcript": VALID_TRANSCRIPT})
        assert resp.status_code == 502
        assert resp.json()["error"]["code"] == "parse_error"

    def test_provider_timeout_returns_503(self, monkeypatch):
        from app import main as main_module

        class TimeoutProvider:
            name = "timeouter"

            def generate(self, prompt: str) -> str:
                raise TimeoutError("boom")

        monkeypatch.setattr(main_module, "provider", TimeoutProvider())
        resp = client.post("/v1/briefings", json={"transcript": VALID_TRANSCRIPT})
        assert resp.status_code == 504


    def test_fenced_output_parsed_correctly(self):
        """Transcript containing [fence] triggers the stub's markdown-fenced output."""
        resp = client.post("/v1/briefings", json={"transcript": "[fence] standup notes"})
        assert resp.status_code == 200
        assert "summary" in resp.json()

    def test_no_stack_trace_in_error_response(self, monkeypatch):
        """500 errors must not leak tracebacks."""
        from app import main as main_module

        class BoomProvider:
            name = "boom"

            def generate(self, prompt: str) -> str:
                raise Exception("internal secret details")

        monkeypatch.setattr(main_module, "provider", BoomProvider())
        resp = client.post("/v1/briefings", json={"transcript": VALID_TRANSCRIPT})
        assert resp.status_code == 500
        text = resp.text
        assert "Traceback" not in text
        assert "internal secret details" not in text