from typing import List, Dict, Tuple
import re

ANGER_KEYWORDS = [
    "angry",
    "outrage",
    "ridiculous",
    "furious",
    "you people",
    "never help",
    "sucks",
    "hate",
    "outrageous",
    "this is unacceptable",
]

FRUSTRATION_KEYWORDS = [
    "frustrat",
    "annoy",
    "upset",
    "not helpful",
    "you are not",
    "youre not",
    "not answered",
    "not answering",
]


def simple_sentiment_score(text: str) -> Tuple[str, float]:
    """Very small lexicon-based sentiment detector returning (label, score).

    Score between 0.0 (calm/neutral) and 1.0 (very angry).
    This is intentionally conservative — used as a heuristic signal joined with LLM reasoning.
    """
    t = (text or "").lower()
    score = 0.0
    for k in ANGER_KEYWORDS:
        if k in t:
            score = max(score, 0.9)
    for k in FRUSTRATION_KEYWORDS:
        if k in t:
            score = max(score, 0.6)

    if score >= 0.9:
        return "angry", score
    if score >= 0.6:
        return "frustrated", score
    return "neutral", 0.0


def repetition_detector(history: List[Dict[str, str]], window: int = 6) -> Tuple[bool, int]:
    """Detect repeated similar user messages in recent history.

    Returns (is_repeated, repeat_count)
    """
    # Look at last `window` messages, count identical normalized user texts
    recent = [h for h in history[-window:] if h.get("role") == "user"]
    norm = [re.sub(r"\s+", " ", (r.get("text","") or "").strip().lower()) for r in recent]
    counts = {}
    maxc = 0
    for n in norm:
        if not n:
            continue
        counts[n] = counts.get(n, 0) + 1
        maxc = max(maxc, counts[n])
    return (maxc >= 3, maxc)


def aggregate_heuristics(history: List[Dict[str, str]], last_agent_confidence: float = 1.0, qualification_context: Dict = None) -> Tuple[float, List[str]]:
    """Compute a heuristic escalation score (0-1) and reason list based on signals.

    Signals include: angry/frustrated text, low agent confidence, repeated questions, explicit request for human, and qualification flags.
    """
    reasons = []
    score = 0.0

    # Check latest user message
    if not history:
        return 0.0, []
    last_user = None
    for h in reversed(history):
        if h.get("role") == "user":
            last_user = h.get("text", "")
            break

    if last_user:
        sentiment_label, sentiment_score = simple_sentiment_score(last_user)
        if sentiment_label != "neutral":
            reasons.append(f"{sentiment_label} sentiment")
            score = max(score, sentiment_score)

        # explicit human request heuristics
        explicit = ["human", "someone real", "representative", "supervisor", "manager", "speak to someone"]
        if any(word in last_user.lower() for word in explicit):
            reasons.append("explicit_human_request")
            score = max(score, 0.95)

    # Low confidence
    try:
        if last_agent_confidence is not None and last_agent_confidence < 0.5:
            reasons.append("low_confidence")
            score = max(score, 0.8)
        elif last_agent_confidence is not None and last_agent_confidence < 0.75:
            reasons.append("moderate_confidence")
            score = max(score, 0.6)
    except Exception:
        pass

    # Repetition detection
    repeated, count = repetition_detector(history)
    if repeated:
        reasons.append(f"repeated_questions_{count}")
        score = max(score, 0.85)

    # Qualification context flags
    if qualification_context and qualification_context.get("escalate_flag"):
        reasons.append("qualification_flagged")
        score = max(score, 0.8)

    return score, reasons
