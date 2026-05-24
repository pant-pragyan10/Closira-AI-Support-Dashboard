# Phase 10 — Final Submission Hardening Checklist

Follow this before submission. Each item should be verified locally and on Streamlit Cloud.

Repository & docs
- [ ] `README.md` polished with badges, screenshots, elevator pitch
- [ ] `PHASE10_CHECKLIST.md` included in repo root
- [ ] `DEPLOYMENT.md`, `CHECKLIST.md`, `prompt_design.md` present and accurate
- [ ] `assets/` contains screenshots (3) and one animated GIF (optional)

Code quality
- [ ] Type hints present in core modules (`utils/`, `agents/`)
- [ ] Docstrings for public functions and classes
- [ ] Exceptions handled and logged gracefully
- [ ] `requirements.txt` minimal and installable

Testing & validation
- [ ] `scripts/run_transcripts.py --dry-run` returns no parsing failures
- [ ] Example transcripts pass schema validation
- [ ] `scripts/cleanup.py` removes logs/build artifacts

Deployment & security
- [ ] No secrets committed (scan for `GROQ_API_KEY` or `.env` content)
- [ ] `.gitignore` excludes `.env`, `.streamlit/secrets.toml`, `logs/`
- [ ] Streamlit Cloud secrets configured and tested

Demo readiness
- [ ] 2–5 minute demo script rehearsed and recorded
- [ ] Demo assets (screenshots/GIF) present
- [ ] Recruiter Q&A notes prepared (`docs/recruiter_qna.md`)

Packaging
- [ ] Create `closira_release.zip` via `git archive` and include `README.md` and `DEPLOYMENT.md`
- [ ] Include sample transcripts in `releases/` or `assets/`

Final steps
- [ ] Run linter/format (e.g., `ruff`/`black`) if used
- [ ] Push to `main` and verify Streamlit Cloud deployment
