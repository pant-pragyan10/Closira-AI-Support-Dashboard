# Phase 5: Summary Engine Tests and Examples

1) Happy path — qualification complete, no escalations

User flow: standard FAQ, qualification collected, no escalation.
Expected: summary with customer_intent, lead_quality, qualification_data filled, escalation_triggered false, no sop_gaps.

2) Escalation-heavy example

User: angry and explicitly requests human. Escalation triggered.
Expected: escalation_reasons include `explicit_human_request`, conversation_sentiment `angry`, recommended_next_action `Human agent follow-up`, follow_up_priority `high`.

3) Unresolved question detected

User asks "What are the aftercare instructions?" and assistant has no SOP info.
Expected: `unanswered_questions` include the question, `sop_gaps_identified` include `missing_aftercare`.

4) Partial qualification

User provides business type but leaves budget blank. Expected summary shows partial qualification_data and lead_quality computed accordingly.

5) Multiple intents / ambiguous

User expresses both interest in product and asks for support. Expected: `customer_intent` prefer highest-priority intent (support vs purchase) and list ambiguous hints.

Edge cases
- Conversation ends abruptly: summary should still produce available data and mark incomplete fields.
- Conflicting user answers: include latest answer and mention conflict in `recommended_next_action` to verify.
- No qualification: summary should handle missing qualification gracefully.

