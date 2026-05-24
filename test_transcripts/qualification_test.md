# Qualification Test

Customer: I have a question about billing for last month.

# Expected Behaviour

- Agent asks follow-up qualification questions when needed and preserves partial lead data.

# Expected JSON Output

```json
{
	"collected_data": {
		"issue_topic": "billing",
		"details": "question about last month's bill"
	},
	"missing_fields": ["contact_method"],
	"qualification_complete": false
}
```
