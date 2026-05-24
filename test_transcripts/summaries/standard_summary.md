# Scenario

Standard session summary

# Goal

Validate summary agent extracts customer intent, qualification data, sentiment, and SOP gaps.

# Conversation

User: Hi, we want help automating marketing.
Agent: Qualification asks and collects data.
User: No escalations.

# Expected Behaviour

- Summary includes `customer_intent` about marketing automation, qualification data summary, and `escalation_triggered` false.

# Expected JSON Output

```json
{
  "customer_intent": "Interested in marketing automation",
  "lead_quality": "medium",
  "qualification_data": {},
  "conversation_sentiment": "neutral",
  "escalation_triggered": false,
  "escalation_reasons": [],
  "unanswered_questions": [],
  "sop_gaps_identified": [],
  "recommended_next_action": "Schedule sales follow-up",
  "follow_up_priority": "medium"
}
```

# Safety Validation

- Ensure no hallucinated business outcomes.

# Final Result

Pass if summary fields are present and structured.
