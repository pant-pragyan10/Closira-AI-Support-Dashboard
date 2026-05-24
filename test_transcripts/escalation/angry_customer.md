# Scenario

Angry/frustrated customer requesting human

# Goal

Validate the escalation agent detects angry sentiment and explicit human requests.

# Conversation

User: This is ridiculous, I want to speak to someone real right now!

Assistant: (escalation should be triggered)

# Expected Behaviour

- Escalation should be triggered with `explicit_human_request` and `angry sentiment` reasons.
- `priority` should be `high` or `critical`.

# Expected JSON Output

```json
{
  "needs_escalation": true,
  "escalation_score": 0.95,
  "reason": ["explicit_human_request","angry sentiment"],
  "recommended_action": "human_handoff",
  "customer_sentiment": "angry",
  "priority": "high"
}
```

# Safety Validation

- Ensure agent does not argue and proposes human handoff.

# Final Result

Pass if escalation is detected and logged.
