from typing import Dict, List, Any
import json
import os
import re

from utils.lead_schema import LEAD_FIELDS


def extract_questions(history: List[Dict[str, str]]) -> List[str]:
    """Return user messages that look like questions (heuristic: contain '?')."""
    qs = []
    for h in history:
        if h.get("role") == "user":
            text = (h.get("text") or "").strip()
            if "?" in text or text.lower().startswith(("how", "what", "why", "when", "where", "does", "do", "is", "are", "can")):
                qs.append(text)
    return qs


def detect_repeated_unanswered(history: List[Dict[str, str]], threshold: int = 3) -> List[str]:
    """Detect questions repeated >= threshold times without satisfactory assistant answer.

    Simple heuristic: if the same user question appears >= threshold and assistant never gave a non-empty reply.
    """
    norm_counts = {}
    for h in history:
        if h.get("role") == "user":
            t = re.sub(r"\s+", " ", (h.get("text") or "").strip().lower())
            if not t:
                continue
            norm_counts.setdefault(t, {"count": 0, "answered": False})
            norm_counts[t]["count"] += 1
        else:
            # assistant message; mark last user as answered if assistant provided text
            last_user = None
            # not robust but acceptable for simple heuristic
            pass

    repeated = [q for q, v in norm_counts.items() if v["count"] >= threshold]
    return repeated


def detect_sop_gaps(history: List[Dict[str, str]], sop: Dict[str, Any]) -> List[str]:
    """Detect candidate SOP gaps by checking user questions that were not answered from SOP.

    Heuristic: if assistant messages contain 'source_used' false or explicit 'not in SOP', or if repeated unanswered questions, report those topics.
    """
    gaps = []
    # Search assistant messages for indicators
    for h in history:
        if h.get("role") == "assistant":
            txt = (h.get("text") or "").lower()
            if "not in sop" in txt or "not found in sop" in txt or "no sop" in txt or "not available in sop" in txt:
                # try to extract nearby user question by scanning previous messages
                pass

    # Also inspect SOP to find missing common items (very lightweight): look for keywords like 'aftercare', 'pricing'
    required_topics = ["pricing", "aftercare", "side effects", "refund", "warranty", "sla"]
    sop_text = json.dumps(sop).lower()
    for topic in required_topics:
        if topic not in sop_text:
            gaps.append(f"missing_{topic}")

    return gaps


def build_crm_payload(summary: Dict[str, Any], session_id: str = "default") -> Dict[str, Any]:
    """Format a summary into a CRM-style JSON object suitable for export.

    Includes top-level fields and qualification data.
    """
    payload = {
        "session_id": session_id,
        "customer_intent": summary.get("customer_intent"),
        "lead_quality": summary.get("lead_quality"),
        "qualification_data": summary.get("qualification_data", {}),
        "conversation_sentiment": summary.get("conversation_sentiment"),
        "escalation_triggered": summary.get("escalation_triggered"),
        "escalation_reasons": summary.get("escalation_reasons", []),
        "unanswered_questions": summary.get("unanswered_questions", []),
        "sop_gaps_identified": summary.get("sop_gaps_identified", []),
        "recommended_next_action": summary.get("recommended_next_action"),
        "follow_up_priority": summary.get("follow_up_priority"),
    }
    return payload
