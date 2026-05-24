from typing import Any, Dict, List
from prompts.summary_prompt import build_prompt
from utils.json_utils import parse_json_robust
from utils.summary_utils import detect_repeated_unanswered, detect_sop_gaps, build_crm_payload
from utils.lead_summary import build_lead_summary
from utils.escalation_logger import EscalationLogger
from utils.logger import ConversationLogger
from utils.escalation_utils import simple_sentiment_score
import os


class SummaryAgent:
    """Summary & Insights agent that produces structured end-of-session reports.

    Steps:
    1. Gather full conversation history, qualification memory, and escalation logs.
    2. Call the LLM with a strict JSON-only prompt to extract customer intent and recommendations.
    3. Merge LLM output with heuristic detectors (SOP gaps, repeated unanswered questions).
    4. Save the structured summary via analytics logger.
    """

    def __init__(self, client: Any = None, sop: Dict = None, memory: Any = None):
        self.client = client
        self.sop = sop or {}
        self.memory = memory
        self.summary_logger = EscalationLogger(path="logs/summaries.json")
        self.conv_logger = ConversationLogger("logs/conversations.json")

    def handle(self, conversation: List[Dict[str, str]], qualification: Dict[str, str] = None, escalations: List[Dict] = None, session_id: str = "default") -> Dict:
        # Prepare context
        conv_text = "\n".join([f"{m.get('role')}: {m.get('text')}" for m in (conversation or [])])

        prompt = build_prompt(conv_text, qualification=qualification or {}, escalations=escalations or [], sop=self.sop)

        system_prompt = "You are a summary assistant that outputs strict JSON only. Extract customer_intent, qualification_data, sentiment, and recommended action."

        raw = ""
        if self.client:
            raw = self.client.generate(system_prompt, prompt, temperature=0.2)

        parsed, err = parse_json_robust(raw)

        # Start base summary from parsed model output when available
        summary = parsed if parsed and not err else {}

        # Ensure keys exist
        # Ensure keys exist with sensible default types
        summary.setdefault("customer_intent", None)
        summary.setdefault("lead_quality", "")
        summary.setdefault("qualification_data", {})
        summary.setdefault("conversation_sentiment", "")
        summary.setdefault("escalation_triggered", False)
        summary.setdefault("escalation_reasons", [])
        summary.setdefault("unanswered_questions", [])
        summary.setdefault("sop_gaps_identified", [])
        summary.setdefault("recommended_next_action", None)
        summary.setdefault("follow_up_priority", None)

        # Heuristic SOP gaps and repeated unanswered detection
        repeated = detect_repeated_unanswered(conversation)
        gaps = detect_sop_gaps(conversation, self.sop)

        # Merge heuristics conservatively
        if repeated and not summary.get("unanswered_questions"):
            summary["unanswered_questions"] = repeated
        if gaps and not summary.get("sop_gaps_identified"):
            summary["sop_gaps_identified"] = gaps

        # Populate qualification_data if missing
        # Ensure qualification_data present (prefer explicit param, then parsed, then memory)
        if not summary.get("qualification_data"):
            if qualification:
                summary["qualification_data"] = qualification
            elif self.memory:
                try:
                    summary["qualification_data"] = self.memory.get_lead() or {}
                except Exception:
                    summary["qualification_data"] = {}

        # Populate lead_quality from qualification_data heuristics if missing
        if not summary.get("lead_quality"):
            try:
                lq = build_lead_summary(summary.get("qualification_data", {})).get("lead_quality")
                summary["lead_quality"] = lq or "unknown"
            except Exception:
                summary["lead_quality"] = "unknown"

        # Fill conversation_sentiment conservatively using a lightweight heuristic if missing
        if not summary.get("conversation_sentiment"):
            try:
                sentiment_label, sentiment_score = simple_sentiment_score(conv_text)
                summary["conversation_sentiment"] = sentiment_label
            except Exception:
                summary["conversation_sentiment"] = "neutral"

        # Default recommended action when escalation triggered
        if summary.get("escalation_triggered") and not summary.get("recommended_next_action"):
            summary["recommended_next_action"] = "Human agent follow-up"
            summary["follow_up_priority"] = summary.get("follow_up_priority") or "high"

        # Save structured summary
        self.summary_logger.log({"session_id": session_id, "summary": summary})

        return summary

