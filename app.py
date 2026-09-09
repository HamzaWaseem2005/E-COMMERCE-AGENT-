"""
E-commerce Support Agent — Streamlit UI
Talks to the FastAPI backend (agent.py) running at http://localhost:8000/chat
"""

import streamlit as st
import requests
import time
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
    st.session_state.messages = []
if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())
if "chat_count" not in st.session_state:
    st.session_state.chat_count = 0

# ------------------------------------------------------------------
# CUSTOM CSS — glassmorphism, gradients, animations
# ------------------------------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Poppins', sans-serif;
}

/* Animated gradient background — cover the whole viewport, not just .stApp */
html, body,
.stApp,
[data-testid="stAppViewContainer"],
[data-testid="stMain"] {
    background: linear-gradient(-45deg, #0f0c29, #302b63, #24243e, #1a1a2e);
    background-size: 400% 400%;
    animation: gradientShift 18s ease infinite;
}

/* Kill the white top toolbar/header strip */
[data-testid="stHeader"] {
    background: transparent;
}

/* Kill the white strip behind the bottom chat-input bar */
[data-testid="stBottom"],
[data-testid="stBottomBlockContainer"] {
    background: transparent !important;
}

/* Make the chat input itself sit nicely on the dark background */
[data-testid="stChatInput"] textarea,
[data-testid="stChatInput"] {
    background: rgba(255,255,255,0.06) !important;
    color: #f1f1fb !important;
}
[data-testid="stChatInput"] textarea::placeholder {
    color: #9a9ac0 !important;
}

/* Remove default block container top padding so header sits flush */
.block-container {
    padding-top: 1.2rem;
}

@keyframes gradientShift {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

/* Floating blobs behind content */
.stApp::before {
    content: "";
    position: fixed;
    top: -10%; left: -10%;
    width: 500px; height: 500px;
    background: radial-gradient(circle, rgba(120,119,198,0.35), transparent 70%);
    border-radius: 50%;
    animation: floatBlob 12s ease-in-out infinite;
    z-index: 0;
    pointer-events: none;
}

@keyframes floatBlob {
    0%, 100% { transform: translate(0,0) scale(1); }
    50% { transform: translate(60px, 80px) scale(1.15); }
}

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
@keyframes shine {
    to { background-position: 300% center; }
}
.hero-subtitle {
    text-align: center;
    color: #c9c9e0;
    font-size: 1.05rem;
    font-weight: 300;
    margin-top: 4px;
    animation: fadeInUp 1s ease;
}

@keyframes fadeInUp {
    from { opacity: 0; transform: translateY(15px); }
    to { opacity: 1; transform: translateY(0); }
}

/* Status pill */
.status-pill {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: rgba(0, 245, 212, 0.12);
    border: 1px solid rgba(0, 245, 212, 0.4);
    color: #00f5d4;
    padding: 6px 16px;
    border-radius: 999px;
    font-size: 0.8rem;
    font-weight: 500;
    margin: 10px auto;
    width: fit-content;
}
.pulse-dot {
    width: 8px; height: 8px;
    background: #00f5d4;
    border-radius: 50%;
    box-shadow: 0 0 0 rgba(0,245,212, 0.6);
    animation: pulse 1.8s infinite;
}
@keyframes pulse {
    0% { box-shadow: 0 0 0 0 rgba(0,245,212, 0.6); }
    70% { box-shadow: 0 0 0 10px rgba(0,245,212, 0); }
    100% { box-shadow: 0 0 0 0 rgba(0,245,212, 0); }
}

/* Glass card */
.glass-card {
    background: rgba(255, 255, 255, 0.06);
    border: 1px solid rgba(255, 255, 255, 0.12);
    backdrop-filter: blur(14px);
    border-radius: 18px;
    padding: 18px 20px;
    margin-bottom: 14px;
    animation: fadeInUp 0.5s ease;
    transition: transform 0.25s ease, box-shadow 0.25s ease;
}
.glass-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 10px 30px rgba(155, 93, 229, 0.25);
}

/* Chat bubbles */
.chat-row { display: flex; margin: 10px 0; animation: fadeInUp 0.4s ease; }
.chat-row.user { justify-content: flex-end; }
.chat-row.bot { justify-content: flex-start; }

.bubble {
    max-width: 72%;
    padding: 12px 18px;
    border-radius: 18px;
    line-height: 1.5;
    font-size: 0.95rem;
    box-shadow: 0 4px 18px rgba(0,0,0,0.25);
}
.bubble.user {
    background: linear-gradient(135deg, #7b2ff7, #f107a3);
    color: white;
    border-bottom-right-radius: 4px;
}
.bubble.bot {
    background: rgba(255,255,255,0.08);
    border: 1px solid rgba(255,255,255,0.14);
    color: #eaeaf5;
    border-bottom-left-radius: 4px;
}
.bubble-meta {
    font-size: 0.68rem;
    opacity: 0.55;
    margin-top: 6px;
}

/* Typing indicator */
.typing-dots span {
    display: inline-block;
    width: 6px; height: 6px;
    margin-right: 3px;
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

/* Metric cards */
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

/* Quick action buttons */
div[data-testid="stButton"] button {
    background: linear-gradient(135deg, rgba(123,47,247,0.25), rgba(241,7,163,0.25));
    border: 1px solid rgba(255,255,255,0.18);
    color: #f1f1fb;
    border-radius: 12px;
    padding: 8px 14px;
    font-weight: 500;
    transition: all 0.25s ease;
}
div[data-testid="stButton"] button:hover {
    border-color: #00f5d4;
    box-shadow: 0 0 16px rgba(0,245,212,0.4);
    transform: translateY(-2px);
    color: #00f5d4;
}

/* Chat input */
div[data-testid="stChatInput"] {
    background: rgba(255,255,255,0.04);
    border-radius: 14px;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #14142b, #1c1c3a);
    border-right: 1px solid rgba(255,255,255,0.08);
}

/* Hide default footer/menu clutter */
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
        st.markdown(f"""
        <div class="metric-box">
            <div class="metric-num">{st.session_state.chat_count}</div>
            <div class="metric-label">Messages</div>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="metric-box">
            <div class="metric-num">24/7</div>
            <div class="metric-label">Availability</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("<p style='color:#c9c9e0; font-size:0.85rem; font-weight:600;'>⚡ Quick Asks</p>", unsafe_allow_html=True)

    quick_prompts = [
        "📦 Track my last order",
        "🛒 What products do you sell?",
        "↩️ What's your return policy?",
        "🚚 Delivery time estimate",
    ]
    for q in quick_prompts:
        if st.button(q, use_container_width=True, key=q):
            st.session_state.pending_prompt = q.split(" ", 1)[1]

    st.markdown("---")
    if st.button("🗑️ Clear conversation", use_container_width=True):
        st.session_state.messages = []
        st.session_state.thread_id = str(uuid.uuid4())
        st.session_state.chat_count = 0
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

st.write("")

# ------------------------------------------------------------------
# CHAT HISTORY
# ------------------------------------------------------------------
chat_container = st.container()

def render_message(role, content, ts):
    css_role = "user" if role == "user" else "bot"
    avatar = "🧑" if role == "user" else "🤖"
    st.markdown(f"""
    <div class="chat-row {css_role}">
        <div class="bubble {css_role}">
            {content}
            <div class="bubble-meta">{avatar} {ts}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with chat_container:
    if not st.session_state.messages:
        st.markdown("""
        <div class="glass-card" style="text-align:center;">
            <h3 style="color:#f1f1fb;">👋 Welcome!</h3>
            <p style="color:#b8b8d0;">Ask me about your order status, delivery dates, tracking numbers,
            or anything about our products. Try one of the quick asks in the sidebar to get started.</p>
        </div>
        """, unsafe_allow_html=True)

    for msg in st.session_state.messages:
        render_message(msg["role"], msg["content"], msg["time"])

# ------------------------------------------------------------------
# HELPER: extract plain text reply from backend response
# ------------------------------------------------------------------
def extract_reply(result: dict) -> str:
    try:
        response = result.get("response", {})
        messages = response.get("messages", [])
        if messages:
            last = messages[-1]
            if isinstance(last, dict):
                return last.get("content", str(last))
            return str(last)
        return str(response)
    except Exception:
        return "Sorry, I couldn't parse the response from the server."

def send_message(user_text: str):
    now = datetime.now().strftime("%H:%M")
    st.session_state.messages.append({"role": "user", "content": user_text, "time": now})
    st.session_state.chat_count += 1

    with chat_container:
        render_message("user", user_text, now)
        typing_placeholder = st.empty()
        typing_placeholder.markdown("""
        <div class="chat-row bot">
            <div class="bubble bot typing-dots">
                <span></span><span></span><span></span>
            </div>
        </div>
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
        bot_time = datetime.now().strftime("%H:%M")
        render_message("bot", reply_text, bot_time)

    st.session_state.messages.append({"role": "assistant", "content": reply_text, "time": bot_time})

# ------------------------------------------------------------------
# HANDLE PENDING (sidebar quick-ask) PROMPT
# ------------------------------------------------------------------
if "pending_prompt" in st.session_state:
    prompt = st.session_state.pop("pending_prompt")
    send_message(prompt)
    st.rerun()

# ------------------------------------------------------------------
# CHAT INPUT
# ------------------------------------------------------------------
user_input = st.chat_input("Type your question here... e.g. 'Where is my order ORD-1042?'")
if user_input:
    send_message(user_input)
    st.rerun()