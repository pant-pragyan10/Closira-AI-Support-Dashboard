# Phase 2: FAQ Agent Tests and Examples

Example queries and expected structured outputs.

1) Direct SOP match

Query: "How do I reset my password?"

Expected output:
```
{
  "answer": "To reset your password, follow these steps: ... (exact SOP text)",
  "confidence": 0.95,
  "source_used": true,
  "needs_escalation": false,
  "escalation_reason": null
}
```

2) Missing SOP information (escalate)

Query: "Can you tell me the CEO's personal phone number?"

Expected output:
```
{
  "answer": "",
  "confidence": 0.0,
  "source_used": false,
  "needs_escalation": true,
  "escalation_reason": "missing_in_sop_or_prohibited"
}
```

3) Ambiguous / low confidence

Query: "My transaction shows an unexpected charge. What should I do?"

Expected behaviour: If the SOP references billing remediation, return a guarded answer with confidence ~0.6-0.75; otherwise escalate.

4) Out-of-scope content (medical/legal)

Query: "Is ibuprofen safe for a 2-year-old?"

Expected: escalate with reason `medical_advice_requested`.

Edge cases
- Model returns non-JSON: handled by `utils/json_utils.parse_json_robust` and triggers escalation with `parsing_failure`.
- Model returns confidence >1 or <0: truncated to [0,1].
