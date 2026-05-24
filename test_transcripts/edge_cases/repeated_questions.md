# Scenario

Repeated unanswered questions detection

# Goal

Validate system escalates when the user repeats the same question multiple times without a helpful answer.

# Conversation

User: "How do I get a refund?"
Assistant: unable to answer
User: "How do I get a refund?"
Assistant: unable to answer
User: "How do I get a refund?"

# Expected Behaviour

- System detects repetition and escalates with reason `repeated_questions_n` and priority `high`.

# Expected JSON Output

```json
{
  "needs_escalation": true,
  "escalation_score": 0.85,
  "reason": ["repeated_questions_3"],
  "recommended_action": "human_handoff",
  "customer_sentiment": "frustrated",
  "priority": "high"
}
```

# Safety Validation

- Ensure repetition detection is robust to minor punctuation/spacing differences.

# Final Result

Pass if repeated question escalates.
