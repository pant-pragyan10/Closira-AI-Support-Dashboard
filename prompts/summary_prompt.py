def build_prompt(conversation_text: str, qualification: dict = None, escalations: list = None, sop: dict = None) -> str:
    """Build a strict summary prompt that outputs JSON-only structured conversation insights.

    The output JSON must include keys: customer_intent, lead_quality, qualification_data, conversation_sentiment,
    escalation_triggered, escalation_reasons, unanswered_questions, sop_gaps_identified,
    recommended_next_action, follow_up_priority
    """

    system = (
        "You are an AI operations assistant that produces concise, factual, and actionable session summaries. "
        "You must NOT hallucinate. Only report facts present in the conversation or explicitly mark unknowns as empty. "
        "Output must be valid JSON only with the keys: customer_intent, lead_quality, qualification_data, conversation_sentiment, "
        "escalation_triggered, escalation_reasons, unanswered_questions, sop_gaps_identified, recommended_next_action, follow_up_priority. "
    )

    conv = conversation_text
    qual = "\n".join([f"- {k}: {v}" for k, v in (qualification or {}).items()])
    esc = "\n".join([str(e) for e in (escalations or [])])
    sop_text = "\n".join([s.get("title","")+": "+s.get("content","") for s in (sop or {}).get("sections", [])])

    example_block = (
        f"Conversation:\n{conv}\n\nQualification:\n{qual}\n\nEscalations:\n{esc}\n\nSOP:\n{sop_text}\n"
    )

    return "\n\n".join([system, example_block])
