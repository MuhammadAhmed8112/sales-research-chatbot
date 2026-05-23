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
)

st.markdown("""
<style>
.metric-card {
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
    border: 1px solid #0f3460;
    border-radius: 12px;
    padding: 20px;
    margin: 8px 0;
}
.email-box {
    background: #0d1117;
    border: 1px solid #30363d;
    border-left: 4px solid #6c63ff;
    border-radius: 8px;
    padding: 16px;
    font-family: 'Courier New', monospace;
    font-size: 0.85em;
    white-space: pre-wrap;
    line-height: 1.6;
}
</style>
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
    st.title("🎯 AI Sales Research Agent")
    st.caption(
        "Describe a prospect and the agent researches them in real-time, "
        "scores the lead, and writes a personalized outreach email."
    )

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if user_input := st.chat_input("Who's the prospect? e.g. 'I'm looking at Acme Corp, they build industrial IoT sensors'"):
        st.session_state.messages.append({"role": "user", "content": user_input})
        st.session_state.lc_messages.append(HumanMessage(content=user_input))

        with st.chat_message("user"):
            st.markdown(user_input)

        with st.chat_message("assistant"):
            with st.spinner("Researching prospect..."):
                result = st.session_state.agent.invoke(
                    {"messages": st.session_state.lc_messages}
                )

                # Last non-empty AI message
                ai_msgs = [
                    m for m in result["messages"]
                    if hasattr(m, "type") and m.type == "ai" and m.content
                ]
                response_text = ai_msgs[-1].content if ai_msgs else "Could not process that. Please try again."

                # Parse tool outputs
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

# ── Sidebar panel ─────────────────────────────────────────────────────────────
with col2:
    st.subheader("📊 Live Insights")

    if st.session_state.lead_score:
        d = st.session_state.lead_score
        tier = d.get("tier", "")
        score = d.get("score", 0)
        color = {"Hot": "#ff4444", "Warm": "#ff9944", "Cold": "#4488ff"}.get(tier, "#888")
        tier_emoji = {"Hot": "🔴", "Warm": "🟡", "Cold": "🔵"}.get(tier, "⚪")

        st.markdown(f"""
<div class="metric-card">
  <div style="font-size:0.75em;color:#888;letter-spacing:0.1em">LEAD SCORE</div>
  <div style="font-size:2.8em;font-weight:bold;color:{color};line-height:1.1">
    {score}<span style="font-size:0.4em;color:#888"> / 10</span>
  </div>
  <div style="font-size:1.1em;margin:6px 0">{tier_emoji} <strong>{tier}</strong></div>
  <hr style="border-color:#333;margin:10px 0">
  <div style="font-size:0.8em;color:#aaa">{d.get("reasoning", "")}</div>
  <hr style="border-color:#333;margin:10px 0">
  <div style="font-size:0.7em;color:#888;letter-spacing:0.1em">RECOMMENDED NEXT STEP</div>
  <div style="font-size:0.9em;color:#7eb8f7;margin-top:4px">{d.get("recommended_next_step", "")}</div>
</div>
""", unsafe_allow_html=True)
    else:
        st.info("Lead score will appear here after qualification.")

    st.divider()

    if st.session_state.email_draft:
        st.subheader("✉️ Outreach Email")
        st.markdown(
            f'<div class="email-box">{st.session_state.email_draft}</div>',
            unsafe_allow_html=True,
        )
        st.download_button(
            label="⬇️ Download Email",
            data=st.session_state.email_draft,
            file_name="outreach_email.txt",
            mime="text/plain",
            use_container_width=True,
        )
    else:
        st.info("Personalized outreach email will appear here once the lead is qualified.")

    st.divider()

    if st.button("🔄 New Prospect", use_container_width=True):
        st.session_state.messages = []
        st.session_state.lc_messages = []
        st.session_state.lead_score = None
        st.session_state.email_draft = None
        st.rerun()
