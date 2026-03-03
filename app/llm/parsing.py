import json
import re
from typing import Any, Dict

def parse_llm_output(raw_text: str) -> Dict[str, Any]:
    if not raw_text or not raw_text.strip():
        raise ValueError("Empty model output")

    # 1. Extract content between triple backticks (if present)
    # Search rather than Match to ignore preambles/postscripts
    fence_match = re.search(r"```(?:json)?\s*(.*?)\s*```", raw_text, re.DOTALL | re.IGNORECASE)
    text = fence_match.group(1) if fence_match else raw_text.strip()

    # 2. Basic cleaning of common LLM artifacts
    # Strip trailing commas before closing braces/brackets
    text = re.sub(r",\s*([\]}])", r"\1", text)

    # 3. Attempt to find the JSON structure
    # This finds the first '{' and the last '}'
    start = text.find("{")
    if start == -1:
        raise ValueError("No JSON object found in output")
    
    # Count braces to find the matching closing brace for the first '{'
    depth = 0
    in_string = False
    escape_next = False

    for i, ch in enumerate(text[start:], start=start):
        # Previous character was a backslash inside a string — skip this char
        if escape_next:
            escape_next = False
            continue

        # Backslash inside a string escapes the next character
        if ch == "\\" and in_string:
            escape_next = True
            continue

        # Toggle string mode on unescaped double-quote
        if ch == '"':
            in_string = not in_string
            continue

        # While inside a string, braces are just data — ignore them
        if in_string:
            continue

        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                json_str = text[start : i + 1]
                break

    else:
        raise ValueError("Unmatched braces in JSON output")

    # 4. Final Parse
    try:
        result = json.loads(json_str)
    except json.JSONDecodeError:
        # Fallback: only try the risky single-quote fix if double quotes are missing
        if '"' not in json_str and "'" in json_str:
            try:
                # Replace single quotes with double quotes, then try again
                result = json.loads(json_str.replace("'", '"'))
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON format: {e}")
        else:
            raise ValueError("LLM returned malformed JSON that couldn't be auto-fixed.")

    if not isinstance(result, dict):
        raise ValueError(f"Expected dict, got {type(result).__name__}")

    return result