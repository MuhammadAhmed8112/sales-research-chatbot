import streamlit as st
import os
import json
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage

load_dotenv()

st.set_page_config(
    page_title="AI Sales Research Agent",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
/* ── Google Font ── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

/* ── Hide Streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }
.stDeployButton, [data-testid="stToolbar"] { display: none !important; }
.block-container { padding-top: 0 !important; }

/* ── Page background ── */
.stApp { background: #07070f; }

/* ── Top header bar ── */
.app-header {
    background: linear-gradient(135deg, #0f0c29 0%, #1a0a2e 50%, #0a1628 100%);
    border-bottom: 1px solid #1e1b4b;
    padding: 18px 28px;
    margin: -4px -4px 24px -4px;
    display: flex;
    align-items: center;
    gap: 14px;
}
.app-header-icon { font-size: 2em; filter: drop-shadow(0 0 10px #7c3aed80); }
.app-header-title {
    font-size: 1.45em;
    font-weight: 800;
    background: linear-gradient(135deg, #fff 0%, #a78bfa 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin: 0; line-height: 1.2;
}
.app-header-sub { font-size: 0.8em; color: #6b7280; margin: 2px 0 0 0; }

/* ── Chat messages ── */
[data-testid="stChatMessage"] {
    border-radius: 12px !important;
    padding: 12px 16px !important;
    margin: 6px 0 !important;
}
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) {
    background: linear-gradient(135deg, #1e1b4b 0%, #1a1a2e 100%) !important;
    border: 1px solid #2d2d6e !important;
}
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) {
    background: linear-gradient(135deg, #0f172a 0%, #111827 100%) !important;
    border: 1px solid #1e293b !important;
}

/* ── Chat input ── */
[data-testid="stChatInput"] > div {
    background: #111827 !important;
    border: 1px solid #374151 !important;
    border-radius: 14px !important;
    box-shadow: 0 0 0 0 #6c63ff00;
    transition: box-shadow 0.2s ease !important;
}
[data-testid="stChatInput"] > div:focus-within {
    border-color: #6c63ff !important;
    box-shadow: 0 0 0 3px #6c63ff22 !important;
}
[data-testid="stChatInput"] textarea { color: #e2e8f0 !important; font-size: 0.93em !important; }

/* ── Right panel card base ── */
.panel-card {
    background: linear-gradient(145deg, #111827 0%, #0d1117 100%);
    border: 1px solid #1f2937;
    border-radius: 16px;
    padding: 20px;
    margin: 0 0 16px 0;
    box-shadow: 0 4px 24px rgba(0,0,0,0.5);
    position: relative;
    overflow: hidden;
}
.panel-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0; height: 3px;
    background: linear-gradient(90deg, #6c63ff, #a78bfa);
    border-radius: 16px 16px 0 0;
}

/* ── Section label ── */
.section-label {
    font-size: 0.68em;
    font-weight: 700;
    color: #6b7280;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    margin-bottom: 10px;
    display: flex;
    align-items: center;
    gap: 6px;
}

/* ── Score display ── */
.score-number {
    font-size: 3.4em;
    font-weight: 800;
    line-height: 1;
    margin: 4px 0 2px 0;
}
.score-denom { font-size: 0.3em; font-weight: 400; color: #4b5563; }

/* ── Tier badge ── */
.tier-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 3px 12px;
    border-radius: 20px;
    font-size: 0.78em;
    font-weight: 700;
    margin: 8px 0 12px 0;
    letter-spacing: 0.04em;
}
.tier-hot  { background: #7f1d1d30; color: #fca5a5; border: 1px solid #7f1d1d; }
.tier-warm { background: #78350f30; color: #fcd34d; border: 1px solid #78350f; }
.tier-cold { background: #1e3a5f30; color: #93c5fd; border: 1px solid #1e3a8a; }

/* ── Score progress bar ── */
.bar-track {
    background: #1f2937;
    border-radius: 6px;
    height: 7px;
    margin: 12px 0 16px 0;
    overflow: hidden;
}
.bar-fill {
    height: 100%;
    border-radius: 6px;
    animation: growBar 0.9s cubic-bezier(.4,0,.2,1) forwards;
}
@keyframes growBar { from { width: 0% } }

/* ── Reasoning & next step ── */
.reasoning-text { font-size: 0.82em; color: #9ca3af; line-height: 1.65; margin: 0; }
.divider-line { border: none; border-top: 1px solid #1f2937; margin: 14px 0; }
.next-step-text { font-size: 0.86em; color: #7dd3fc; line-height: 1.55; }

/* ── Email card ── */
.email-card {
    background: #0d1117;
    border: 1px solid #21262d;
    border-radius: 14px;
    overflow: hidden;
    margin-bottom: 10px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.4);
}
.email-card-header {
    background: #161b22;
    padding: 10px 16px;
    border-bottom: 1px solid #21262d;
    display: flex;
    align-items: center;
    justify-content: space-between;
    font-size: 0.78em;
    font-weight: 600;
    color: #8b949e;
    letter-spacing: 0.06em;
}
.email-draft-badge {
    background: #1f2937;
    color: #6b7280;
    border-radius: 4px;
    padding: 2px 7px;
    font-size: 0.85em;
    font-weight: 500;
}
.email-body {
    padding: 16px;
    font-family: 'Courier New', monospace;
    font-size: 0.82em;
    color: #c9d1d9;
    white-space: pre-wrap;
    line-height: 1.72;
    max-height: 340px;
    overflow-y: auto;
}

/* ── Empty states ── */
.empty-state {
    text-align: center;
    padding: 28px 16px 24px;
}
.empty-state-icon { font-size: 2.4em; opacity: 0.25; margin-bottom: 10px; }
.empty-state-text { font-size: 0.82em; color: #4b5563; line-height: 1.6; }

/* ── Buttons ── */
.stButton > button {
    background: linear-gradient(135deg, #6c63ff 0%, #4f46e5 100%) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    font-size: 0.88em !important;
    padding: 10px 18px !important;
    box-shadow: 0 4px 14px rgba(108,99,255,0.3) !important;
    transition: all 0.2s ease !important;
}
.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 20px rgba(108,99,255,0.45) !important;
}
.stDownloadButton > button {
    background: #111827 !important;
    color: #d1d5db !important;
    border: 1px solid #374151 !important;
    border-radius: 10px !important;
    font-weight: 500 !important;
    box-shadow: none !important;
}
.stDownloadButton > button:hover { background: #1f2937 !important; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: #1f2937; border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: #374151; }

/* ── Panel heading ── */
.panel-heading {
    font-size: 0.9em;
    font-weight: 700;
    color: #d1d5db;
    margin: 0 0 14px 0;
    display: flex;
    align-items: center;
    gap: 7px;
}
</style>
""", unsafe_allow_html=True)

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="app-header">
  <div class="app-header-icon">🎯</div>
  <div>
    <div class="app-header-title">AI Sales Research Agent</div>
    <div class="app-header-sub">Real-time prospect research · Lead scoring · Personalized outreach</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── Session state ─────────────────────────────────────────────────────────────
for key, val in [
    ("messages", []),
    ("lc_messages", []),
    ("lead_score", None),
    ("email_draft", None),
    ("agent", None),
]:
    if key not in st.session_state:
        st.session_state[key] = val

if st.session_state.agent is None:
    from agent import get_agent
    st.session_state.agent = get_agent()

# ── Layout ────────────────────────────────────────────────────────────────────
col1, col2 = st.columns([2, 1], gap="large")

with col1:
    # Chat history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Empty state when no messages yet
    if not st.session_state.messages:
        st.markdown("""
<div style="text-align:center;padding:48px 24px;color:#374151;">
  <div style="font-size:3em;margin-bottom:16px;opacity:0.3">🔍</div>
  <div style="font-size:1em;font-weight:600;color:#4b5563;margin-bottom:8px">
    Start by describing a prospect
  </div>
  <div style="font-size:0.85em;color:#374151;line-height:1.7;">
    e.g. <em>"Acme Corp builds industrial IoT sensors for manufacturing plants"</em><br>
    The agent will research them, score the lead, and draft a personalized email.
  </div>
</div>
""", unsafe_allow_html=True)

    if user_input := st.chat_input("Who's the prospect? e.g. 'Acme Corp builds industrial IoT sensors...'"):
        st.session_state.messages.append({"role": "user", "content": user_input})
        st.session_state.lc_messages.append(HumanMessage(content=user_input))

        with st.chat_message("user"):
            st.markdown(user_input)

        with st.chat_message("assistant"):
            with st.spinner("Researching prospect..."):
                result = st.session_state.agent.invoke(
                    {"messages": st.session_state.lc_messages}
                )

                ai_msgs = [
                    m for m in result["messages"]
                    if hasattr(m, "type") and m.type == "ai" and m.content
                ]
                response_text = ai_msgs[-1].content if ai_msgs else "Could not process that. Please try again."

                for m in result["messages"]:
                    if hasattr(m, "type") and m.type == "tool":
                        tool_name = getattr(m, "name", "")
                        if tool_name == "score_lead":
                            try:
                                raw = m.content.strip().lstrip("```json").lstrip("```").rstrip("```")
                                st.session_state.lead_score = json.loads(raw)
                            except Exception:
                                pass
                        elif tool_name == "generate_outreach_email":
                            st.session_state.email_draft = m.content

                st.session_state.lc_messages = result["messages"]
                st.markdown(response_text)
                st.session_state.messages.append({"role": "assistant", "content": response_text})

# ── Right panel ───────────────────────────────────────────────────────────────
with col2:

    # ── Lead Score Card ──
    st.markdown('<div class="panel-heading">📊 Live Insights</div>', unsafe_allow_html=True)

    if st.session_state.lead_score:
        d = st.session_state.lead_score
        tier  = d.get("tier", "")
        score = d.get("score", 0)

        color_map = {"Hot": "#f87171", "Warm": "#fbbf24", "Cold": "#60a5fa"}
        badge_map = {"Hot": "tier-hot", "Warm": "tier-warm", "Cold": "tier-cold"}
        emoji_map = {"Hot": "🔴", "Warm": "🟡", "Cold": "🔵"}

        color      = color_map.get(tier, "#9ca3af")
        badge_cls  = badge_map.get(tier, "tier-cold")
        tier_emoji = emoji_map.get(tier, "⚪")
        bar_pct    = int(score) * 10

        st.markdown(f"""
<div class="panel-card">
  <div class="section-label">⚡ Lead Score</div>
  <div class="score-number" style="color:{color}">
    {score}<span class="score-denom"> / 10</span>
  </div>
  <span class="tier-badge {badge_cls}">{tier_emoji} {tier}</span>
  <div class="bar-track">
    <div class="bar-fill" style="width:{bar_pct}%;background:linear-gradient(90deg,{color}88,{color});"></div>
  </div>
  <p class="reasoning-text">{d.get("reasoning", "")}</p>
  <hr class="divider-line">
  <div class="section-label">💡 Recommended Next Step</div>
  <div class="next-step-text">{d.get("recommended_next_step", "")}</div>
</div>
""", unsafe_allow_html=True)

    else:
        st.markdown("""
<div class="panel-card">
  <div class="empty-state">
    <div class="empty-state-icon">📈</div>
    <div class="empty-state-text">Lead score will appear here<br>after the prospect is qualified.</div>
  </div>
</div>
""", unsafe_allow_html=True)

    # ── Outreach Email Card ──
    st.markdown('<div class="panel-heading">✉️ Outreach Email</div>', unsafe_allow_html=True)

    if st.session_state.email_draft:
        st.markdown(f"""
<div class="email-card">
  <div class="email-card-header">
    <span>📧 DRAFT</span>
    <span class="email-draft-badge">outreach_email.txt</span>
  </div>
  <div class="email-body">{st.session_state.email_draft}</div>
</div>
""", unsafe_allow_html=True)
        st.download_button(
            label="⬇️ Download Email",
            data=st.session_state.email_draft,
            file_name="outreach_email.txt",
            mime="text/plain",
            use_container_width=True,
        )
    else:
        st.markdown("""
<div class="panel-card">
  <div class="empty-state">
    <div class="empty-state-icon">✉️</div>
    <div class="empty-state-text">Personalized outreach email will appear<br>once the lead is qualified.</div>
  </div>
</div>
""", unsafe_allow_html=True)

    # ── Reset ──
    st.markdown("<div style='margin-top:4px'>", unsafe_allow_html=True)
    if st.button("🔄 New Prospect", use_container_width=True):
        st.session_state.messages     = []
        st.session_state.lc_messages  = []
        st.session_state.lead_score   = None
        st.session_state.email_draft  = None
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
