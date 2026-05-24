# Scenario

Completed lead qualification

# Goal

Verify the Qualification Agent collects all fields, creates lead summary, and marks qualification_complete true.

# Conversation

User: Hi, I'm interested in your product.
Agent: What kind of business are you in?
User: I'm an e-commerce retailer.
Agent: How many people are on your team?
User: About 20.
Agent: Which tools do you use?
User: Shopify and Mailchimp.
Agent: What are your goals?
User: Improve conversion and automate campaigns.
Agent: What's your budget interest?
User: Medium budget.
Agent: Preferred contact method?
User: Email.

# Expected Behaviour

- All lead fields collected, qualification_complete true, lead_quality computed (medium/high depending on scoring).

# Expected JSON Output

```json
{
  "next_question": "",
  "collected_data": {
    "business_type": "e-commerce retailer",
    "team_size": "20",
    "current_tools": "Shopify, Mailchimp",
    "customer_goals": "Improve conversion and automate campaigns",
    "budget_interest": "medium",
    "contact_method": "email"
  },
  "missing_fields": [],
  "qualification_complete": true,
  "lead_quality": "medium"
}
```

# Safety Validation

- Ensure values are stored and summary is generated.

# Final Result

Pass if qualification completes and lead_summary exists.
