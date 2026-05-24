from typing import Any, Dict, Tuple
from .faq_agent import FaqAgent
from .qualification_agent import QualificationAgent
from .escalation_agent import EscalationAgent
from .summary_agent import SummaryAgent
from utils.lead_schema import missing_fields


class RouterAgent:
    """Automatic router/orchestrator that selects appropriate agent.

    Routing rules (simplified, extensible):
    - If a qualification is in-progress (session last_asked) -> QualificationAgent
    - If user explicitly requests a summary -> SummaryAgent
    - If message strongly indicates qualification (business/team) -> QualificationAgent
    - Otherwise default to FAQAgent
    After primary agent returns, if result indicates escalation, run EscalationAgent and merge decisions.
    """

    def __init__(self, client: Any = None, sop: Dict = None, memory: Any = None):
        self.client = client
        self.sop = sop or {}
        self.memory = memory
        # Agents lazily created
        self._faq = None
        self._qual = None
        self._esc = None
        self._summ = None

    def _faq_agent(self):
        if self._faq is None:
            self._faq = FaqAgent(client=self.client, sop=self.sop, memory=self.memory)
        return self._faq

    def _qual_agent(self):
        if self._qual is None:
            self._qual = QualificationAgent(client=self.client, sop=self.sop, memory=self.memory)
        return self._qual

    def _esc_agent(self):
        if self._esc is None:
            self._esc = EscalationAgent(client=self.client, sop=self.sop, memory=self.memory)
        return self._esc

    def _summ_agent(self):
        if self._summ is None:
            self._summ = SummaryAgent(client=self.client, sop=self.sop, memory=self.memory)
        return self._summ

    def _looks_like_qualification(self, text: str, lead: Dict) -> bool:
        t = (text or "").lower()
        if lead and missing_fields(lead):
            # If user mentions business/team keywords, prefer qualification
            if any(k in t for k in ("business", "clinic", "team", "staff", "employees", "we are")):
                return True
        return False

    def _is_summary_request(self, text: str) -> bool:
        t = (text or "").lower()
        return any(k in t for k in ("summarize", "summary", "summarise", "recap"))

    def handle(self, message: str, session_store=None) -> Dict:
        # session_store: SessionStore
        lead = {}
        last_asked, _ = (None, None)
        if session_store:
            lead = session_store.get_lead() or {}
            last_asked, _ = session_store.get_last_asked()

        # 1) Continue active qualification if present
        if last_asked:
            out = self._qual_agent().handle(message)
            return {**out, "agent_used": "qualification"}

        # 2) Explicit summary request
        if self._is_summary_request(message):
            # Build summary using full conversation
            history = session_store.get_history() if session_store else []
            out = self._summ_agent().handle(history, qualification=lead or {}, escalations=[], session_id=(session_store.session_id if session_store else "default"))
            return {"assistant_text": out.get("recommended_next_action") or "Summary generated.", "agent_used": "summary", "confidence": 1.0, "needs_escalation": False, "metadata": {"summary": out}}

        # 3) Qualification intent detection
        if self._looks_like_qualification(message, lead):
            out = self._qual_agent().handle(message)
            # qualification agent returns structured dict (next_question etc.)
            # map to assistant-visible text
            assistant_text = out.get("next_question") or out.get("answer") or ""
            return {"assistant_text": assistant_text, "agent_used": "qualification", "confidence": out.get("lead_quality") or 0.0, "needs_escalation": out.get("needs_escalation", False), "metadata": out}

        # 4) Default FAQ
        faq_out = self._faq_agent().handle(message)
        assistant_text = faq_out.get("answer") or faq_out.get("next_question") or ""

        # After FAQ, consider escalation internally
        if faq_out.get("needs_escalation") and session_store is not None:
            conv = session_store.get_history()
            esc_report = self._esc_agent().handle(conv, last_agent_answer=faq_out.get("answer") or assistant_text, faq_confidence=faq_out.get("confidence", 0.0))
            # If escalation required by heuristics and model, mark needs_escalation
            needs_esc = esc_report.get("needs_escalation", False)
            metadata = {"faq": faq_out, "escalation": esc_report}
            return {"assistant_text": assistant_text or "", "agent_used": "faq", "confidence": faq_out.get("confidence", 0.0), "needs_escalation": needs_esc, "metadata": metadata}

        return {"assistant_text": assistant_text or "", "agent_used": "faq", "confidence": faq_out.get("confidence", 0.0), "needs_escalation": faq_out.get("needs_escalation", False), "metadata": {"faq": faq_out}}
