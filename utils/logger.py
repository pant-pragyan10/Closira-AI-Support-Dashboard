import json
import os
from datetime import datetime
from typing import Any, Dict

class ConversationLogger:
    """Append conversation entries to a JSON file as a simple log store."""

    def __init__(self, path: str):
        self.path = path
        os.makedirs(os.path.dirname(path), exist_ok=True)
        if not os.path.exists(path):
            with open(path, "w", encoding="utf-8") as f:
                json.dump([], f)

    def log(self, entry: Dict[str, Any]):
        record = {"timestamp": datetime.utcnow().isoformat() + "Z", **entry}
        with open(self.path, "r+", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except Exception:
                data = []
            data.append(record)
            f.seek(0)
            json.dump(data, f, indent=2)
            f.truncate()
