from typing import Any
from .faq_agent import FaqAgent
from .qualification_agent import QualificationAgent
from .escalation_agent import EscalationAgent
from .summary_agent import SummaryAgent

AGENTS = {
    "faq": FaqAgent,
    "qualification": QualificationAgent,
    "escalation": EscalationAgent,
    "summary": SummaryAgent,
}

def route_message(agent_name: str, message: str, **kwargs) -> str:
    agent_cls = AGENTS.get(agent_name)
    if not agent_cls:
        return "Unknown agent"
    agent = agent_cls(**kwargs)
    return agent.handle(message)
