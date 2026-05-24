# Phase 9 — Final Submission Checklist

Use this checklist before submitting the repo or sharing with recruiters.

Repository checks
- [ ] `README.md` is polished and explains quick-run steps
- [ ] `DEPLOYMENT.md` has clear Streamlit Cloud steps
- [ ] `.gitignore` excludes `.env`, `logs/`, and `.streamlit/secrets.toml`
- [ ] No sensitive keys committed
- [ ] `requirements.txt` minimal and correct

Code quality
- [ ] `app.py` starts without heavy initialization
- [ ] `utils/groq_client.py` handles missing key demo-mode
- [ ] JSON parsing robust (`utils/json_utils.py`)
- [ ] Tests/transcripts run via `scripts/run_transcripts.py --dry-run`

Assets
- [ ] Screenshots and animated GIFs under `assets/` (not huge)
- [ ] `docs/demo_walkthrough.md` present and concise

Deployment
- [ ] Streamlit Cloud deploys with secrets configured
- [ ] App runs within free tier limits

Demo & Presentation
- [ ] 2–5 minute demo script ready (`docs/demo_walkthrough.md`)
- [ ] Recruiter Q&A (`docs/recruiter_qna.md`) ready
- [ ] Example transcripts attached in `test_transcripts/`

Submission packaging
- [ ] Zip/tarball creation instructions documented
- [ ] Exported sample transcripts included
