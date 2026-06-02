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
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

/* ── Hide Streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }
.stDeployButton, [data-testid="stToolbar"] { display: none !important; }
.block-container { padding-top: 1rem !important; padding-bottom: 100px !important; }

/* ── Page background ── */
.stApp { background: #080808; }

/* ── Header ── */
.app-header {
    background: #0d0d0d;
    border-bottom: 2px solid #9b1c1c;
    border-radius: 12px;
    padding: 16px 24px;
    margin-bottom: 24px;
    display: flex;
    align-items: center;
    gap: 14px;
    box-shadow: 0 2px 20px rgba(185,28,28,0.2);
}
.app-header-icon { font-size: 2em; filter: drop-shadow(0 0 8px #b91c1c88); }
.app-header-title {
    font-size: 1.4em;
    font-weight: 800;
    background: linear-gradient(135deg, #ffffff 0%, #fca5a5 60%, #b91c1c 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin: 0; line-height: 1.2;
}
.app-header-sub { font-size: 0.78em; color: #52525b; margin: 3px 0 0 0; }

/* ── Chat messages ── */
[data-testid="stChatMessage"] {
    border-radius: 12px !important;
    padding: 12px 16px !important;
    margin: 6px 0 !important;
}
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) {
    background: linear-gradient(135deg, #1a0808 0%, #140606 100%) !important;
    border: 1px solid #450a0a !important;
}
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) {
    background: #0e0e0e !important;
    border: 1px solid #1c1c1c !important;
}

/* ── Chat input styling (let Streamlit handle positioning) ── */
[data-testid="stChatInput"] > div {
    background: #111111 !important;
    border: 1px solid #450a0a !important;
    border-radius: 14px !important;
    transition: border-color 0.2s, box-shadow 0.2s !important;
}
[data-testid="stChatInput"] > div:focus-within {
    border-color: #b91c1c !important;
    box-shadow: 0 0 0 3px #b91c1c22 !important;
}
[data-testid="stChatInput"] textarea {
    color: #e2e8f0 !important;
    font-size: 0.93em !important;
    background: transparent !important;
}

/* ── Right panel card ── */
.panel-card {
    background: #0e0e0e;
    border: 1px solid #1c1c1c;
    border-radius: 16px;
    padding: 20px;
    margin: 0 0 16px 0;
    box-shadow: 0 4px 24px rgba(0,0,0,0.6);
    position: relative;
    overflow: hidden;
}
.panel-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0; height: 3px;
    background: linear-gradient(90deg, #7f1d1d, #b91c1c, #ef4444);
    border-radius: 16px 16px 0 0;
}

/* ── Section label ── */
.section-label {
    font-size: 0.67em;
    font-weight: 700;
    color: #52525b;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    margin-bottom: 10px;
}

/* ── Score ── */
.score-number {
    font-size: 3.4em;
    font-weight: 800;
    line-height: 1;
    margin: 4px 0 2px 0;
}
.score-denom { font-size: 0.3em; font-weight: 400; color: #3f3f46; }

/* ── Tier badges ── */
.tier-badge {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    padding: 3px 12px;
    border-radius: 20px;
    font-size: 0.77em;
    font-weight: 700;
    margin: 8px 0 12px 0;
    letter-spacing: 0.04em;
}
.tier-hot  { background: #450a0a; color: #fca5a5; border: 1px solid #7f1d1d; }
.tier-warm { background: #451a03; color: #fcd34d; border: 1px solid #92400e; }
.tier-cold { background: #042f2e; color: #5eead4; border: 1px solid #0f766e; }

/* ── Score bar ── */
.bar-track {
    background: #1c1c1c;
    border-radius: 6px;
    height: 6px;
    margin: 12px 0 16px 0;
    overflow: hidden;
}
.bar-fill {
    height: 100%;
    border-radius: 6px;
    animation: growBar 1s cubic-bezier(.4,0,.2,1) forwards;
}
@keyframes growBar { from { width: 0% } }

.reasoning-text { font-size: 0.82em; color: #a1a1aa; line-height: 1.65; margin: 0; }
.divider-line   { border: none; border-top: 1px solid #1c1c1c; margin: 14px 0; }
.next-step-text { font-size: 0.86em; color: #2dd4bf; line-height: 1.55; }

/* ── Email card ── */
.email-card {
    background: #0a0a0a;
    border: 1px solid #1c1c1c;
    border-left: 3px solid #b91c1c;
    border-radius: 12px;
    overflow: hidden;
    margin-bottom: 10px;
}
.email-card-header {
    background: #0e0e0e;
    padding: 9px 14px;
    border-bottom: 1px solid #1c1c1c;
    display: flex;
    align-items: center;
    justify-content: space-between;
    font-size: 0.75em;
    font-weight: 600;
    color: #71717a;
    letter-spacing: 0.06em;
}
.email-draft-badge {
    background: #141414;
    color: #52525b;
    border-radius: 4px;
    padding: 2px 7px;
    font-size: 0.88em;
}
.email-body {
    padding: 14px;
    font-family: 'Courier New', monospace;
    font-size: 0.8em;
    color: #d4d4d8;
    white-space: pre-wrap;
    line-height: 1.72;
    max-height: 320px;
    overflow-y: auto;
}

/* ── Empty states ── */
.empty-state { text-align: center; padding: 60px 16px; }
.empty-state-icon { font-size: 2.5em; opacity: 0.2; margin-bottom: 14px; }
.empty-state-title { font-size: 0.95em; font-weight: 600; color: #52525b; margin-bottom: 8px; }
.empty-state-text { font-size: 0.82em; color: #3f3f46; line-height: 1.75; }
.empty-state-hint { color: #52525b; font-style: italic; }

/* ── Panel heading ── */
.panel-heading {
    font-size: 0.88em;
    font-weight: 700;
    color: #d4d4d8;
    margin: 0 0 12px 0;
    display: flex;
    align-items: center;
    gap: 7px;
}

/* ── Buttons ── */
.stButton > button {
    background: linear-gradient(135deg, #b91c1c 0%, #7f1d1d 100%) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    font-size: 0.87em !important;
    box-shadow: 0 4px 14px rgba(185,28,28,0.35) !important;
    transition: all 0.2s ease !important;
}
.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 20px rgba(185,28,28,0.5) !important;
}
.stDownloadButton > button {
    background: #111111 !important;
    color: #a1a1aa !important;
    border: 1px solid #27272a !important;
    border-radius: 10px !important;
    font-weight: 500 !important;
    box-shadow: none !important;
}
.stDownloadButton > button:hover {
    background: #1c1c1c !important;
    color: #e2e8f0 !important;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: #27272a; border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: #3f3f46; }
</style>
""", unsafe_allow_html=True)

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="app-header">
  <div class="app-header-icon">🎯</div>
  <div>
    <div class="app-header-title">AI Sales Research Agent</div>
    <div class="app-header-sub">Real-time prospect research &nbsp;·&nbsp; Lead scoring &nbsp;·&nbsp; Personalized outreach</div>
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
    # Empty state
    if not st.session_state.messages:
        st.markdown("""
<div class="empty-state">
  <div class="empty-state-icon">🔍</div>
  <div class="empty-state-title">Start by describing a prospect</div>
  <div class="empty-state-text">
    e.g. <span class="empty-state-hint">"Acme Corp builds industrial IoT sensors for manufacturing plants"</span><br><br>
    The agent will research them, score the lead,<br>and draft a personalized outreach email.
  </div>
</div>
""", unsafe_allow_html=True)

    # Chat history — always above the input
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Chat input at the bottom
    if user_input := st.chat_input("Who's the prospect? e.g. 'Acme Corp — 50-person IoT company, open budget...'"):
        st.session_state.messages.append({"role": "user", "content": user_input})
        st.session_state.lc_messages.append(HumanMessage(content=user_input))

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
            st.session_state.messages.append({"role": "assistant", "content": response_text})

        st.rerun()  # Re-render so messages appear above the input

# ── Right panel ───────────────────────────────────────────────────────────────
with col2:

    # Lead Score
    st.markdown('<div class="panel-heading">📊 Live Insights</div>', unsafe_allow_html=True)

    if st.session_state.lead_score:
        d      = st.session_state.lead_score
        tier   = d.get("tier", "")
        score  = d.get("score", 0)

        color_map = {"Hot": "#ef4444", "Warm": "#f59e0b", "Cold": "#2dd4bf"}
        badge_map = {"Hot": "tier-hot",  "Warm": "tier-warm", "Cold": "tier-cold"}
        emoji_map = {"Hot": "🔴",        "Warm": "🟡",        "Cold": "🔵"}

        color      = color_map.get(tier, "#a1a1aa")
        badge_cls  = badge_map.get(tier, "tier-cold")
        tier_emoji = emoji_map.get(tier, "⚪")
        bar_pct    = int(score) * 10

        st.markdown(f"""
<div class="panel-card">
  <div class="section-label">⚡ Lead Score</div>
  <div class="score-number" style="color:{color}">
    {score}<span class="score-denom"> / 10</span>
  </div>
  <span class="tier-badge {badge_cls}">{tier_emoji}&nbsp;{tier}</span>
  <div class="bar-track">
    <div class="bar-fill" style="width:{bar_pct}%;background:linear-gradient(90deg,{color}66,{color});"></div>
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
  <div style="text-align:center;padding:24px 8px;">
    <div style="font-size:2em;opacity:0.15;margin-bottom:10px;">📈</div>
    <div style="font-size:0.8em;color:#3f3f46;line-height:1.6;">Lead score will appear here<br>after the prospect is qualified.</div>
  </div>
</div>
""", unsafe_allow_html=True)

    # Outreach Email
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
  <div style="text-align:center;padding:24px 8px;">
    <div style="font-size:2em;opacity:0.15;margin-bottom:10px;">✉️</div>
    <div style="font-size:0.8em;color:#3f3f46;line-height:1.6;">Personalized outreach email will appear<br>once the lead is qualified.</div>
  </div>
</div>
""", unsafe_allow_html=True)

    # Reset
    if st.button("🔄 New Prospect", use_container_width=True):
        st.session_state.messages    = []
        st.session_state.lc_messages = []
        st.session_state.lead_score  = None
        st.session_state.email_draft = None
        st.rerun()
