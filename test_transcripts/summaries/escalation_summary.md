# Scenario

Summary after escalation

# Goal

Ensure the summary includes escalation events and provides next actions.

# Conversation

User angry and asks for human; escalation occurred earlier in the flow.

# Expected Behaviour

- Summary marks `escalation_triggered` true, includes `escalation_reasons`, and recommends `Human agent follow-up` with `high` priority.

# Expected JSON Output

```json
{
  "customer_intent": "Support complaint",
  "lead_quality": "low",
  "qualification_data": {},
  "conversation_sentiment": "angry",
  "escalation_triggered": true,
  "escalation_reasons": ["explicit_human_request","angry sentiment"],
  "unanswered_questions": [],
  "sop_gaps_identified": [],
  "recommended_next_action": "Human agent follow-up",
  "follow_up_priority": "high"
}
```

# Safety Validation

- Summary must accurately reflect escalation reasons.

# Final Result

Pass if escalation is reflected in the summary.
