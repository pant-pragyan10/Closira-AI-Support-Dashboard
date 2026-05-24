def build_prompt(conversation: list, last_agent_answer: str = "", faq_confidence: float = 1.0, sop: dict = None) -> str:
    """Build a strict prompt for escalation reasoning.

    Expects `conversation` as a list of {role, text} dicts. The model must output JSON only with keys:
    - needs_escalation (bool)
    - escalation_score (0.0-1.0)
    - reason (list of strings)
    - recommended_action (string)
    - customer_sentiment (string: neutral|frustrated|angry)
    - priority (low|medium|high|critical)

    The prompt must analyze emotional tone, safety, SOP coverage, uncertainty, repetition, and risk.
    """

    sop_text = "\n".join([
        f"- {s.get('title','')}: {s.get('content','') }" for s in (sop or {}).get("sections", [])
    ])

    conv_text = "\n".join([f"{m.get('role')}: {m.get('text')}" for m in (conversation or [])[-20:]])

    system = (
        "You are an escalation intelligence assistant. Analyze the provided conversation and the last agent answer. "
        "Your job is to decide whether the conversation should be handed to a human and to explain the reasons. "
        "Do NOT hallucinate facts; base decisions on conversation content, SOP coverage, and confidence signals."
    )

    schema = (
        "Output MUST be valid JSON only with keys: needs_escalation (bool), escalation_score (float 0-1), reason (list of strings), "
        "recommended_action (string), customer_sentiment (string), priority (string). Do not output extra text."
    )

    example = (
        f"SOP:\n{sop_text}\nConversation:\n{conv_text}\nLast agent answer:\n{last_agent_answer}\nFAQ confidence:{faq_confidence}\n"
    )

    prompt = "\n\n".join([system, schema, example])
    return prompt
