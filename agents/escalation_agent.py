from typing import Any, Dict, List
from prompts.escalation_prompt import build_prompt
from utils.json_utils import parse_json_robust
from utils.escalation_utils import aggregate_heuristics, simple_sentiment_score
from utils.escalation_logger import EscalationLogger


class EscalationAgent:
    """Escalation intelligence engine combining heuristics and LLM reasoning.

    Input:
    - conversation: list of {role, text}
    - last_agent_answer: str
    - faq_confidence: float (0-1)
    - sop: dict

    Output: structured escalation decision dict
    """

    def __init__(self, client: Any = None, sop: Dict = None, memory: Any = None):
        self.client = client
        self.sop = sop or {}
        self.memory = memory
        self.logger = EscalationLogger()

    def handle(self, conversation: List[Dict[str, str]], last_agent_answer: str = "", faq_confidence: float = 1.0) -> Dict:
        # Compute heuristic score and reasons
        h_score, h_reasons = aggregate_heuristics(conversation, last_agent_confidence=faq_confidence)

        # Local sentiment label (helpful for priority mapping)
        last_user = ""
        for m in reversed(conversation):
            if m.get("role") == "user":
                last_user = m.get("text", "")
                break
        sentiment_label, _ = simple_sentiment_score(last_user)

        # Build LLM prompt for deeper reasoning
        prompt = build_prompt(conversation, last_agent_answer=last_agent_answer, faq_confidence=faq_confidence, sop=self.sop)
        system_prompt = "You are an escalation analyst. Provide a JSON-only decision about whether to escalate."
        model_output = ""
        if self.client:
            model_output = self.client.generate(system_prompt, prompt, temperature=0.2)

        parsed, perr = parse_json_robust(model_output)

        # Start with heuristic defaults
        needs_escalation = False
        escalation_score = h_score
        reasons = list(h_reasons)
        recommended_action = "none"
        priority = "low"

        if parsed and not perr:
            # Merge model judgment with heuristics conservatively
            try:
                model_score = float(parsed.get("escalation_score", 0.0))
            except Exception:
                model_score = 0.0
            escalation_score = max(escalation_score, model_score)
            # Merge reason lists
            m_reasons = parsed.get("reason", []) or []
            for r in m_reasons:
                if r not in reasons:
                    reasons.append(r)

            needs_escalation = bool(parsed.get("needs_escalation", False)) or escalation_score >= 0.75
            recommended_action = parsed.get("recommended_action") or ("human_handoff" if needs_escalation else "monitor")
            priority = parsed.get("priority") or self._map_priority(escalation_score, reasons)
        else:
            # No model judgment; use heuristics
            needs_escalation = escalation_score >= 0.75
            recommended_action = "human_handoff" if needs_escalation else "monitor"
            priority = self._map_priority(escalation_score, reasons)

        report = {
            "needs_escalation": needs_escalation,
            "escalation_score": round(float(escalation_score), 2),
            "reason": reasons,
            "recommended_action": recommended_action,
            "customer_sentiment": sentiment_label,
            "priority": priority,
        }

        # Log the escalation decision with conversation snapshot
        self.logger.log({"report": report, "conversation_snapshot": conversation[-20:], "last_agent_answer": last_agent_answer})

        return report

    def _map_priority(self, score: float, reasons: List[str]) -> str:
        if score >= 0.9 or any("medical" in r or "safety" in r for r in reasons):
            return "critical"
        if score >= 0.75:
            return "high"
        if score >= 0.5:
            return "medium"
        return "low"

