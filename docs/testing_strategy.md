# Testing Strategy and Guidance

This document explains the testing approach for Phase 7. It provides reasoning for each test, how tests were chosen, and guidance for demo selection.

Why testing matters
- Verifies system behavior and prevents regressions.
- Demonstrates reliability, safety, and production-readiness to reviewers.
- Reproducible transcripts help audit hallucinations and escalation accuracy.

Test selection rationale
- Chosen tests reflect assignment requirements and real-world scenarios: in-scope answers, out-of-scope requests, escalation triggers, qualification flows, and summaries.
- Edge cases (malformed input, repeated questions) ensure robust handling.

Running tests
- Use `python scripts/run_transcripts.py --dry-run` to validate transcript JSON blocks.
- For live evaluation, extend the script to call agents and compare expected outputs (requires `GROQ_API_KEY`).

Demo video guidance
- Show 3 transcripts: one Happy Path (completed_lead), one Escalation (angry_customer), and one SOP Gap (repeated_questions or hallucination_test).
- Narrate why each test is important and what the system did to remain safe.

What recruiters look for
- Clear test cases, reproducible results, safety considerations, and explanation of engineering trade-offs.
