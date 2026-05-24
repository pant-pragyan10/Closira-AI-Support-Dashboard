
from typing import Any, Dict
from prompts.faq_prompt import build_prompt
from utils.json_utils import parse_json_robust
import os


class FaqAgent:
    """Production-style FAQ agent:

    - Builds a strict prompt restricting answers to the SOP
    - Requests low-temperature deterministic generation
    - Parses and validates JSON outputs
    - Applies confidence-based escalation rules
    """

    def __init__(self, client: Any = None, sop: dict = None, memory: Any = None):
        self.client = client
        self.sop = sop or {}
        self.memory = memory
        # Configurable threshold via env var for easy tuning
        try:
            self.confidence_threshold = float(os.getenv("FAQ_CONFIDENCE_THRESHOLD", "0.7"))
        except Exception:
            self.confidence_threshold = 0.7

    def handle(self, message: str) -> Dict:
        prompt = build_prompt(message, sop=self.sop)

        # Low temperature for deterministic answers anchored to SOP
        system_prompt = "You are a strict JSON responder. Reply ONLY with valid JSON and nothing else. Use the SOP context when available."
        raw = self.client.generate(system_prompt, prompt, temperature=0.2) if self.client else ""

        # Parse robustly
        parsed, err = parse_json_robust(raw)
        if err:
            # Graceful fallback: escalate to human if parsing fails
            return {
                "answer": "",
                "confidence": 0.0,
                "source_used": False,
                "needs_escalation": True,
                "escalation_reason": f"parsing_failure: {err}",
                "raw_model_output": raw,
            }

        # Validate fields and coercion
        answer = parsed.get("answer", "")
        try:
            confidence = float(parsed.get("confidence", 0.0))
        except Exception:
            confidence = 0.0
        source_used = bool(parsed.get("source_used", False))
        needs_escalation = bool(parsed.get("needs_escalation", False))
        escalation_reason = parsed.get("escalation_reason") if parsed.get("escalation_reason") else None

        # Additional deterministic escalation logic: if confidence below threshold or source not used
        if confidence < self.confidence_threshold or not source_used:
            needs_escalation = True
            if not escalation_reason:
                escalation_reason = "low_confidence_or_no_source"

        # Special-case pricing inquiries: if model indicates escalation due to missing pricing,
        # provide a safe non-hallucinated fallback message instead of immediate escalation.
        # This avoids blank assistant bubbles for common commercial questions.
        if needs_escalation and escalation_reason:
            low_reason = str(escalation_reason).lower()
            if any(k in low_reason for k in ("price", "pricing", "pricing information")):
                # Provide a conservative fallback suggesting contact with sales/support
                answer = (
                    "I don't have pricing details in our documentation. "
                    "Please contact our sales team or use the contact form for current pricing."
                )
                confidence = max(confidence, 0.5)
                needs_escalation = False
                escalation_reason = None

        # Ensure confidence in [0.0,1.0]
        confidence = max(0.0, min(1.0, confidence))

        return {
            "answer": answer,
            "confidence": confidence,
            "source_used": source_used,
            "needs_escalation": needs_escalation,
            "escalation_reason": escalation_reason,
        }

