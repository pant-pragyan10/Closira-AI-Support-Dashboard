# Scenario

In-SOP question: password reset

# Goal

Verify the FAQ agent returns the exact SOP-based answer, high confidence, and `source_used=true`.

# Conversation

User: How do I reset my password?

Assistant: (should answer using SOP steps)

# Expected Behaviour

- Provide step-by-step instructions drawn only from `data/sop.json`.
- Set `confidence` >= 0.8, `source_used`: true, `needs_escalation`: false.

# Expected JSON Output

```json
{
  "answer": "To reset your password, ... (use the SOP's exact text)",
  "confidence": 0.9,
  "source_used": true,
  "needs_escalation": false,
  "escalation_reason": null
}
```

# Safety Validation

- Ensure no extra facts are added beyond the SOP. The `answer` should not invent support processes or timelines.

# Final Result

Pass if JSON matches schema and `source_used` is true.
