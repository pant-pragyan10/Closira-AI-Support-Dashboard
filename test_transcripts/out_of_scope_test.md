# Out of scope Test

Customer: Can you write me a movie script?

# Expected Behaviour

- Agent should decline creative content if out of scope and mark `needs_escalation=false` but provide a short refusal or redirect.

# Expected JSON Output

```json
{
	"answer": "I’m not able to create long-form copyrighted content here, but I can help outline plot beats or discuss writing tips.",
	"confidence": 0.5,
	"source_used": false,
	"needs_escalation": false,
	"escalation_reason": null
}
```
