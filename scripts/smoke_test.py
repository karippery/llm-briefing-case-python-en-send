import json

import httpx

TRANSCRIPT = """Project update:
- Action: Bob will prepare slides by Monday
- Risk: dependency on external vendor
"""


def main() -> None:
    payload = {"transcript": TRANSCRIPT}
    r = httpx.post("http://localhost:8000/v1/briefings", json=payload, timeout=5.0)
    print("status:", r.status_code)
    print(json.dumps(r.json(), indent=2))


if __name__ == "__main__":
    main()
