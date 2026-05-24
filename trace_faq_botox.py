import json
from utils.parser import load_sop
from prompts.faq_prompt import build_prompt
from utils.groq_client import GroqClient
from utils.json_utils import parse_json_robust
from agents.faq_agent import FaqAgent
from agents.router_agent import RouterAgent
from utils.session_store import SessionStore
import os


def main():
    sop_path = "data/sop.json"
    sop = load_sop(sop_path)
    print("1) SOP raw source:")
    print(json.dumps(sop, indent=2))

    # Build serialized SOP text exactly as faq prompt does
    sop_text = "\n".join([f"- {s.get('title','')}: {s.get('content','')}" for s in sop.get('sections', [])])
    print("\n2) SOP serialized string:")
    print(sop_text)

    user_q = "What are your Botox prices?"
    prompt = build_prompt(user_q, sop=sop)
    system_prompt = "You are a strict JSON responder. Reply ONLY with valid JSON and nothing else. Use the SOP context when available."

    print("\n3) Exact prompt sent to Groq (system):")
    print(system_prompt)
    print("\n3b) Exact prompt sent to Groq (user):")
    print(prompt)

    # Initialize client if possible
    api_key = os.getenv("GROQ_API_KEY")
    client = GroqClient(api_key=api_key)

    print("\n4) Raw LLM output:")
    raw = ""
    try:
        raw = client.generate(system_prompt, prompt, temperature=0.2)
        print(raw)
    except Exception as e:
        print(f"[Groq call failed: {e}]")
        print("Raw response unavailable — falling back to Demo/mock output for parsing step.")
        # A conservative mock response that some models return when SOP absent
        raw = '{"answer": "", "confidence": 0.0, "source_used": false, "needs_escalation": true, "escalation_reason": "pricing not found"}'
        print(raw)

    print("\n5) Parsed JSON (parse_json_robust):")
    parsed, err = parse_json_robust(raw)
    print("Error:", err)
    print(json.dumps(parsed, indent=2))

    print("\n6) FAQAgent normalized output (internal logic):")
    faq = FaqAgent(client=client if getattr(client, 'client', None) else None, sop=sop)
    faq_out = faq.handle(user_q)
    print(json.dumps(faq_out, indent=2))

    print("\n7) Router output:")
    store = SessionStore(session_id="trace_botox")
    store.clear()
    router = RouterAgent(client=client if getattr(client, 'client', None) else None, sop=sop, memory=store)
    route_out = router.handle(user_q, session_store=store)
    print(json.dumps(route_out, indent=2))

    print("\n8) Final UI normalized output (response_normalizer):")
    # reuse normalize_response if available
    try:
        from utils.response_normalizer import normalize_response
        norm = normalize_response(route_out)
        print(json.dumps(norm, indent=2))
    except Exception as e:
        print(f"[normalize_response unavailable: {e}]")


if __name__ == '__main__':
    main()
