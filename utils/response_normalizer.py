from typing import Any, Dict


def normalize_response(response: Any) -> Dict[str, Any]:
    """Normalize various agent responses into a standard schema consumed by the UI.

    Output keys:
    - assistant_text: str
    - confidence: float (0.0-1.0)
    - needs_escalation: bool
    - escalation_reason: str or None
    - metadata: dict (other keys preserved)
    """
    out = {
        "assistant_text": "",
        "confidence": 0.0,
        "needs_escalation": False,
        "escalation_reason": None,
        "metadata": {},
    }

    if response is None:
        return out

    # If response is a string, set as assistant_text
    if isinstance(response, str):
        out["assistant_text"] = response
        out["confidence"] = 1.0
        return out

    if isinstance(response, dict):
        # assistant-visible text may be in 'answer' or 'next_question' or nested
        assistant_text = response.get("answer") or response.get("next_question") or response.get("assistant_text") or ""
        if isinstance(assistant_text, (list, dict)):
            # fallback to JSON string
            import json

            try:
                assistant_text = json.dumps(assistant_text)
            except Exception:
                assistant_text = str(assistant_text)

        out["assistant_text"] = assistant_text or "[No assistant response — check logs]"

        try:
            out["confidence"] = float(response.get("confidence", response.get("score", 0.0) or 0.0))
        except Exception:
            out["confidence"] = 0.0

        out["needs_escalation"] = bool(response.get("needs_escalation", False))
        out["escalation_reason"] = response.get("escalation_reason") if response.get("escalation_reason") else None

        # metadata: keep everything else
        meta = dict(response)
        for k in ("answer", "next_question", "assistant_text", "confidence", "score", "needs_escalation", "escalation_reason"):
            meta.pop(k, None)
        out["metadata"] = meta

        # Normalize confidence bounds
        try:
            if out["confidence"] < 0.0:
                out["confidence"] = 0.0
            if out["confidence"] > 1.0:
                out["confidence"] = 1.0
        except Exception:
            out["confidence"] = 0.0

        return out

    # Other types: stringify
    try:
        out["assistant_text"] = str(response)
        out["confidence"] = 1.0
    except Exception:
        pass
    return out
