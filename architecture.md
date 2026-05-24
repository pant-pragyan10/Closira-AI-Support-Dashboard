## Architecture Overview

Concise architecture overview for reviewers. The system is intentionally small and modular to be auditable and easy to run locally.

- `app.py`: Streamlit dashboard and router.
- `agents/`: focused agent wrappers (FAQ, Qualification, Escalation, Summary).
- `prompts/`: per-agent prompt templates enforcing JSON outputs.
- `utils/`: helpers (Groq client, JSON parsing, session store, simple config).
- `test_transcripts/`: evaluation transcripts and expected outputs.

Data flow: User → Router → Agent → SessionStore/Logs → Escalation/Summary

Deployment note: keep `app.py` lightweight on startup; load SOP sections lazily.
