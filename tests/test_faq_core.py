import json
from utils.parser import load_sop
from agents.faq_agent import FaqAgent


def test_botox_pricing():
    sop = load_sop("data/sop.json")
    faq = FaqAgent(client=None, sop=sop)
    out = faq.handle("What are your Botox prices?")
    assert out["answer"].lower().startswith("from") or "£" in out["answer"]
    assert out["source_used"] is True
    assert out["needs_escalation"] is False
    assert out["confidence"] >= 0.8


def test_booking_info():
    sop = load_sop("data/sop.json")
    faq = FaqAgent(client=None, sop=sop)
    out = faq.handle("How can I book a consultation?")
    assert any(x in out["answer"].lower() for x in ("whatsapp", "website", "booking"))
    assert out["source_used"] is True
    assert out["needs_escalation"] is False


def test_clinic_hours():
    sop = load_sop("data/sop.json")
    faq = FaqAgent(client=None, sop=sop)
    out = faq.handle("What are your clinic hours?")
    assert "09:00" in out["answer"] or "09" in out["answer"]
    assert out["source_used"] is True


def test_unsupported_service_escalates():
    sop = load_sop("data/sop.json")
    faq = FaqAgent(client=None, sop=sop)
    out = faq.handle("Do you offer laser eye surgery?")
    assert out["answer"] == ""
    assert out["needs_escalation"] is True


def test_medical_question_escalates():
    sop = load_sop("data/sop.json")
    faq = FaqAgent(client=None, sop=sop)
    out = faq.handle("What medications should I avoid before Botox?")
    # Medical questions should escalate and not return pricing
    assert out["answer"] == "" or out["needs_escalation"] is True
