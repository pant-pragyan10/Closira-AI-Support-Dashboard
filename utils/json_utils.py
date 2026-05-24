import json
import re
from typing import Any, Dict, Tuple


def extract_json_substring(text: str) -> str:
    """Try to extract the first JSON object/array substring from `text`.

    This helps when models wrap JSON in backticks or extra commentary.
    """
    # Try to find a {...} or [...] block
    brace_stack = []
    start_idx = None
    for i, ch in enumerate(text):
        if ch == "{":
            if start_idx is None:
                start_idx = i
            brace_stack.append(ch)
        elif ch == "}" and brace_stack:
            brace_stack.pop()
            if not brace_stack and start_idx is not None:
                return text[start_idx : i + 1]

    # If braces search failed, try regex for JSON-like substring
    m = re.search(r"\{.*\}", text, flags=re.DOTALL)
    if m:
        return m.group(0)

    m = re.search(r"\[.*\]", text, flags=re.DOTALL)
    if m:
        return m.group(0)

    return ""


def parse_json_robust(text: str) -> Tuple[Dict[str, Any], str]:
    """Attempt to parse `text` into JSON with graceful fallbacks.

    Returns a tuple `(obj, error)` where `obj` is the parsed JSON or an empty dict,
    and `error` is an error string (empty on success).
    """
    # Fast path: direct parse
    try:
        obj = json.loads(text)
    except Exception:
        obj = None

    # Try to extract JSON substring if direct parse failed
    if obj is None:
        candidate = extract_json_substring(text)
        if candidate:
            try:
                obj = json.loads(candidate)
            except Exception:
                obj = None

    # Try to clean common artifacts (triple backticks, leading text)
    if obj is None:
        cleaned = re.sub(r"```(json)?\n", "", text)
        cleaned = re.sub(r"```", "", cleaned)
        # Remove common prefixes like 'Answer:'
        cleaned = re.sub(r"^[A-Za-z ]+:\s*", "", cleaned, count=1)
        try:
            obj = json.loads(cleaned)
        except Exception:
            obj = None

    # If still no object, produce a safe structured fallback (do not return empty answer)
    if obj is None or not isinstance(obj, dict):
        fallback = {
            "answer": "I'm unable to process that response right now. I've flagged this for human review.",
            "confidence": 0.0,
            "source_used": False,
            "needs_escalation": True,
            "escalation_reason": "parsing_failure",
        }
        return fallback, ""  # no error to force agents to use the structured fallback

    # Validate required fields and inject defaults
    required = {
        "answer": "",
        "confidence": 0.0,
        "source_used": False,
        "needs_escalation": False,
    }
    for k, default in required.items():
        if k not in obj:
            obj[k] = default

    # Coerce types where sensible
    try:
        obj["confidence"] = float(obj.get("confidence", 0.0))
    except Exception:
        obj["confidence"] = 0.0
    obj["source_used"] = bool(obj.get("source_used", False))
    obj["needs_escalation"] = bool(obj.get("needs_escalation", False))

    return obj, ""
