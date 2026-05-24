# Summary Test

Conversation: multiple messages to summarize.

# Expected Behaviour

- The Summary Agent should extract `customer_intent`, `qualification_data`, `escalation_triggered`, and produce a concise recommended next action.

# Expected JSON Output

```json
{
	"customer_intent": "General support and billing inquiry",
	"lead_quality": "low",
	"qualification_data": {},
	"conversation_sentiment": "neutral",
	"escalation_triggered": false,
	"escalation_reasons": [],
	"unanswered_questions": [],
	"sop_gaps_identified": [],
	"recommended_next_action": "Provide billing help article and ask if they need specialist follow-up",
	"follow_up_priority": "low"
}
```
