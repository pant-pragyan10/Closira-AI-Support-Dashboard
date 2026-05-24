import json
from typing import Dict

def load_sop(path: str) -> Dict:
    """Load SOP JSON from disk and return as dict.

    This is intentionally minimal; extend as needed for richer parsing.
    """
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"title": "(no SOP found)", "sections": []}
