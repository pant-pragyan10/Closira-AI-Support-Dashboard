# Closira AI — Support Dashboard

Overview
--
Closira AI is a grounded, SOP-driven support assistant demonstrating routing, qualification, escalation, and summary workflows backed by an LLM (Groq). The system emphasizes safety-first JSON outputs, deterministic SOP fallbacks, and production-like UX in a Streamlit dashboard.

Structure
--
- `agents/` — modular agents (FAQ, Qualification, Escalation, Summary, Router)
- `prompts/` — prompt builders for each agent
- `utils/` — clients, normalization, session store, parsers, and helpers
- `tests/` — unit tests for core behaviors
- `app.py` — Streamlit UI entrypoint

Design Notes
--
- SOP Grounding: `data/sop.json` is the single source-of-truth. Agents prefer SOP-cited answers and use deterministic extraction when model output is missing or unparsable.
- Routing: `agents/router_agent.py` automatically chooses between qualification, FAQ, summary, and escalation flows.
- Safety: Agents return strict JSON; `utils/json_utils.py` performs robust parsing and fallbacks.
- UI: `app.py` normalizes agent outputs and stores authoritative conversation state in `logs/session_*.json` via `SessionStore`.

Quick Start
--
1. Copy `.env.example` to `.env` and set your Groq API key:

```bash
cp .env.example .env
# edit .env and add your key
```

2. Install dependencies (recommended in a virtualenv):

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

3. Run the Streamlit app:

```bash
streamlit run app.py
```

Deployment
--
- The app is a single-process Streamlit dashboard. For production, deploy via a container or a PaaS and wire environment variables securely (do not commit `.env`).

Repository hygiene
--
- Secrets must never be committed. Use `.env.example` as a template.
- Logs and session files are ignored by `.gitignore`.

Final notes
--
This repo is prepared for portfolio presentation: concise README, cleaned logs, and a minimal dependency list. Add screenshots to `assets/` and update the README gallery section before publishing.
# Closira — SOP-Grounded AI Support Agent

Short, professional README tailored for recruiter reviewers and demo viewers.

## Project Overview

Closira is a production-style, SOP-grounded conversational AI assistant built for SMB customer support. It answers FAQs from a supplied SOP, runs a safe lead-qualification flow, detects and escalates risky or ambiguous cases, and produces CRM-ready summaries — all via a polished Streamlit dashboard.

## Features

- SOP-grounded FAQ answering with hallucination prevention
- Multi-turn lead qualification with session memory
- Hybrid escalation intelligence (heuristics + LLM reasoning)
- Structured JSON outputs for automation and CRM
- Streamlit demo dashboard with analytics and export
- Transcript-based testing & validation runner

## AI Workflow Architecture

- Router selects per-turn agent: FAQ, Qualification, Escalation, Summary
- Agents are prompt-constrained to emit JSON only
- SessionStore persists conversation history and lead fields
- Escalation engine merges heuristics and LLM analysis conservatively

See [architecture.md](architecture.md) and [prompt_design.md](prompt_design.md).

## System Design

Closira emphasizes modularity and safety:

- Small agents with single responsibilities
- Strict prompt constraints and low temperature
- Parsing & JSON validation on every model response
- Conservative escalation fallback on parsing/confidence failures

## Prompt Engineering

Prompts are organized in `prompts/` and enforce JSON-only structured outputs. See `prompt_design.md` for rationale and schemas.

## Escalation Intelligence

Hybrid approach:
- Lexicon & replay heuristics for fast signals
- LLM-based analyzer for nuanced decisions
- Conservative merging (take the higher escalation score)

## Streamlit Dashboard

Run locally:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

The UI supports session export, transcript playback, and basic analytics.

## Testing Framework

Run the dry-run transcript validator:

```bash
python scripts/run_transcripts.py --dry-run
```

## Installation

1. Create a virtualenv
2. Install `requirements.txt`
3. Create a `.env` with `GROQ_API_KEY` (or set Streamlit Cloud secret)

## Deployment

See `DEPLOYMENT.md` for exact Streamlit Cloud deployment steps and `secrets.toml` guidance.

## Demo Walkthrough

See `docs/demo_walkthrough.md` for a succinct 2–5 minute demo script and recruiter talking points.

## Example Outputs

Examples live in `test_transcripts/` and `logs/` after running locally.

## Tech Stack

- Python 3.11+
- Streamlit for UI
- Groq API for LLM calls (via `utils/groq_client.py`)
- Simple JSON-backed session persistence

## Future Improvements

- Add vector DB retrieval (FAISS) for large SOPs
- CI runner for live transcript comparisons
- Fine-tuned classifiers for intent & sentiment

## Licensing & Attribution

This repo is prepared for demo and educational purposes. Replace or remove any production credentials before sharing.

---

Badges

![Streamlit](https://img.shields.io/badge/Streamlit-ready-blue)
![Language](https://img.shields.io/badge/python-3.11-green)

Screenshots (optional)

If you add screenshots, place them in `assets/` named `screenshot-1.png`, `screenshot-2.png`, `screenshot-3.png`. An optional GIF demonstrating the qualification flow is fine but not required.

Quick pitch

Closira is an SOP-grounded AI support assistant built for safe, auditable automation.
# Closira AI Agent — PHASE 1

This repository contains a Phase 1 implementation scaffold for the Closira AI Agent using Groq API and Streamlit.

Quick start

1. Create a virtual environment and install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Copy `.env.example` to `.env` and add your `GROQ_API_KEY`.

3. Run the Streamlit app:

```bash
streamlit run app.py
```

What we included
- `app.py`: Streamlit UI and wiring
- `utils/groq_client.py`: Groq API client wrapper
- `utils/memory.py`: simple session memory abstraction
- `utils/logger.py`: conversation logger
- `utils/parser.py`: SOP loader
- `agents/` and `prompts/`: modular agent and prompt templates
- `data/sop.json`: sample SOP
- `logs/conversations.json`: starter conversation log

This phase is intentionally beginner-friendly while keeping an internship-quality structure.
