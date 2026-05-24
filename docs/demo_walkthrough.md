# Demo Walkthrough (2–5 minute script)

Goal: concisely show technical depth and product value for recruiters.

Flow (2–5 minutes)

1. 0:00–0:20 Intro: one-line summary — "Closira is an SOP-grounded AI support agent with safe escalation and CRM-ready outputs."
2. 0:20–1:10 Show the Streamlit UI: brief tour of sidebar controls, chat pane, and export buttons.
3. 1:10–2:10 Live demo: run three short scenarios (FAQ grounding, hallucination prevention/escalation, qualification → summary).
   - FAQ grounding: ask an SOP-covered question and show `source_used: true` and high confidence.
   - Hallucination prevention: ask an out-of-scope or ambiguous question; show conservative refusal and escalation recommendation.
   - Qualification flow: demonstrate one or two Q&A turns, show `lead_data` saved and final CRM-ready summary.
4. 2:10–3:00 Architecture explanation: briefly explain agents, JSON outputs, and escalation merging.
5. 3:00–3:30 Closing: next steps and invite to view repo/README.

What to say (concise points)
- "Agents are small, focused, and emit JSON only — this makes automation reliable."
- "We prioritize human-in-the-loop for ambiguous cases; you'll see that when the system escalates."
- "Session data is exported as JSON for CRM ingestion and audits."

What NOT to say
- Avoid implying the system is production-grade for critical domains without further validation.
- Don't claim zero hallucinations — instead emphasize conservative safeguards.

Recording tips
- Use Streamlit's fullscreen for cleaner video.
- Use animated GIF highlights (e.g., crop via QuickTime) to point at elements.
