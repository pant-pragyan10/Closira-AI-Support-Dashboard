# Scenario

Malformed / non-JSON agent output handling

# Goal

Test robust JSON parsing and escalation when agent output is malformed.

# Conversation

User: Ask a question that triggers a model reply.
Assistant: Returns malformed JSON like `Answer: {not json}`

# Expected Behaviour

- The system detects parsing failure, logs raw output, escalates with `parsing_failure`, and returns safe fallback.

# Expected JSON Output

```json
{
  "answer": "",
  "confidence": 0.0,
  "source_used": false,
  "needs_escalation": true,
  "escalation_reason": "parsing_failure"
}
```

# Safety Validation

- Raw model output must be logged for auditing.

# Final Result

Pass if parsing failure triggers escalation and logging.
