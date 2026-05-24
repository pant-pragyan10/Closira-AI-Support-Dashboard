from typing import Dict


def score_lead(collected: Dict[str, str]) -> str:
    """Simple heuristic lead scoring: high, medium, low."""
    # Basic rules: budget_interest and team_size are primary signals
    budget = (collected.get("budget_interest") or "").lower()
    team_size = collected.get("team_size") or ""

    # Parse team size into numeric if possible
    size = 0
    try:
        size = int(''.join(ch for ch in team_size if ch.isdigit()))
    except Exception:
        size = 0

    # Map budget keywords
    if any(k in budget for k in ["high", "$", "premium", "enterprise"]):
        budget_score = 2
    elif any(k in budget for k in ["medium", "mid", "moderate"]):
        budget_score = 1
    else:
        budget_score = 0

    # Team size score
    if size >= 50:
        size_score = 2
    elif size >= 10:
        size_score = 1
    else:
        size_score = 0

    total = budget_score + size_score
    if total >= 3:
        return "high"
    if total == 2:
        return "medium"
    return "low"


def build_lead_summary(collected: Dict[str, str]) -> Dict[str, str]:
    """Create a short lead profile summarizing collected fields and quality."""
    quality = score_lead(collected)
    return {
        "profile": collected,
        "lead_quality": quality,
        "summary": f"{collected.get('business_type','Unknown')} business with team size {collected.get('team_size','unknown')}. Budget interest: {collected.get('budget_interest','unspecified')}.",
    }
