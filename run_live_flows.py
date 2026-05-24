import os
from dotenv import load_dotenv
import json
from utils.groq_client import GroqClient
from utils.parser import load_sop
from agents.faq_agent import FaqAgent
from agents.escalation_agent import EscalationAgent
from agents.qualification_agent import QualificationAgent
from agents.summary_agent import SummaryAgent
from utils.session_store import SessionStore
import time


def run_faq(client, sop):
    faq = FaqAgent(client=client, sop=sop)
    q = "How do I reset my password?"
    print("--- FAQ Test ---")
    start = time.perf_counter()
    out = faq.handle(q)
    elapsed = time.perf_counter() - start
    print(json.dumps(out, indent=2))
    print(f"Latency: {elapsed:.2f}s")


def run_escalation(client, sop):
    esc = EscalationAgent(client=client, sop=sop)
    convo = [
        {"role":"user","text":"I can't access my account and see unauthorized transactions."}
    ]
    print("--- Escalation Test ---")
    start = time.perf_counter()
    out = esc.handle(convo, last_agent_answer="", faq_confidence=0.6)
    elapsed = time.perf_counter() - start
    print(json.dumps(out, indent=2))
    print(f"Latency: {elapsed:.2f}s")


def run_qualification(client, sop):
    store = SessionStore(session_id="test_qual")
    store.clear()
    qual = QualificationAgent(client=client, sop=sop, memory=store)
    print("--- Qualification Test (multi-turn) ---")
    # Simulate user initiating
    resp1 = qual.handle("Hi, I'm interested in your product.")
    print("Agent asked:", resp1.get("next_question"))
    # Provide business_type
    resp2 = qual.handle("We are an e-commerce retailer.")
    print("Agent asked:", resp2.get("next_question"))
    # Provide team_size
    start = time.perf_counter()
    resp3 = qual.handle("About 20.")
    elapsed = time.perf_counter() - start
    print(json.dumps(resp3, indent=2))
    print(f"Latency (last turn): {elapsed:.2f}s")


def run_qualification_edge_tests(client, sop):
    print("--- Qualification Edge Cases ---")
    store = SessionStore(session_id="edge_case_1")
    store.clear()
    qual = QualificationAgent(client=client, sop=sop, memory=store)

    # Normal flow
    print("Normal flow:")
    print(qual.handle("Hello, I'm interested."))
    print(qual.handle("We're a small clinic."))
    print(qual.handle("About 5 staff."))

    # Contradictory update: user changes earlier answer
    store2 = SessionStore(session_id="edge_case_2")
    store2.clear()
    qual2 = QualificationAgent(client=client, sop=sop, memory=store2)
    print("Contradictory update flow:")
    print(qual2.handle("Hi, I want info."))
    print(qual2.handle("We are a clinic."))
    # User corrects business_type
    print("User corrects earlier field:")
    print(qual2.handle("Actually, we're a dental clinic."))

    # Skipped questions: user says 'I need to go' after first
    store3 = SessionStore(session_id="edge_case_3")
    store3.clear()
    qual3 = QualificationAgent(client=client, sop=sop, memory=store3)
    print("Skipped/abandoned flow:")
    print(qual3.handle("Hello"))
    print(qual3.handle("I need to go, bye"))

    # Vague answers
    store4 = SessionStore(session_id="edge_case_4")
    store4.clear()
    qual4 = QualificationAgent(client=client, sop=sop, memory=store4)
    print("Vague answers flow:")
    print(qual4.handle("Hi"))
    print(qual4.handle("Maybe in the future"))
    print(qual4.handle("We use some tools"))


def run_summary(client, sop):
    store = SessionStore(session_id="test_summary")
    # prepare a conversation
    conv = [
        {"role":"user","text":"Hi, we want help automating marketing."},
        {"role":"assistant","text":"What kind of business are you in?"},
        {"role":"user","text":"E-commerce"}
    ]
    summ = SummaryAgent(client=client, sop=sop, memory=store)
    print("--- Summary Test ---")
    start = time.perf_counter()
    out = summ.handle(conv, qualification={"business_type":"e-commerce"}, escalations=[] , session_id="test_summary")
    elapsed = time.perf_counter() - start
    print(json.dumps(out, indent=2))
    print(f"Latency: {elapsed:.2f}s")


def main():
    load_dotenv()
    api_key = os.getenv("GROQ_API_KEY")
    client = GroqClient(api_key=api_key)
    sop = load_sop("data/sop.json")

    run_faq(client, sop)
    run_escalation(client, sop)
    run_qualification(client, sop)
    run_qualification_edge_tests(client, sop)
    run_summary(client, sop)


if __name__ == "__main__":
    main()
