import re


def is_gibberish(text: str) -> bool:
    if not text or not text.strip():
        return True
    t = text.strip()
    # too short
    if len(t.split()) <= 1:
        return True
    # proportion of tokens with vowels
    tokens = re.findall(r"[A-Za-z]+", t)
    if not tokens:
        return True
    vowel_tokens = [tok for tok in tokens if re.search(r"[aeiou]", tok, re.I)]
    if len(vowel_tokens) / len(tokens) < 0.5:
        return True
    # too many punctuation/non-alnum
    nonalnum = len([ch for ch in t if not ch.isalnum() and not ch.isspace()])
    if nonalnum / max(1, len(t)) > 0.3:
        return True
    return False


def is_clarification_needed(text: str) -> bool:
    # Simple heuristic: short, vague questions lacking keywords
    if not text or len(text.split()) < 3:
        return True
    # lacks a verb or noun? (very basic)
    if not re.search(r"\b(is|are|do|does|what|how|where|when|who|why|can|could|should|would)\b", text, re.I):
        # but if contains business keywords, not clarification
        if re.search(r"clinic|business|team|staff|price|book|booking|appointment|hours|schedule", text, re.I):
            return False
        return True
    return False
