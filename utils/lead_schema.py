from typing import Dict, List

LEAD_FIELDS = [
    "business_type",
    "team_size",
    "current_tools",
    "customer_goals",
    "budget_interest",
    "contact_method",
]


def missing_fields(collected: Dict[str, str]) -> List[str]:
    return [f for f in LEAD_FIELDS if not collected.get(f)]
