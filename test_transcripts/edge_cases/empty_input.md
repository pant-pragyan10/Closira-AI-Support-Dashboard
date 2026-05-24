# Scenario

Empty input handling

# Goal

Validate system handles empty messages gracefully.

# Conversation

User: (sends empty message)

# Expected Behaviour

- System warns user to enter a message; no agent call; no crash.

# Expected JSON Output

```json
{
  "action": "no_op",
  "message": "User input empty",
  "handled": true
}
```

# Safety Validation

- Ensure no model calls are made on empty input.

# Final Result

Pass if UI warns and system does not attempt model call.
