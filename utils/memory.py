from typing import Any, Dict

class SessionMemory:
    """Simple session memory that can be used by agents.

    This keeps a dict in memory. The Streamlit app exposes it in the sidebar.
    For production, swap it with a persistent store.
    """

    def __init__(self):
        self._store: Dict[str, Any] = {}

    def get(self, key: str, default=None):
        return self._store.get(key, default)

    def set(self, key: str, value: Any):
        self._store[key] = value

    def append_to_list(self, key: str, value: Any):
        self._store.setdefault(key, []).append(value)

    def dump(self) -> Dict[str, Any]:
        return dict(self._store)
