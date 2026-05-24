# Test transcripts

This folder contains structured test transcripts used to validate the Closira AI Agent workflow.

Structure

- `faq/` — FAQ-focused scenarios
- `escalation/` — Escalation and safety scenarios
- `qualification/` — Lead qualification flows
- `summaries/` — Summary generation scenarios
- `edge_cases/` — Malformed/empty/repeated input tests

Each transcript is a Markdown file with the following sections:

```
# Scenario
# Goal
# Conversation
# Expected Behaviour
# Expected JSON Output
# Safety Validation
# Final Result
```

Running tests

A lightweight runner is provided at `scripts/run_transcripts.py` that performs a dry-run validation: it parses the transcript files and validates that the `Expected JSON Output` is well-formed JSON and contains required keys. The runner can be extended to call agents for live evaluation when `GROQ_API_KEY` is available.

To run (dry-run only):

```bash
python scripts/run_transcripts.py --dry-run
```

To run in live mode (requires `GROQ_API_KEY` in `.env` and network access):

```bash
python scripts/run_transcripts.py --live
```

# Example Expected JSON Output (for dry-run validation)

```json
{
	"answer": "Example answer string",
	"confidence": 0.9,
	"source_used": true,
	"needs_escalation": false,
	"escalation_reason": null
}
```

# Expected JSON Output

```json
{
  "answer": "Example answer string",
  "confidence": 0.9,
  "source_used": true,
  "needs_escalation": false,
  "escalation_reason": null
}
```

The runner outputs per-transcript validation results and writes an evaluation summary to `logs/test_results.json`.
