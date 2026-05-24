def build_prompt(previous_answers: dict, target_field: str) -> str:
    """Build a prompt asking the model to produce one concise question for the target_field.

    The model should return JSON only with keys: `next_question` (string), `field` (string).
    It should craft a polite, single question that references previous answers to sound natural.
    """
    prev_text = "\n".join([f"- {k}: {v}" for k, v in (previous_answers or {}).items() if v])
    system = (
        "You are a professional sales qualification assistant. Ask exactly one concise, polite, and clear question "
        "to gather the `target_field`. Avoid asking multiple questions. Do not repeat questions for fields that already have answers. "
        "Reference previous answers to make the question natural when helpful."
    )
    schema = "Output MUST be valid JSON only with keys: `next_question` and `field`. Do not output any other text."
    example = f"Target field: {target_field}\nPrevious answers:\n{prev_text}\n"
    return "\n\n".join([system, schema, example])
