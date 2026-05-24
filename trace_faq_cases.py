import json
from utils.parser import load_sop
from agents.faq_agent import FaqAgent
from agents.router_agent import RouterAgent
from utils.groq_client import GroqClient
from utils.session_store import SessionStore
import os


def run_case(q, client, sop, session_store=None):
    print(f"\n--- Question: {q}")
    faq = FaqAgent(client=client if getattr(client, 'client', None) else None, sop=sop)
    out = faq.handle(q)
    print(json.dumps(out, indent=2))
    # run via router
    router = RouterAgent(client=client if getattr(client, 'client', None) else None, sop=sop, memory=session_store)
    route = router.handle(q, session_store=session_store or SessionStore(session_id="trace_cases"))
    print("Router output:")
    print(json.dumps(route, indent=2))


def main():
    sop = load_sop("data/sop.json")
    api_key = os.getenv("GROQ_API_KEY")
    client = GroqClient(api_key=api_key)
    session_store = SessionStore(session_id="trace_cases")
    session_store.clear()

    cases = [
        "What are your Botox prices?",
        "How can I book a consultation?",
        "What are your clinic hours?",
        "Do you offer laser eye surgery?",
        "What medications should I avoid before Botox?",
    ]

    for q in cases:
        run_case(q, client, sop, session_store)


if __name__ == '__main__':
    main()
