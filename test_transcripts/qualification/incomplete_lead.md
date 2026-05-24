# Scenario

Incomplete lead qualification

# Goal

Verify agent handles users leaving mid-flow and preserves partial data.

# Conversation

User: We're a small clinic.
Agent: How many staff?
User: I need to go, bye.

# Expected Behaviour

- Agent stores `business_type` but not `team_size`, `qualification_complete` false.

# Expected JSON Output

```json
{
  "collected_data": {
    "business_type": "small clinic"
  },
  "missing_fields": ["team_size","current_tools","customer_goals","budget_interest","contact_method"],
  "qualification_complete": false
}
```

# Safety Validation

- System should preserve partial data and allow follow-up.

# Final Result

Pass if partial data is saved and qualification incomplete.
