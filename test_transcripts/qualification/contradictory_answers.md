# Scenario

Contradictory user information

# Goal

Validate the system allows updating answers and flags contradictions.

# Conversation

User: We have a team of 5.
Agent: Noted. Anything else?
User later: Actually it's 15 now.

# Expected Behaviour

- System should update `team_size` to latest value (15) and include a note indicating a change in summary or recommended verification.

# Expected JSON Output

```json
{
  "collected_data": {
    "team_size": "15"
  },
  "notes": "team_size updated from 5 to 15",
  "qualification_complete": false
}
```

# Safety Validation

- Ensure latest answers overwrite previous ones and change is noted for human reviewers.

# Final Result

Pass if update and note are present.
