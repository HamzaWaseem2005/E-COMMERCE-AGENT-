"""
ShopSense AI — E-commerce Support Agent UI
Talks to the FastAPI backend (agent.py) running at http://localhost:8000/chat
"""

import streamlit as st
import requests
import uuid
from datetime import datetime

# ------------------------------------------------------------------
# PAGE CONFIG
# ------------------------------------------------------------------
st.set_page_config(
    page_title="ShopSense AI — Support",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded",
)

API_URL = "http://localhost:8000/chat"

# ------------------------------------------------------------------
# SESSION STATE
# ------------------------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []          # [{"role": "user"/"assistant", "content": str, "time": str}]
if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())
if "pending_prompt" not in st.session_state:
    st.session_state.pending_prompt = None

# ------------------------------------------------------------------
# CUSTOM CSS — theme only. Message CONTENT is rendered by Streamlit's
# own st.chat_message, so nothing here can corrupt agent replies.
# ------------------------------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800&display=swap');

html, body, [class*="css"] { font-family: 'Poppins', sans-serif; }

/* Full-viewport animated gradient — covers header + body + bottom bar */
html, body, .stApp,
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
[data-testid="stHeader"],
[data-testid="stBottom"] {
    background: linear-gradient(-45deg, #0f0c29, #302b63, #24243e, #1a1a2e) !important;
    background-size: 400% 400% !important;
    animation: gradientShift 18s ease infinite;
}
[data-testid="stHeader"] { background-color: transparent !important; }

@keyframes gradientShift {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

.block-container { padding-top: 1.5rem; max-width: 900px; }

/* Hero header */
.hero-title {
    font-size: 2.6rem;
    font-weight: 800;
    background: linear-gradient(90deg, #00f5d4, #9b5de5, #f15bb5, #00f5d4);
    background-size: 300% auto;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    animation: shine 6s linear infinite;
    text-align: center;
    margin-bottom: 0;
}
@keyframes shine { to { background-position: 300% center; } }

.hero-subtitle {
    text-align: center;
    color: #c9c9e0;
    font-size: 1.05rem;
    font-weight: 300;
    margin-top: 4px;
    animation: fadeInUp 0.8s ease;
}
@keyframes fadeInUp {
    from { opacity: 0; transform: translateY(12px); }
    to { opacity: 1; transform: translateY(0); }
}

.status-pill {
    display: flex; align-items: center; gap: 8px;
    background: rgba(0, 245, 212, 0.12);
    border: 1px solid rgba(0, 245, 212, 0.4);
    color: #00f5d4;
    padding: 6px 16px;
    border-radius: 999px;
    font-size: 0.8rem;
    font-weight: 500;
    margin: 14px auto 22px auto;
    width: fit-content;
}
.pulse-dot {
    width: 8px; height: 8px;
    background: #00f5d4;
    border-radius: 50%;
    animation: pulse 1.8s infinite;
}
@keyframes pulse {
    0% { box-shadow: 0 0 0 0 rgba(0,245,212, 0.6); }
    70% { box-shadow: 0 0 0 10px rgba(0,245,212, 0); }
    100% { box-shadow: 0 0 0 0 rgba(0,245,212, 0); }
}

.glass-card {
    background: rgba(255, 255, 255, 0.06);
    border: 1px solid rgba(255, 255, 255, 0.12);
    backdrop-filter: blur(14px);
    border-radius: 18px;
    padding: 20px 22px;
    animation: fadeInUp 0.5s ease;
    text-align: center;
}

/* Chat message bubbles (Streamlit's native chat_message container) */
[data-testid="stChatMessage"] {
    border-radius: 18px;
    padding: 12px 16px !important;
    margin-bottom: 14px;
    animation: slideIn 0.4s ease;
}

/* Assistant messages */
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) {
    background: rgba(255,255,255,0.07) !important;
    border: 1px solid rgba(255,255,255,0.14);
    animation: slideInLeft 0.4s ease;
}

/* User messages */
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) {
    background: linear-gradient(135deg, rgba(123,47,247,0.35), rgba(241,7,163,0.28)) !important;
    border: 1px solid rgba(255,255,255,0.16);
    animation: slideInRight 0.4s ease;
}

@keyframes slideIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}
@keyframes slideInLeft {
    from { opacity: 0; transform: translateX(-24px); }
    to { opacity: 1; transform: translateX(0); }
}
@keyframes slideInRight {
    from { opacity: 0; transform: translateX(24px); }
    to { opacity: 1; transform: translateX(0); }
}

/* Force bright, readable text inside every chat message */
[data-testid="stChatMessage"] p,
[data-testid="stChatMessage"] span,
[data-testid="stChatMessage"] li,
[data-testid="stChatMessage"] strong,
[data-testid="stChatMessageContent"] * {
    color: #f3f3fb !important;
    opacity: 1 !important;
}
[data-testid="stChatMessage"] [data-testid="stCaptionContainer"] p {
    color: #b8b8d0 !important;
    font-size: 0.72rem !important;
}

/* Avatar circles */
[data-testid="stChatMessageAvatarUser"],
[data-testid="stChatMessageAvatarAssistant"] {
    background: #1c1c3a !important;
    border: 1px solid rgba(255,255,255,0.15) !important;
}

/* Typing spinner text */
[data-testid="stSpinner"] p {
    color: #00f5d4 !important;
    font-style: italic;
}

/* Metric cards in sidebar */
.metric-box {
    background: rgba(255,255,255,0.06);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 14px;
    padding: 14px;
    text-align: center;
    transition: transform 0.2s ease;
}
.metric-box:hover { transform: scale(1.04); }
.metric-num {
    font-size: 1.6rem;
    font-weight: 700;
    background: linear-gradient(90deg,#00f5d4,#9b5de5);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.metric-label { font-size: 0.75rem; color: #b8b8d0; }

/* Buttons */
div[data-testid="stButton"] button {
    background: linear-gradient(135deg, rgba(123,47,247,0.25), rgba(241,7,163,0.25));
    border: 1px solid rgba(255,255,255,0.18);
    color: #f1f1fb;
    border-radius: 12px;
    padding: 8px 14px;
    font-weight: 500;
    transition: all 0.25s ease;
    width: 100%;
}
div[data-testid="stButton"] button:hover {
    border-color: #00f5d4;
    box-shadow: 0 0 16px rgba(0,245,212,0.4);
    transform: translateY(-2px);
    color: #00f5d4;
}

/* Chat input — simple solid black box, white text */
[data-testid="stChatInput"],
[data-testid="stChatInputContainer"],
[data-testid="stChatInput"] div[data-baseweb="textarea"],
[data-testid="stChatInput"] div[data-baseweb="base-input"],
[data-testid="stChatInput"] textarea {
    background-color: #000000 !important;
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
    caret-color: #ffffff !important;
}
[data-testid="stChatInput"] textarea::placeholder {
    color: #aaaaaa !important;
    -webkit-text-fill-color: #aaaaaa !important;
    opacity: 1 !important;
}
/* Send button */
[data-testid="stChatInputSubmitButton"] {
    background: linear-gradient(135deg, #7b2ff7, #f107a3) !important;
    border-radius: 12px !important;
    border: none !important;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}
[data-testid="stChatInputSubmitButton"]:hover {
    transform: scale(1.08);
    box-shadow: 0 0 14px rgba(241,7,163,0.5);
}
[data-testid="stChatInputSubmitButton"] svg {
    fill: white !important;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #14142b, #1c1c3a);
    border-right: 1px solid rgba(255,255,255,0.08);
}

/* Typing indicator dots */
.typing-dots { display: flex; gap: 5px; padding: 6px 2px; }
.typing-dots span {
    width: 8px; height: 8px;
    background: #00f5d4;
    border-radius: 50%;
    animation: typingBounce 1.2s infinite ease-in-out;
}
.typing-dots span:nth-child(2) { animation-delay: 0.2s; }
.typing-dots span:nth-child(3) { animation-delay: 0.4s; }
@keyframes typingBounce {
    0%, 60%, 100% { transform: translateY(0); opacity: 0.5; }
    30% { transform: translateY(-6px); opacity: 1; }
}

#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ------------------------------------------------------------------
# SIDEBAR
# ------------------------------------------------------------------
with st.sidebar:
    st.markdown("<h2 style='color:#00f5d4;'>🛍️ ShopSense AI</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color:#b8b8d0; font-size:0.85rem;'>Your always-on order & delivery assistant.</p>", unsafe_allow_html=True)
    st.markdown("---")

    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"""<div class="metric-box"><div class="metric-num">{len(st.session_state.messages)}</div><div class="metric-label">Messages</div></div>""", unsafe_allow_html=True)
    with c2:
        st.markdown("""<div class="metric-box"><div class="metric-num">24/7</div><div class="metric-label">Availability</div></div>""", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("<p style='color:#c9c9e0; font-size:0.85rem; font-weight:600;'>⚡ Quick Asks</p>", unsafe_allow_html=True)

    quick_prompts = {
        "📦 Track my last order": "Track my last order",
        "🛒 What products do you sell?": "What products do you sell?",
        "↩️ What's your return policy?": "What's your return policy?",
        "🚚 Delivery time estimate": "What's the typical delivery time estimate?",
    }
    for label, prompt in quick_prompts.items():
        if st.button(label, key=label):
            st.session_state.pending_prompt = prompt

    st.markdown("---")
    if st.button("🗑️ Clear conversation", key="clear_btn"):
        st.session_state.messages = []
        st.session_state.thread_id = str(uuid.uuid4())
        st.rerun()

    st.markdown("<div style='margin-top:30px; text-align:center; color:#6b6b8a; font-size:0.72rem;'>Powered by DeepAgents · LangGraph</div>", unsafe_allow_html=True)

# ------------------------------------------------------------------
# HEADER
# ------------------------------------------------------------------
st.markdown("<div class='hero-title'>ShopSense AI Support</div>", unsafe_allow_html=True)
st.markdown("<div class='hero-subtitle'>Instant answers on orders, tracking & products — powered by AI</div>", unsafe_allow_html=True)
st.markdown("""
<div style="display:flex; justify-content:center;">
    <div class="status-pill"><span class="pulse-dot"></span> Agent online</div>
</div>
""", unsafe_allow_html=True)

# ------------------------------------------------------------------
# WELCOME CARD (only when chat is empty)
# ------------------------------------------------------------------
if not st.session_state.messages:
    st.markdown("""
    <div class="glass-card">
        <h3 style="color:#f1f1fb; margin-bottom:6px;">👋 Welcome!</h3>
        <p style="color:#b8b8d0; margin:0;">Ask me about your order status, delivery dates, tracking numbers,
        or anything about our products. Try one of the quick asks in the sidebar to get started.</p>
    </div>
    """, unsafe_allow_html=True)
    st.write("")

# ------------------------------------------------------------------
# RENDER CHAT HISTORY — using Streamlit's own safe chat components
# ------------------------------------------------------------------
for msg in st.session_state.messages:
    avatar = "🧑" if msg["role"] == "user" else "🤖"
    with st.chat_message(msg["role"], avatar=avatar):
        st.write(msg["content"])
        st.caption(msg["time"])

# ------------------------------------------------------------------
# BACKEND CALL
# ------------------------------------------------------------------
def extract_reply(result: dict) -> str:
    try:
        response = result.get("response", {})
        messages = response.get("messages", [])
        if messages:
            last = messages[-1]
            if isinstance(last, dict):
                return str(last.get("content", last))
            return str(last)
        return str(response) if response else "Sorry, I didn't get a reply from the agent."
    except Exception:
        return "Sorry, I couldn't parse the response from the server."


def handle_user_message(user_text: str):
    now = datetime.now().strftime("%H:%M")
    st.session_state.messages.append({"role": "user", "content": user_text, "time": now})

    with st.chat_message("user", avatar="🧑"):
        st.write(user_text)
        st.caption(now)

    with st.chat_message("assistant", avatar="🤖"):
        typing_placeholder = st.empty()
        typing_placeholder.markdown("""
        <div class="typing-dots"><span></span><span></span><span></span></div>
        """, unsafe_allow_html=True)

        try:
            resp = requests.post(
                API_URL,
                json={"text": user_text, "thread_id": st.session_state.thread_id},
                timeout=60,
            )
            resp.raise_for_status()
            reply_text = extract_reply(resp.json())
        except requests.exceptions.ConnectionError:
            reply_text = "⚠️ Can't reach the support agent backend. Make sure `agent.py` is running on `localhost:8000`."
        except Exception as e:
            reply_text = f"⚠️ Something went wrong: {e}"

        typing_placeholder.empty()
        st.write(reply_text)
        bot_time = datetime.now().strftime("%H:%M")
        st.caption(bot_time)

    st.session_state.messages.append({"role": "assistant", "content": reply_text, "time": bot_time})


# ------------------------------------------------------------------
# HANDLE SIDEBAR QUICK-ASK
# ------------------------------------------------------------------
if st.session_state.pending_prompt:
    prompt = st.session_state.pending_prompt
    st.session_state.pending_prompt = None
    handle_user_message(prompt)
    st.rerun()

# ------------------------------------------------------------------
# CHAT INPUT
# ------------------------------------------------------------------
user_input = st.chat_input("Type your question here... e.g. 'Where is my order ORD-1042?'")
if user_input:
    handle_user_message(user_input)
    st.rerun()
