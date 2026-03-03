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
    end = text.rfind("}")
    
    if start == -1 or end == -1:
        raise ValueError("No JSON object found in output")
    
    json_str = text[start:end+1]

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