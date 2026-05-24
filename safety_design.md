# Safety Design

This document drills into safety mechanisms and why they were chosen.

## Safety goals

- Prevent harmful or incorrect automated responses.
- Ensure human-in-the-loop for risky or ambiguous situations.
- Provide auditable trails for every decision.

## Key safety mechanisms

1. SOP grounding: agents only answer from the SOP, and `source_used` must be true when SOP content is used.
2. Conservative defaults: if the model is uncertain or the output cannot be parsed into JSON, the system escalates rather than responds.
3. Escalation Engine: uses multiple signals and LLM reasoning to reduce false negatives.
4. Logging & audit: raw model outputs and parsed JSON are stored for each turn in `logs/`.

## Human handoff policy

- Escalation levels map to human workflows (`high` and `critical` are immediate handoffs; `medium` is monitored). The policy is intentionally conservative.

## Privacy & PII

- Prompts explicitly forbid returning private data. Out-of-scope/PII requests are escalated and logged; sensitive data is not written to logs.
