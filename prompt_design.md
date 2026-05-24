"""
Prompt Design & AI Engineering Notes

Purpose
- This document explains the prompt engineering, safety, and orchestration choices for the Closira AI Agent. It is written for reviewers and engineers who need to understand why prompts are structured the way they are, how hallucination prevention is enforced, and how the multi-agent workflow operates in production-like settings.

Contents
- Project overview
- System architecture and workflow
- Prompt engineering strategy (per agent)
- Hallucination prevention techniques
- Escalation & safety design
- Structured output schemas
- Memory and multi-turn design
- Streamlit dashboard rationale
- Testing and validation philosophy
- Tradeoffs, limitations, and future improvements

---

## 1. Project Overview

- What the system does: closira-ai-agent is an AI assistant tailored for SMB customer support. It answers SOP-grounded FAQs, qualifies leads through natural dialogue, detects when human handoff is needed, and produces structured CRM-ready summaries.
- Business problem: many SMBs need consistent, safe, and auditable first-line support that reduces human load while ensuring no harmful or incorrect guidance is sent to customers.
- Why this matters: structured AI workflows reduce risk, enable reliable automation, and create data that is actionable for sales and operations teams.

## 2. System Architecture (high-level)

The system is modular and orchestrated by a router. Each agent is constrained with a focused prompt and returns structured JSON to allow downstream automation.

User → Router → Agent(s) → Memory & Logger → Escalation Engine → Summary Engine → Analytics / CRM

- Router: decides which agent (FAQ / Qualification / Escalation / Summary) to call based on UI selection and signals.
- Agents: small, single-responsibility components. Each has a prompt file and minimal logic wrapper.
- Memory: session-scoped persistence (`SessionStore`) holds conversation history and lead fields.
- Escalation Engine: combines lightweight heuristics + LLM reasoning to decide handoffs.
- Summary Engine: produces CRM-style summaries and SOP-gap detection.

See `architecture.md` and `workflow_diagrams.md` for a mermaid flow diagram.

---

## 3. Prompt Engineering Strategy

Design principles
- Minimal surface area: keep prompts short but explicit; minimize the model’s freedom to reduce hallucination.
- Single responsibility: each agent has one primary goal and a single JSON schema to emit.
- Deterministic defaults: lower temperature (0.2) and schema enforcement to make outputs repeatable.
- Auditable instructions: prompts explicitly forbid hallucinations and demand source attribution when used.

Why modular prompts?
- Easier to test: unit-test each prompt/agent pair separately.
- Clear responsibility boundaries: qualification vs FAQ vs escalation are distinct concerns.
- Safer by design: strict, per-agent constraints reduce cross-talk and uncontrolled generalization.

Why JSON outputs?
- Machine-readable responses simplify downstream routing (escalation, CRM export).
- Enables schema validation and deterministic UI rendering.

Why low temperature?
- Low temperature reduces variability and prevents the model from creatively inventing details not grounded in SOP.

Agent-specific prompts (summary)

- **FAQ Agent**
  - Purpose: answer customer questions strictly from SOP.
  - Key constraints: "Answer ONLY from the SOP", "Output JSON only", "Provide confidence [0.0-1.0]", "Set source_used true only if citing SOP".
  - Expected output schema: see "FAQ JSON schema" below.

- **Qualification Agent**
  - Purpose: gather required lead fields using single-question turns; avoid duplicates and be conversational.
  - Key constraints: ask exactly one concise question at a time, reference prior answers, output JSON `{next_question, field}` when used to generate questions.

- **Escalation Agent**
  - Purpose: assess safety/risk and recommend handoff.
  - Key constraints: analyze conversation & SOP coverage, output JSON specifying `needs_escalation`, `escalation_score`, `reason`, `recommended_action`, and `priority`.

- **Summary Agent**
  - Purpose: produce CRM-style conversation summaries and actionable next steps.
  - Key constraints: analyze full conversation history, qualification memory, escalation logs; output JSON-only summary schema.

Prompt engineering tradeoffs
- Strict prompts reduce creativity; acceptable for customer-support where correctness matters more than expressiveness.
- The system favors conservative refusals and escalations over risky confident answers.

---

## 4. Hallucination Prevention Design (very important)

Core idea: prefer silence + escalation over plausible-sounding but incorrect answers.

Key mechanisms

- SOP grounding: the FAQ prompt injects the SOP sections into the prompt context. The model is explicitly instructed to only use content present in that context.
- JSON-only output: forcing structured responses makes partial free-text hallucinations less likely and easier to detect.
- Confidence scoring: model-reported confidence (0.0-1.0) is combined with deterministic thresholds. Low-confidence responses trigger escalation.
- Low temperature: reduces variability and creative generation.
- Parsing & validation: `utils/json_utils.parse_json_robust` extracts and validates JSON; parsing failures cause safe fallbacks and escalations.
- Escalation fallback: when in doubt (parsing failure, low confidence, missing SOP coverage), recommend human handoff rather than guessing.

Why hallucination prevention matters
- In customer support, incorrect guidance can cause customer harm, regulatory risk, or loss of trust. The system errs on the side of human review.

Practical patterns
- Always include the SOP text in prompts, but avoid passing massive context; only pass relevant sections when possible.
- Implement audit logs storing raw model outputs for post-hoc review.

---

## 5. Escalation & Safety Design

Goals
- Detect when an LLM reply cannot be trusted, when the user is at risk, or when the user explicitly requests a human.

Signals used
- Lexical sentiment heuristics (anger/frustration keywords) — cheap and fast.
- Repetition detector: repeated user questions within a short window. Repetition >= 3 is a signal.
- Low confidence: agent's `confidence` < configurable threshold triggers escalation.
- SOP boundary detection: if the SOP lacks an answer, escalate.
- LLM reasoning: escalation agent runs an LLM-based analysis (JSON output) to combine signals and provide detailed reasons.

Why not keyword-only?
- Keyword-only systems miss context (sarcasm, multi-turn nuance) and generate many false positives. Combining heuristics with LLM reasoning balances precision and recall.

Decision flow

1. At each assistant reply, collect signals (confidence, sentiment, repetition, SOP coverage).
2. Aggregate heuristics produce a baseline escalation score.
3. LLM-based `EscalationAgent` analyzes the conversation and outputs a JSON decision.
4. Merge conservatively: take max of heuristic and model score; if above threshold, flag escalation.

Escalation outputs

```json
{
  "needs_escalation": true,
  "escalation_score": 0.89,
  "reason": ["angry sentiment","medical_advice_requested"],
  "recommended_action": "human_handoff",
  "customer_sentiment": "frustrated",
  "priority": "high"
}
```

---

## 6. Structured Output Schemas

Schemas are intentionally small and consistent for auditability.

- FAQ Output (FAQ JSON schema)

```json
{
  "answer": "...",
  "confidence": 0.0,
  "source_used": false,
  "needs_escalation": false,
  "escalation_reason": null
}
```

- Qualification Output

```json
{
  "next_question": "...",
  "collected_data": { /* fields */ },
  "missing_fields": ["budget", "contact_method"],
  "qualification_complete": false,
  "lead_quality": "medium"
}
```

- Escalation Output

```json
{
  "needs_escalation": true,
  "escalation_score": 0.85,
  "reason": ["low_confidence","repeated_questions_3"],
  "recommended_action": "human_handoff",
  "customer_sentiment": "angry",
  "priority": "high"
}
```

- Summary Output

```json
{
  "customer_intent": "...",
  "lead_quality": "medium",
  "qualification_data": { /* ... */ },
  "conversation_sentiment": "neutral",
  "escalation_triggered": true,
  "escalation_reasons": [],
  "unanswered_questions": [],
  "sop_gaps_identified": [],
  "recommended_next_action": "Human agent follow-up",
  "follow_up_priority": "high"
}
```

Why consistent schemas matter
- Enable deterministic UI rendering, monitoring, and rule-based routing to CRM or support tools.
- Support automated validation in testing and CI.

---

## 7. Memory & Multi-Turn Conversation Design

SessionStore overview
- Lightweight JSON-backed session store per session id.
- Stores `history` (role/text/timestamp/meta) and `lead_data` (structured qualification fields).

Design choices
- Keep memory simple and local for Phase 1–2; plan to replace with Redis or vector DB when scaling.
- Persist partial qualification answers immediately to avoid data loss.

Why memory matters
- Maintains context across turns so the Qualification Agent can ask targeted follow-ups and skip already answered fields.
- Enables accurate summaries and escalation decisions that rely on conversation history and prior answers.

Multi-turn orchestration
- Agents operate statelessly except that the router supplies the session store and SOP. Agents write to memory as needed.
- This avoids complex long-lived state in the agents themselves and centralizes persistence.

---

## 8. Streamlit Dashboard Design

Why Streamlit?
- Rapid iteration and deployment on Streamlit Cloud.
- Native support for JSON rendering, download buttons, progress bars, and simple layout controls.

UI decisions
- Chat-style bubbles for readability and demo polish.
- Sidebar with session controls and analytics to support reviewer workflows.
- Downloadable JSON for auditability and CRM export.

Deployment readiness
- `requirements.txt` contains dependencies; the app uses `streamlit run app.py` as entrypoint. Environment variables are read via `.env`.

---

## 9. Testing & Reliability Validation

Transcript-based testing
- Test transcripts are curated scenarios encoded in Markdown with expected JSON outputs.
- The `scripts/run_transcripts.py` runner performs a JSON-block validation dry-run and can be extended for live comparisons.

Validation targets
- Hallucination prevention: transcripts that should not produce factual statements outside SOP.
- Escalation logic: anger, medical, pricing, and repeated unanswered tests.
- Qualification flows: completed and partial flows with contradictory answers.

Why transcripts?
- Reproducible records that reviewers can run locally.
- Serves as living documentation of intended system behavior.

---

## 10. Tradeoffs & Limitations

- LLM accuracy: prompts constrain but do not eliminate model mistakes; logs and escalation are required for safety.
- Context size: we pass limited SOP context; a full retrieval/RAG system would scale better for large SOPs.
- Sentiment heuristics: lexicon-based detectors are inexpensive but imperfect; we pair them with LLM reasoning to reduce false positives.
- Determinism vs flexibility: low temperature increases repeatability but reduces natural language variety.

---

## 11. Future Improvements

- Integrate a vector DB (e.g., FAISS) for RAG and better SOP retrieval.
- Add fine-tuned classifiers (sentiment, intent) for higher precision.
- Add secure CRM integration and audit workflows for GDPR/privacy.
- Add CI pipeline for live transcript comparisons using mocked model outputs.

---

Appendix: file map
- `prompts/*` — per-agent prompt templates
- `agents/*` — agent logic wrappers
- `utils/*` — helpers: `groq_client`, `json_utils`, `session_store`, `lead_summary`, `escalation_utils`
- `test_transcripts/` — evaluation transcripts
- `app.py` — Streamlit dashboard

This document is intentionally practical and engineering-focused. It documents why we made each choice and the safety tradeoffs involved.
"""# Prompt Design Notes

This file documents the simple prompt templates used by the Phase 1 agents. Keep prompts short and deterministic.
