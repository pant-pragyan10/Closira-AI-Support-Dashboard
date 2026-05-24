# FAQ Test

Customer: How do I reset my password?

Assistant: ...

# Expected Behaviour

- The FAQ agent should return the SOP-based password reset steps, set `source_used=true`, `confidence>=0.8`, and `needs_escalation=false`.

# Expected JSON Output

```json
{
	"answer": "To reset your password, go to Settings → Security → Reset Password, follow the emailed link, and choose a new password that meets the policy.",
	"confidence": 0.9,
	"source_used": true,
	"needs_escalation": false,
	"escalation_reason": null
}
```
