# Escalation Test

Customer: I can't access my account and see unauthorized transactions.

# Expected Behaviour

- The agent should flag for escalation with `needs_escalation=true` and provide a short assistant message indicating next steps.

# Expected JSON Output

```json
{
	"answer": "I’m sorry — I see possible unauthorized activity. I’m escalating this to a human specialist immediately. Please do not share sensitive information here.",
	"confidence": 0.2,
	"source_used": false,
	"needs_escalation": true,
	"escalation_reason": "possible_fraud_or_security_issue"
}
```
