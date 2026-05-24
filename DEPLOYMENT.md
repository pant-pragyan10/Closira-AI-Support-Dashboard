# Deployment Guide — Streamlit Cloud

This document walks through preparing and deploying Closira to Streamlit Cloud, configuring secrets, and troubleshooting common issues.

1) Prerequisites
- A free Streamlit Cloud account
- GitHub repository pushed (public or private)
- `GROQ_API_KEY` available (store securely)

2) Prepare repo
- Ensure `requirements.txt` lists runtime dependencies.
- Add a `.streamlit` folder for runtime config if needed.
- Ensure `app.py` is at repository root and runnable.

3) Configure secrets on Streamlit Cloud

- In the Streamlit app deployment UI, open "Secrets" and add:
  - `GROQ_API_KEY` : your_api_key_here
  - Any other runtime flags (e.g., `FAQ_CONFIDENCE_THRESHOLD=0.6`)

OR use `secrets.toml` locally for testing (do NOT commit):

```toml
GROQ_API_KEY = "your_api_key_here"
FAQ_CONFIDENCE_THRESHOLD = "0.6"
```

Place `secrets.toml` in `.streamlit/` for local testing only.

4) Add `requirements.txt` (minimal)

Make sure it contains at least:

```
streamlit
requests
python-dotenv
jsonschema
```

5) Deploy

- In Streamlit Cloud, create a new app, connect to the repo branch, and set the `main` file to `app.py`.
- Click "Deploy" — Streamlit will install dependencies and start the app.

6) Troubleshooting

- App fails to start / module not found: ensure `requirements.txt` covers all deps and `app.py` imports are correct.
- Missing secrets: check Streamlit Secrets or `.streamlit/secrets.toml` for local runs.
- Long cold starts: reduce heavy initialization in `app.py` (defer loading SOPs or large files to on-demand operations).
- Memory limits: Streamlit Cloud free tier RAM is limited — avoid loading huge data on startup.

7) Startup reliability tips

- Lazy-load large assets (SOPs) only when needed.
- Wrap external calls (Groq) with timeouts and retry logic.
- Provide a demo-mode fallback when `GROQ_API_KEY` missing (already present in `utils/groq_client.py`).

8) Logging and monitoring

- Use `logs/` for local debugging (excluded from git via `.gitignore`).
- For production, integrate with a hosted logging or error tracking service (Sentry) in the future.
