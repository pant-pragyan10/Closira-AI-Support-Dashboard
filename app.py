import os
from dotenv import load_dotenv
import streamlit as st
import json
import time
from datetime import datetime

from utils.groq_client import GroqClient
from utils.parser import load_sop
from utils.logger import ConversationLogger
from agents.router_agent import RouterAgent
from agents.escalation_agent import EscalationAgent
from utils.escalation_logger import EscalationLogger
from agents.summary_agent import SummaryAgent
from utils.session_store import SessionStore
from utils.response_normalizer import normalize_response
from utils.lead_schema import missing_fields, LEAD_FIELDS

load_dotenv()

API_KEY = os.getenv("GROQ_API_KEY")
MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

st.set_page_config(page_title="Closira AI — Dashboard", layout="wide", initial_sidebar_state="expanded")

client = GroqClient(api_key=API_KEY, model=MODEL)
logger = ConversationLogger("logs/conversations.json")

# Small CSS for chat bubbles and badges
CHAT_CSS = """
<style>
.chat-row{display:flex;gap:8px;margin-bottom:8px}
.chat-bubble{padding:12px;border-radius:12px;max-width:70%;box-shadow:0 1px 2px rgba(0,0,0,0.05)}
.user{justify-content:flex-end}
.user .chat-bubble{background:#DCF8C6;color:#000}
.assistant .chat-bubble{background:#ffffff;color:#111;border:1px solid #eee}
.meta{font-size:12px;color:#666;margin-top:4px}
.badge{display:inline-block;padding:2px 8px;border-radius:12px;background:#eef2ff;color:#3730a3;font-size:12px}
.esc{background:#fff1f0;color:#7f1d1d}
.confidence{font-weight:600}
</style>
"""


def init_session():
    if "history" not in st.session_state:
        st.session_state.history = []
    if "session_id" not in st.session_state:
        st.session_state.session_id = os.urandom(6).hex()
    if "agent" not in st.session_state:
        st.session_state.agent = "faq"


def render_sidebar(sop, session_store: SessionStore):
    st.sidebar.title("Session Controls")
    # Demo mode indicator
    # Show Groq client initialization status
    try:
        if not getattr(client, "client", None):
            st.sidebar.warning("Groq client not initialized. Check GROQ_API_KEY and SDK installation.")
    except Exception:
        pass
    st.sidebar.markdown(f"**Session:** `{st.session_state.session_id}`")
    st.sidebar.markdown("---")

    st.sidebar.header("SOP Status")
    st.sidebar.write(sop.get("title", "(no SOP)"))

    st.sidebar.header("Qualification Progress")
    lead = session_store.get_lead() or {}
    # Count only truly populated lead fields (non-empty, non-null)
    completed = sum(1 for f in LEAD_FIELDS if lead.get(f))
    st.sidebar.progress(completed / len(LEAD_FIELDS))
    st.sidebar.markdown(f"**Collected:** {completed}/{len(LEAD_FIELDS)}")

    st.sidebar.header("Escalation Status")
    # show last escalation if present
    try:
        with open("logs/escalations.json","r",encoding="utf-8") as f:
            es = json.load(f)
            last = es[-1] if es else None
            if last:
                st.sidebar.markdown(f"**Last Escalation:** {last.get('report',{}).get('priority')} — {last.get('report',{}).get('reason')}")
            else:
                st.sidebar.markdown("No escalations yet.")
    except Exception:
        st.sidebar.markdown("No escalation log found.")

    st.sidebar.header("Session Analytics")
    hist = session_store.get_history() or []
    st.sidebar.markdown(f"- Conversation length: {len(hist)} messages")
    avg_conf = compute_avg_confidence(hist)
    st.sidebar.markdown(f"- Avg confidence: {avg_conf:.2f}")

    if st.sidebar.button("Generate Session Summary"):
        generate_summary_action(session_store)

    if st.sidebar.button("Export Conversation JSON"):
        export_conversation()

    if st.sidebar.button("Reset Session"):
        session_store.clear()
        # clear UI session keys to avoid stale metrics
        for k in ["history", "last_summary", "input_box", "debug_mode", "agent"]:
            if k in st.session_state:
                try:
                    del st.session_state[k]
                except Exception:
                    st.session_state[k] = None
        st.experimental_rerun()

    # Debug Mode toggle - when enabled, reveal developer controls
    debug = st.sidebar.checkbox("Debug Mode", value=False, help="Enable manual agent selection and raw metadata for debugging")
    st.session_state["debug_mode"] = bool(debug)


def compute_avg_confidence(history):
    vals = []
    for m in history:
        if m.get("role") == "assistant" and isinstance(m.get("meta"), dict):
            c = m.get("meta", {}).get("confidence")
            try:
                vals.append(float(c))
            except Exception:
                pass
    # Return 0.0 when no confidences present to avoid hardcoded perfect score
    return (sum(vals) / len(vals)) if vals else 0.0


def export_conversation():
    try:
        # Export the authoritative session store history when available
        data = []
        try:
            ss = SessionStore(session_id=st.session_state.session_id)
            data = ss.get_history()
        except Exception:
            data = st.session_state.get("history", [])
        st.sidebar.download_button("Download conversation", json.dumps(data, indent=2), file_name=f"conversation_{st.session_state.session_id}.json", mime="application/json")
    except Exception:
        st.sidebar.error("Unable to export conversation.")


def generate_summary_action(session_store: SessionStore):
    # simple wrapper to call summary agent (UI button handler)
    history = session_store.get_history() or st.session_state.history
    qualification = session_store.get_lead()
    # load escalations
    try:
        with open("logs/escalations.json","r",encoding="utf-8") as f:
            escalations = json.load(f)
    except Exception:
        escalations = []

    summary_agent = SummaryAgent(client=client, sop=load_sop("data/sop.json"), memory=session_store)
    summary = summary_agent.handle(history, qualification=qualification, escalations=escalations, session_id=st.session_state.session_id)
    st.sidebar.success("Summary generated — see Summary panel below.")
    st.session_state["last_summary"] = summary


def render_chat(session_store: SessionStore):
    st.markdown(CHAT_CSS, unsafe_allow_html=True)
    chat_col, meta_col = st.columns([3,1])
    with chat_col:
        st.header("Conversation")
        for msg in session_store.get_history():
            render_message(msg)

    # Show summary and controls in meta column
    with meta_col:
        st.header("Summary")
        summary = st.session_state.get("last_summary")
        if summary:
            st.json(summary)
            st.download_button("Download Summary", json.dumps(summary, indent=2), file_name=f"summary_{st.session_state.session_id}.json")
        else:
            st.write("No summary yet.")


def render_message(msg: dict):
    role = msg.get("role")
    text = msg.get("text")
    meta = msg.get("meta")
    ts = msg.get("timestamp") or datetime.utcnow().isoformat()

    if role == "user":
        st.markdown(f"<div class='chat-row user'><div class='chat-bubble'>{text}</div></div>", unsafe_allow_html=True)
        st.markdown(f"<div class='meta' style='text-align:right'>{ts}</div>", unsafe_allow_html=True)
    else:
        # Assistant may include structured meta with confidence, type
        badge_html = ""
        if isinstance(meta, dict):
            conf = meta.get("confidence")
            typ = meta.get("type")
            if conf is not None:
                badge_html += f"<span class='badge confidence'>Conf: {conf}</span> "
            if typ:
                badge_html += f"<span class='badge'>{typ}</span> "
            if meta.get("escalation"):
                badge_html += f"<span class='badge esc'>ESC</span> "

        content = text if isinstance(text, str) else json.dumps(text)
        st.markdown(f"<div class='chat-row assistant'><div class='chat-bubble'>{badge_html}{content}</div></div>", unsafe_allow_html=True)
        st.markdown(f"<div class='meta'>{ts}</div>", unsafe_allow_html=True)
        # If debug mode enabled, show raw metadata below the message for developer inspection
        try:
            if st.session_state.get("debug_mode") and isinstance(meta, dict):
                st.markdown(f"<div class='meta'><pre>{json.dumps(meta, indent=2)}</pre></div>", unsafe_allow_html=True)
        except Exception:
            pass


def post_user_message(text: str, agent_choice: str, session_store: SessionStore):
    text = text.strip()
    if not text:
        st.warning("Please enter a message before sending.")
        return

    # Append user message
    session_store.append_message("user", text)

    # Route to agent
    try:
        # Automatic routing via RouterAgent (default). The agent dropdown remains for debug only.
        router = RouterAgent(client=client, sop=load_sop("data/sop.json"), memory=session_store)
        response = router.handle(text, session_store=session_store)
    except Exception as e:
        # Surface a concise error to the UI and log full details for debugging
        err_msg = str(e) or "unknown error"
        session_store.append_message("assistant", f"Service error: unable to contact model ({err_msg})")
        logger.log({"event": "router_handle_error", "error": err_msg})
        return

    # Normalize response and append (avoid empty bubbles)
    norm = normalize_response(response) if response is not None else normalize_response(None)
    assistant_text = norm.get("assistant_text") or "I'm sorry, I don't have an answer right now. I've flagged this for follow-up."
    meta = {"confidence": norm.get("confidence"), "needs_escalation": norm.get("needs_escalation")}
    # preserve any extra metadata
    if norm.get("metadata"):
        meta.update({"extra": norm.get("metadata")})
    session_store.append_message("assistant", assistant_text)
    # attach meta to last message
    session_store._data.setdefault("history", [])[-1]["meta"] = meta
    # persist metadata so a Streamlit rerun sees the updated confidence
    try:
        session_store.save()
    except Exception:
        pass
    # If agent returned a structured summary in metadata, expose it in UI summary panel
    try:
        summary = norm.get("metadata", {}).get("summary")
        if summary:
            st.session_state["last_summary"] = summary
    except Exception:
        pass
    logger.log({"agent": agent_choice, "user": text, "assistant": response, "normalized": norm})

    # After every assistant response, run escalation check
    try:
        esc_agent = EscalationAgent(client=client, sop=load_sop("data/sop.json"))
        esc_report = esc_agent.handle(session_store.get_history(), last_agent_answer=(response.get('answer') if isinstance(response, dict) else str(response)), faq_confidence=(response.get('confidence') if isinstance(response, dict) else 1.0))
        # Log to escalation file
        EscalationLogger().log({"session_id": st.session_state.session_id, "report": esc_report})
        # Only surface a UI escalation overlay when both the escalation engine and the
        # agent indicate escalation is required, or when the escalation score is extremely high.
        if esc_report.get("needs_escalation") and (
            norm.get("needs_escalation") or esc_report.get("escalation_score", 0) >= 0.95
        ):
            # Annotate the last assistant message with escalation metadata instead of appending a duplicate overlay.
            try:
                last = session_store._data.setdefault("history", [])[-1]
                last_meta = last.get("meta", {}) or {}
                last_meta.update({"escalation": True, "priority": esc_report.get("priority"), "escalation_reasons": esc_report.get("reason")})
                last["meta"] = last_meta
                try:
                    session_store.save()
                except Exception:
                    pass
            except Exception:
                # Fallback to appending a short escalation note if annotation fails
                session_store.append_message("assistant", f"Escalation recommended: {', '.join(esc_report.get('reason', []))}")
                session_store._data.setdefault("history", [])[-1]["meta"] = {"escalation": True, "priority": esc_report.get("priority")}
    except Exception:
        pass


def main():
    init_session()

    sop = load_sop("data/sop.json")
    session_store = SessionStore(session_id=st.session_state.session_id)
    # Keep a lightweight UI cache in session_state in sync with authoritative store
    try:
        st.session_state.history = session_store.get_history()
    except Exception:
        st.session_state.history = []

    # Validate model / API at startup and switch to demo mode on failures
    try:
        ok, reason = client.validate_model()
        if not ok:
            # Turn on demo mode if validation fails
            client.demo_mode = True
            logger.log({"event": "startup_validation", "ok": ok, "reason": reason})
    except Exception as e:
        logger.log({"event": "startup_validation_exception", "error": str(e)})

    # Top layout: sidebar + main
    with st.sidebar:
        render_sidebar(sop, session_store)

    # Main container
    st.title("Closira AI — Support Dashboard")
    cols = st.columns([3, 1])
    with cols[0]:
        render_chat(session_store)

        # Input area
        st.markdown("---")
        # Manual agent selector hidden by default; shown only in Debug Mode
        if st.session_state.get("debug_mode"):
            agent_choice = st.selectbox("Agent (debug only)", ["auto", "faq", "qualification", "escalation", "summary"], index=["auto","faq","qualification","escalation","summary"].index(st.session_state.get("agent","auto")))
            st.session_state["agent"] = agent_choice
        else:
            st.session_state["agent"] = "auto"

        # Use session_state-backed text input and a button callback to clear safely.
        user_text = st.text_input("Message", key="input_box")

        def _send_from_state():
            # Read values from session state, call handler, then clear the input.
            txt = st.session_state.get("input_box", "").strip()
            agent = st.session_state.get("agent", "auto")
            if txt:
                post_user_message(txt, agent, session_store)
            # clearing is safe inside a callback
            st.session_state["input_box"] = ""

        st.button("Send", on_click=_send_from_state)

    with cols[1]:
        st.header("Analytics")
        st.metric("Messages", len(session_store.get_history()))
        # Count only truly populated lead fields
        lead = session_store.get_lead() or {}
        collected = sum(1 for f in LEAD_FIELDS if lead.get(f))
        st.metric("Lead Progress", f"{collected}/{len(LEAD_FIELDS)}")
        st.metric("Avg Confidence", f"{compute_avg_confidence(session_store.get_history()):.2f}")


if __name__ == "__main__":
    main()
