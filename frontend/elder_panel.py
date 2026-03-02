import streamlit as st
import requests
import base64
from datetime import datetime

API_BASE_URL = "http://api:8000/api"

st.set_page_config(
    page_title="SMARAN — My Assistant",
    layout="centered",
    page_icon="🏥"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@300;400;500;600;700&family=Playfair+Display:wght@600;700&display=swap');

:root {
    --white:      #ffffff;
    --bg:         #f5f7fa;
    --border:     #dde3ec;
    --border-mid: #b8c4d4;
    --navy:       #0b2545;
    --navy-mid:   #1a3a6e;
    --blue:       #1557c0;
    --blue-lt:    #e8eef9;
    --teal:       #0097a7;
    --teal-lt:    #e0f5f7;
    --green:      #1b8a5a;
    --green-lt:   #e6f5ef;
    --amber:      #c47a00;
    --amber-lt:   #fff3d6;
    --red:        #c0392b;
    --red-lt:     #fdecea;
    --text:       #0b1e35;
    --text-mid:   #3d5166;
    --text-soft:  #7a93aa;
    --shadow-sm:  0 1px 4px rgba(11,37,69,0.07);
    --shadow-md:  0 4px 16px rgba(11,37,69,0.10);
    --shadow-lg:  0 12px 40px rgba(11,37,69,0.14);
    --r: 14px;
    --rl: 20px;
}

#MainMenu {visibility:hidden;}
footer {visibility:hidden;}
header {visibility:hidden;}

html, body, .stApp {
    background: var(--bg) !important;
    color: var(--text) !important;
    font-family: 'IBM Plex Sans', sans-serif !important;
}

::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: var(--border-mid); border-radius: 3px; }

.main .block-container {
    max-width: 720px !important;
    padding: 2rem 1.5rem !important;
    animation: fadein 0.4s ease;
}
@keyframes fadein { from{opacity:0;transform:translateY(8px)} to{opacity:1;transform:translateY(0)} }

/* ── BUTTONS ── */
.stButton > button {
    background: var(--blue) !important;
    color: #fff !important;
    border: none !important;
    border-radius: var(--r) !important;
    font-family: 'IBM Plex Sans', sans-serif !important;
    font-size: 1.1rem !important;
    font-weight: 600 !important;
    padding: 0.75rem 1.2rem !important;
    width: 100% !important;
    transition: all 0.2s ease !important;
    box-shadow: var(--shadow-sm) !important;
    letter-spacing: 0.01em !important;
}
.stButton > button:hover {
    background: var(--navy-mid) !important;
    box-shadow: var(--shadow-md) !important;
    transform: translateY(-1px) !important;
}

/* Emergency button override */
.emergency-btn .stButton > button {
    background: var(--red) !important;
    font-size: 1.25rem !important;
    letter-spacing: 0.02em !important;
    padding: 1rem 1.5rem !important;
    box-shadow: 0 4px 16px rgba(192,57,43,0.25) !important;
}
.emergency-btn .stButton > button:hover {
    background: #a93226 !important;
    box-shadow: 0 6px 20px rgba(192,57,43,0.35) !important;
}

/* Sign out */
.signout-btn .stButton > button {
    background: transparent !important;
    color: var(--text-soft) !important;
    border: 1px solid var(--border) !important;
    font-size: 0.88rem !important;
    width: auto !important;
    padding: 0.4rem 1rem !important;
    box-shadow: none !important;
}
.signout-btn .stButton > button:hover {
    background: var(--red-lt) !important;
    color: var(--red) !important;
    border-color: #f0a8a1 !important;
    transform: none !important;
}

/* ── FORM INPUT ── */
.stTextInput > div > div > input {
    background: var(--white) !important;
    border: 1.5px solid var(--border) !important;
    border-radius: var(--r) !important;
    color: var(--text) !important;
    font-family: 'IBM Plex Sans', sans-serif !important;
    font-size: 1.15rem !important;
    padding: 0.8rem 1rem !important;
    transition: all 0.2s ease !important;
}
.stTextInput > div > div > input:focus {
    border-color: var(--blue) !important;
    box-shadow: 0 0 0 3px rgba(21,87,192,0.1) !important;
    outline: none !important;
}
.stTextInput > div > div > input::placeholder { color: var(--text-soft) !important; }
.stTextInput label {
    color: var(--text-mid) !important; font-size: 0.78rem !important;
    font-weight: 600 !important; text-transform: uppercase !important;
    letter-spacing: 0.08em !important;
}

/* ── ALERTS ── */
.stSuccess { background:var(--green-lt) !important; border:1px solid #a3d9bd !important; border-radius:var(--r) !important; color:var(--green) !important; }
.stError   { background:var(--red-lt) !important;   border:1px solid #f0a8a1 !important; border-radius:var(--r) !important; color:var(--red) !important; }
.stInfo    { background:var(--blue-lt) !important;   border:1px solid #b0c8f0 !important; border-radius:var(--r) !important; color:var(--navy-mid) !important; }
.stWarning { background:var(--amber-lt) !important;  border:1px solid #f0d080 !important; border-radius:var(--r) !important; }
.stSpinner > div { border-top-color: var(--blue) !important; }

/* ── CUSTOM COMPONENTS ── */

.header-card {
    background: var(--navy);
    border-radius: var(--rl);
    padding: 1.8rem 2rem;
    margin-bottom: 1.5rem;
    text-align: center;
    box-shadow: var(--shadow-md);
}
.header-card .greeting {
    font-family: 'Playfair Display', serif;
    font-size: 2rem;
    font-weight: 700;
    color: #fff;
    margin-bottom: 0.3rem;
}
.header-card .datetime {
    font-size: 0.88rem;
    color: rgba(255,255,255,0.45);
    letter-spacing: 0.04em;
}
.header-card .mood-line {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    background: rgba(255,255,255,0.08);
    border: 1px solid rgba(255,255,255,0.12);
    border-radius: 20px;
    padding: 0.3rem 0.9rem;
    font-size: 0.82rem;
    color: rgba(255,255,255,0.65);
    margin-top: 0.8rem;
}

.quick-label {
    font-size: 0.72rem;
    text-transform: uppercase;
    letter-spacing: 0.14em;
    color: var(--text-soft);
    font-weight: 700;
    margin-bottom: 0.6rem;
}

.chat-wrap {
    margin: 1.2rem 0;
}

.bubble-user {
    background: var(--white);
    border: 1px solid var(--border);
    border-radius: var(--rl) var(--rl) 4px var(--rl);
    padding: 1rem 1.2rem;
    margin-bottom: 0.8rem;
    font-size: 1.15rem;
    color: var(--text);
    line-height: 1.5;
    box-shadow: var(--shadow-sm);
    text-align: right;
}
.bubble-user .who {
    font-size: 0.7rem;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    color: var(--text-soft);
    font-weight: 700;
    margin-bottom: 0.3rem;
}
.bubble-user.emergency {
    background: var(--red-lt);
    border-color: #f0a8a1;
    border-left: 4px solid var(--red);
}

.bubble-bot {
    background: var(--navy);
    border-radius: 4px var(--rl) var(--rl) var(--rl);
    padding: 1rem 1.2rem;
    margin-bottom: 0.5rem;
    font-size: 1.15rem;
    color: #fff;
    line-height: 1.6;
    box-shadow: var(--shadow-md);
}
.bubble-bot .who {
    font-size: 0.7rem;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    color: rgba(255,255,255,0.4);
    font-weight: 700;
    margin-bottom: 0.4rem;
}

.mood-tag {
    display: inline-flex;
    align-items: center;
    gap: 0.3rem;
    background: var(--blue-lt);
    border: 1px solid #c0d4f5;
    border-radius: 20px;
    padding: 0.22rem 0.75rem;
    font-size: 0.75rem;
    color: var(--blue);
    font-weight: 600;
    margin-bottom: 1rem;
}

.activity-card {
    background: var(--teal-lt);
    border: 1px solid #b0e0e6;
    border-left: 4px solid var(--teal);
    border-radius: 0 var(--r) var(--r) 0;
    padding: 0.8rem 1rem;
    font-size: 0.9rem;
    color: #005f6b;
    margin-bottom: 1rem;
}

.divider {
    height: 1px;
    background: var(--border);
    margin: 1.5rem 0;
}

/* Login */
.login-brand { text-align: center; margin-bottom: 2rem; }
.login-icon {
    width: 80px; height: 80px; border-radius: 20px;
    background: linear-gradient(135deg, var(--navy), var(--navy-mid));
    display: flex; align-items: center; justify-content: center;
    font-size: 36px; margin: 0 auto 1rem;
    box-shadow: 0 8px 24px rgba(11,37,69,0.22);
}
.login-brand h1 {
    font-family: 'Playfair Display', serif !important;
    font-size: 2.2rem !important; font-weight: 700 !important;
    color: var(--navy) !important; letter-spacing: 0.04em; margin: 0 !important;
}
.login-brand p {
    font-size: 1rem !important; color: var(--text-soft) !important;
    margin-top: 0.35rem;
}
.login-card {
    background: var(--white);
    border: 1px solid var(--border);
    border-radius: var(--rl);
    padding: 2.5rem 2rem;
    box-shadow: var(--shadow-lg);
    animation: fadein 0.5s ease;
}
.login-divider { height: 1px; background: var(--border); margin: 1.5rem 0; }
.login-footer { text-align: center; margin-top: 1.2rem; font-size: 0.72rem; color: var(--text-soft); }
</style>
""", unsafe_allow_html=True)

# ── Session state ──────────────────────────────────────────────────────────────
if "token" not in st.session_state:
    st.session_state.token = None
if "elder_id" not in st.session_state:
    st.session_state.elder_id = "elder_123"
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

MOOD_EMOJI = {
    "happy": "😊", "sad": "😢", "anxious": "😰",
    "confused": "😕", "neutral": "😐", "angry": "😠",
    "lonely": "🥺", "excited": "🤩"
}

# ── Helpers ───────────────────────────────────────────────────────────────────
def send_message(message, emergency=False):
    headers = {"Authorization": f"Bearer {st.session_state.token}"}
    payload = {
        "elder_id": st.session_state.elder_id,
        "message": ("EMERGENCY: Elder needs immediate assistance. " + message) if emergency else message,
        "hour_of_day": datetime.now().hour,
        "return_audio": True
    }
    st.session_state.chat_history.append({"role": "user", "text": message, "emergency": emergency})

    with st.spinner("SMARAN is thinking..."):
        try:
            res = requests.post(f"{API_BASE_URL}/chat/", json=payload, headers=headers, timeout=30)
            if res.status_code == 200:
                st.session_state.chat_history.append({
                    "role": "bot",
                    "text": res.headers.get("X-Reply-Text", "I have processed your message."),
                    "audio": res.content,
                    "mood": res.headers.get("X-Detected-Mood", "neutral"),
                    "trigger": res.headers.get("X-MoodMitra-Triggered", "")
                })
                st.rerun()
            elif res.status_code == 401:
                st.session_state.token = None
                st.error("Your session has expired. Please sign in again.")
                st.rerun()
            else:
                st.error("Sorry, I couldn't process that. Please try again.")
        except Exception:
            st.error("⚠️ Connection lost. Please check your internet and try again.")

# ── LOGIN ─────────────────────────────────────────────────────────────────────
def login():
    st.markdown("""
    <div class="login-brand">
        <div class="login-icon">🏥</div>
        <h1>SMARAN</h1>
        <p>Your Memory Companion</p>
    </div>
    <div class="login-divider"></div>
    """, unsafe_allow_html=True)

    with st.form("login_form"):
        username = st.text_input("Your Name / ID", value="elder_123", placeholder="e.g. elder_123")
        password = st.text_input("Your Password", type="password", value="password123", placeholder="••••••••")
        st.markdown("<br>", unsafe_allow_html=True)
        submit = st.form_submit_button("✓  Sign In", use_container_width=True)

    if submit:
        with st.spinner("Signing you in..."):
            try:
                res = requests.post(f"{API_BASE_URL}/auth/login", data={"username": username, "password": password}, timeout=10)
                if res.status_code == 200:
                    st.session_state.token = res.json()["access_token"]
                    st.session_state.elder_id = username
                    st.rerun()
                else:
                    st.error("Incorrect details. Please try again or ask your caregiver for help.")
            except Exception:
                st.error("⚠️ System is offline right now. Please try again shortly.")

    st.markdown('<div class="login-footer">SMARAN v1.0 · Your personal health companion</div>', unsafe_allow_html=True)

# ── MAIN INTERFACE ────────────────────────────────────────────────────────────
def main_interface():
    # Detect current mood
    bot_msgs = [m for m in st.session_state.chat_history if m.get("role") == "bot"]
    current_mood = bot_msgs[-1].get("mood", "neutral") if bot_msgs else "neutral"
    mood_emoji = MOOD_EMOJI.get(current_mood, "😐")
    name_display = st.session_state.elder_id.replace("_", " ").title()

    # ── Header ──
    st.markdown(f"""
    <div class="header-card">
        <div class="greeting">Hello, {name_display}! {mood_emoji}</div>
        <div class="datetime">{datetime.now().strftime('%A, %d %B %Y — %I:%M %p')}</div>
        <div class="mood-line">Current mood detected: <strong>{current_mood.title()}</strong></div>
    </div>
    """, unsafe_allow_html=True)

    # ── Quick action buttons ──
    st.markdown('<div class="quick-label">Quick Actions</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("💊  My Medicines", use_container_width=True):
            send_message("What medicines do I need to take?")
    with c2:
        if st.button("📅  My Appointments", use_container_width=True):
            send_message("What appointments do I have coming up?")
    with c3:
        if st.button("🧠  What do you remember?", use_container_width=True):
            send_message("What do you remember about me?")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Emergency button ──
    st.markdown('<div class="emergency-btn">', unsafe_allow_html=True)
    if st.button("🚨  CALL CAREGIVER — EMERGENCY", use_container_width=True):
        send_message("I am having an emergency and need immediate help.", emergency=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    # ── Chat history ──
    if st.session_state.chat_history:
        st.markdown('<div class="chat-wrap">', unsafe_allow_html=True)
        for msg in st.session_state.chat_history[-10:]:
            if msg["role"] == "user":
                em_class = " emergency" if msg.get("emergency") else ""
                prefix = "🚨 Emergency — " if msg.get("emergency") else ""
                st.markdown(f"""
                <div class="bubble-user{em_class}">
                    <div class="who">You</div>
                    {prefix}{msg['text']}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="bubble-bot">
                    <div class="who">🏥 SMARAN</div>
                    {msg['text']}
                </div>
                """, unsafe_allow_html=True)

                # Audio
                if msg.get("audio") and len(msg["audio"]) > 100:
                    b64 = base64.b64encode(msg["audio"]).decode()
                    st.markdown(
                        f'<audio controls style="width:100%;margin:0.4rem 0 0.6rem;border-radius:8px;">'
                        f'<source src="data:audio/wav;base64,{b64}" type="audio/wav"></audio>',
                        unsafe_allow_html=True
                    )

                # Mood tag
                mood = msg.get("mood", "neutral")
                st.markdown(
                    f'<div class="mood-tag">{MOOD_EMOJI.get(mood,"😐")} Mood: {mood.title()}</div>',
                    unsafe_allow_html=True
                )

                # Activity trigger
                if msg.get("trigger"):
                    st.markdown(
                        '<div class="activity-card">💡 A helpful activity has been recommended for you by your caregiver.</div>',
                        unsafe_allow_html=True
                    )

        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    # ── Text input ──
    with st.form("chat_form", clear_on_submit=True):
        user_input = st.text_input(
            "Your Message",
            placeholder="Type here and press Send... or ask me anything!",
            label_visibility="collapsed"
        )
        submitted = st.form_submit_button("Send  →", use_container_width=True)
        if submitted and user_input.strip():
            send_message(user_input.strip())

    # ── Sign out ──
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="signout-btn">', unsafe_allow_html=True)
    if st.button("Sign Out", use_container_width=False):
        st.session_state.token = None
        st.session_state.chat_history = []
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# ── Entry ─────────────────────────────────────────────────────────────────────
if st.session_state.token is None:
    login()
else:
    main_interface()