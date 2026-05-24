# Phase 4: Escalation Engine Tests and Examples

Examples to validate escalation detection and behavior.

1) Angry customer

User: "This is ridiculous, you people never help!"
Expected: escalate with reasons including `angry sentiment`, `explicit_complaint`; priority `high` or `critical`.

2) Explicit human request

User: "Can I speak to someone real?"
Expected: escalate with `explicit_human_request`, recommended_action `human_handoff`.

3) Low confidence from FAQ

Scenario: FAQ returns low confidence (<0.5) for several answers.
Expected: escalate with `low_confidence`, priority `high`.

4) Repeated unanswered questions

User repeatedly asks the same question 3+ times.
Expected: escalate with `repeated_questions_n`, priority `high`.

5) Medical risk example

User: "Is this treatment safe for my child?"
Expected: escalate with `medical_advice_requested`, priority `critical`.

6) Sarcasm / false positives

User: "Great, that worked... not." (sarcastic)
Expected: sentiment detector may flag frustration; LLM reasoning should disambiguate; escalation may be `medium` only if repeated or confounding signals exist.

Edge cases:
- Passive-aggressive phrases should be monitored but not always escalated; combine with repetition and confidence signals to avoid false positives.
- Mid-conversation tone changes should update escalation score dynamically.
