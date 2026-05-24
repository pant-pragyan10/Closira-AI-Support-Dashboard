# Phase 3: Qualification Agent Tests and Examples

1) Happy path — user provides clear answers

User: "Hi, I'd like to learn more about your product."
Agent: "What kind of business or industry are you in?"
User: "We run a digital marketing agency."
Agent: "How many people are on your team (approx.)?"
User: "About 25." 
Agent: "Which tools do you currently use for campaign management?"
User: "We use HubSpot and Google Ads." 
Agent continues until all fields collected, then returns qualification_complete true and lead_quality.

2) Edge case — user refuses to answer budget

User: "I don't want to share budget info."
Agent should record `budget_interest: refused` and proceed to next questions or mark as missing and continue; scoring should account for refused as low signal.

3) Incomplete answers — user gives multi-field response

User: "We're a small retailer, team of 8, use Shopify."
Agent should extract 3 fields in one turn (business_type, team_size, current_tools) and skip asking those again.

4) Changing answers — user updates previous answer

User initially says team_size 5, later corrects to 12. Agent should allow updating stored field and recompute lead score.

5) Users avoiding questions — agent should politely try alternatives and mark fields `unknown` after polite attempts.
