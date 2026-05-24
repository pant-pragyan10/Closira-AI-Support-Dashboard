def build_prompt(user_message: str, sop: dict = None) -> str:
    """Build a strict system+user prompt that forces JSON-only responses grounded in the SOP.

    The prompt enforces:
    - ONLY answer using the provided SOP text.
    - DO NOT hallucinate or invent facts not present in the SOP.
    - OUTPUT must be valid JSON matching the schema exactly.
    - Include confidence as a float between 0.0 and 1.0.
    - Set `source_used` true only when the answer cites SOP content.
    - Set `needs_escalation` true when the model is uncertain or the question is unsafe/out-of-scope.
    - Use professional SMB customer support tone.
    """

    # Render SOP into a more semantic, human-friendly context block to aid grounding.
    parts = []
    for s in (sop or {}).get("sections", []):
        title = s.get("title", "").strip()
        content = s.get("content", "").strip()
        # If content uses semicolons to separate items, expand into bullets for clarity.
        if ";" in content:
            items = [it.strip() for it in content.split(";") if it.strip()]
            bullet_list = "\n".join([f"  - {it}" for it in items])
            parts.append(f"{title}:\n{bullet_list}")
        else:
            parts.append(f"{title}: {content}")
    sop_text = "\n\n".join(parts)

    system = (
        "You are a strict FAQ assistant for Closira. You must only use the SOP context provided. "
        "You are forbidden from inventing information or hallucinating. If the SOP does not contain an answer,"
        " you must set `answer` to an empty string, `source_used` to false, and `needs_escalation` to true with an appropriate `escalation_reason`."
    )

    schema_instructions = (
        "Output MUST be valid JSON only, with the exact keys: `answer` (string), `confidence` (number 0.0-1.0), "
        "`source_used` (boolean), `needs_escalation` (boolean), `escalation_reason` (string or null). "
        "Do NOT output any explanation or extra text."
    )

    escalation_triggers = (
        "Escalate (set `needs_escalation` true) when: the SOP lacks the information, the user requests medical/legal advice, "
        "the user shows angry or abusive tone, or the user asks for pricing negotiation beyond listed prices. Do NOT escalate if the SOP contains explicit pricing; instead answer directly using that pricing information."
    )

    scoring_rules = (
        "Provide a `confidence` score between 0.0 and 1.0 representing the model's estimated factuality relative to the SOP. "
        "Use values >= 0.8 for high-confidence direct SOP matches, 0.5-0.79 for partial matches, and <0.5 for likely unknowns."
    )

    user_block = f"User question: {user_message}\n"

    prompt = "\n\n".join([system, sop_text, schema_instructions, escalation_triggers, scoring_rules, user_block])
    return prompt
