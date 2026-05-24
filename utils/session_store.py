import json
import os
from typing import Any, Dict


class SessionStore:
    """Simple JSON-backed session store for lead qualification.

    Keeps session-specific memory (conversation history and collected lead data).
    This is lightweight and beginner-friendly; swap with Redis or DB later.
    """

    def __init__(self, session_id: str = "default", storage_dir: str = "logs"):
        self.session_id = session_id
        self.storage_dir = storage_dir
        os.makedirs(self.storage_dir, exist_ok=True)
        self.path = os.path.join(self.storage_dir, f"session_{self.session_id}.json")
        # In-memory representation
        self._data: Dict[str, Any] = {
            "history": [],
            "lead_data": {},
            # field the assistant most recently asked for during qualification
            "last_asked_field": None,
            "last_asked_question": None,
        }
        # Load existing if present
        if os.path.exists(self.path):
            try:
                with open(self.path, "r", encoding="utf-8") as f:
                    self._data.update(json.load(f))
            except Exception:
                # ignore and start fresh
                pass

    def save(self):
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self._data, f, indent=2)

    # History helpers
    def append_message(self, role: str, text: str):
        self._data.setdefault("history", []).append({"role": role, "text": text})
        self.save()

    def get_history(self):
        return list(self._data.get("history", []))

    # Lead data helpers
    def get_lead(self) -> Dict[str, Any]:
        return dict(self._data.get("lead_data", {}))

    def set_lead_field(self, key: str, value: Any):
        self._data.setdefault("lead_data", {})[key] = value
        # clear last asked field on explicit user-provided value
        if self._data.get("last_asked_field") == key:
            self._data["last_asked_field"] = None
            self._data["last_asked_question"] = None
        self.save()

    def bulk_set_lead(self, data: Dict[str, Any]):
        self._data.setdefault("lead_data", {}).update(data)
        self.save()

    # last asked field helpers
    def set_last_asked(self, field: str, question: str = None):
        self._data["last_asked_field"] = field
        self._data["last_asked_question"] = question
        self.save()

    def get_last_asked(self):
        return self._data.get("last_asked_field"), self._data.get("last_asked_question")

    def clear_last_asked(self):
        self._data["last_asked_field"] = None
        self._data["last_asked_question"] = None
        self.save()

    def clear(self):
        self._data = {"history": [], "lead_data": {}}
        self.save()
