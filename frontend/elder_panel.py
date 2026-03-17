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
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600;700&family=Playfair+Display:wght@600;700&display=swap');

:root {
    --white:      #ffffff;
    --bg:         #fffdf7; /* Warm off-white */
    --border:     #e2d5c3;
    --border-mid: #cbb497;
    --navy:       #1b3a57;
    --blue:       #2a6bb2;
    --blue-lt:    #eef4fa;
    --green:      #2b8a3e;
    --green-lt:   #eaf5ea;
    --amber:      #d97706;
    --amber-lt:   #fef3c7;
    --red:        #dc2626;
    --red-lt:     #fee2e2;
    --text:       #111827; /* Dark text for high contrast */
    --text-mid:   #374151;
    --text-soft:  #4b5563;
    --shadow-sm:  0 2px 8px rgba(0,0,0,0.08);
    --shadow-md:  0 8px 24px rgba(0,0,0,0.12);
    --r: 16px;
    --rl: 24px;
}

#MainMenu {visibility:hidden;}
footer {visibility:hidden;}
header {visibility:hidden;}

html, body, .stApp {
    background: var(--bg) !important;
    color: var(--text) !important;
    font-family: 'IBM Plex Sans', sans-serif !important;
    font-size: 1.4rem !important; /* Minimum font size everywhere */
}

/* Ensure paragraph and general text also inherit larger sizes */
p, div, span, label {
    font-size: 1.4rem !important;
    line-height: 1.6 !important;
}
.stMarkdown p {
    font-size: 1.4rem !important;
}

::-webkit-scrollbar { width: 8px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: var(--border-mid); border-radius: 4px; }

.main .block-container {
    max-width: 800px !important;
    padding: 2rem 1.5rem !important;
    animation: fadein 0.4s ease;
}
@keyframes fadein { from{opacity:0;transform:translateY(8px)} to{opacity:1;transform:translateY(0)} }

/* ── BUTTONS ── */
.stButton > button, button[kind="primary"], button[kind="secondary"] {
    background: var(--blue) !important;
    color: #fff !important;
    border: none !important;
    border-radius: var(--r) !important;
    font-family: 'IBM Plex Sans', sans-serif !important;
    font-size: 1.5rem !important;
    font-weight: 600 !important;
    padding: 1rem 1.2rem !important;
    width: 100% !important;
    min-height: 60px !important;
    transition: all 0.2s ease !important;
    box-shadow: var(--shadow-sm) !important;
    letter-spacing: 0.01em !important;
}
.stButton > button:hover, button[kind="primary"]:hover {
    background: #1e528e !important;
    box-shadow: var(--shadow-md) !important;
    transform: translateY(-2px) !important;
}

/* Emergency button override */
.emergency-btn button {
    background: var(--red) !important;
    font-size: 1.6rem !important;
    font-weight: 700 !important;
    padding: 1.2rem !.2rem !important;
    box-shadow: 0 4px 16px rgba(220,38,38,0.3) !important;
}
.emergency-btn button:hover {
    background: #b91c1c !important;
    box-shadow: 0 6px 20px rgba(220,38,38,0.4) !important;
}

/* Checkbox / Expander */
.stExpander {
    border: 2px solid var(--border) !important;
    border-radius: var(--r) !important;
    background: var(--white) !important;
}
.stExpander summary {
    font-size: 1.5rem !important;
    font-weight: 600 !important;
    color: var(--navy) !important;
    padding: 1rem !important;
}

/* ── FORM INPUT ── */
.stTextInput > div > div > input {
    background: var(--white) !important;
    border: 2px solid var(--border-mid) !important;
    border-radius: var(--r) !important;
    color: var(--text) !important;
    font-family: 'IBM Plex Sans', sans-serif !important;
    font-size: 1.5rem !important;
    padding: 1rem 1.2rem !important;
    transition: all 0.2s ease !important;
    min-height: 60px !important;
}
.stTextInput > div > div > input:focus {
    border-color: var(--blue) !important;
    box-shadow: 0 0 0 4px rgba(42,107,178,0.15) !important;
    outline: none !important;
}
.stTextInput > div > div > input::placeholder { color: var(--text-soft) !important; font-size: 1.4rem !important; }
.stTextInput label {
    color: var(--text) !important; 
    font-size: 1.3rem !important;
    font-weight: 600 !important; 
    margin-bottom: 0.3rem !important;
}

/* ── ALERTS ── */
.stSuccess { background:var(--green-lt) !important; border:2px solid var(--green) !important; border-radius:var(--r) !important; color:var(--text) !important; padding: 1rem !important; }
.stError   { background:var(--red-lt) !important;   border:2px solid var(--red) !important; border-radius:var(--r) !important; color:var(--text) !important; padding: 1rem !important; }
.stInfo    { background:var(--blue-lt) !important;   border:2px solid var(--blue) !important; border-radius:var(--r) !important; color:var(--text) !important; padding: 1rem !important; }
.stWarning { background:var(--amber-lt) !important;  border:2px solid var(--amber) !important; border-radius:var(--r) !important; color:var(--text) !important; padding: 1rem !important; }

/* ── CUSTOM COMPONENTS ── */

.header-card {
    background: var(--navy);
    border-radius: var(--rl);
    padding: 2rem 2.5rem;
    margin-bottom: 1.5rem;
    text-align: center;
    box-shadow: var(--shadow-md);
    color: white !important;
}
.header-card .greeting {
    font-family: 'Playfair Display', serif;
    font-size: 2.2rem !important;
    font-weight: 700;
    margin-bottom: 0.5rem;
}
.header-card .datetime {
    font-size: 1.4rem !important;
    color: #e2e8f0 !important;
}
.header-card .mood-line {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    background: rgba(255,255,255,0.15);
    border: 2px solid rgba(255,255,255,0.25);
    border-radius: 20px;
    padding: 0.5rem 1rem;
    font-size: 1.4rem !important;
    color: #fff !important;
    font-weight: 500;
    margin-top: 1rem;
}

.quick-label {
    font-size: 1.5rem !important;
    color: var(--text);
    font-weight: 600;
    margin-bottom: 1rem;
    text-align: center;
}

.chat-wrap {
    margin: 1.5rem 0;
}

.bubble-user {
    background: var(--white);
    border: 2px solid var(--border-mid);
    border-radius: var(--rl) var(--rl) 4px var(--rl);
    padding: 1.2rem 1.5rem;
    margin-bottom: 1rem;
    font-size: 1.5rem !important;
    color: var(--text) !important;
    line-height: 1.6 !important;
    box-shadow: var(--shadow-sm);
    text-align: right;
    margin-left: 2rem;
}
.bubble-user.emergency {
    background: var(--red-lt);
    border-color: var(--red);
    border-left: 6px solid var(--red);
}

.bubble-bot {
    background: var(--blue-lt);
    border: 2px solid #aecae6;
    border-radius: 4px var(--rl) var(--rl) var(--rl);
    padding: 1.2rem 1.5rem;
    margin-bottom: 0.8rem;
    font-size: 1.5rem !important;
    color: var(--text) !important;
    line-height: 1.6 !important;
    box-shadow: var(--shadow-md);
    margin-right: 2rem;
}
.bubble-bot .who {
    font-size: 1.3rem !important;
    color: var(--navy);
    font-weight: 700;
    margin-bottom: 0.5rem;
}

.mood-tag {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    background: var(--white);
    border: 2px solid #aecae6;
    border-radius: 20px;
    padding: 0.4rem 0.8rem;
    font-size: 1.3rem !important;
    color: var(--blue);
    font-weight: 600;
    margin-bottom: 1.5rem;
}

.activity-card {
    background: var(--green-lt);
    border: 2px solid var(--green);
    border-left: 6px solid var(--green);
    border-radius: var(--r);
    padding: 1rem 1.2rem;
    font-size: 1.4rem !important;
    color: var(--text) !important;
    margin-bottom: 1.5rem;
}

.divider {
    height: 2px;
    background: var(--border-mid);
    margin: 2rem 0;
}

/* Login */
.login-brand { text-align: center; margin-bottom: 2rem; }
.login-icon {
    width: 100px; height: 100px; border-radius: 24px;
    background: var(--blue);
    color: white;
    display: flex; align-items: center; justify-content: center;
    font-size: 48px; margin: 0 auto 1.5rem;
    box-shadow: var(--shadow-md);
}
.login-brand h1 {
    font-family: 'Playfair Display', serif !important;
    font-size: 3rem !important; font-weight: 700 !important;
    color: var(--navy) !important; margin: 0 !important;
}
.login-brand p {
    font-size: 1.6rem !important; color: var(--text-soft) !important;
    margin-top: 0.5rem;
    font-weight: 500;
}
.login-card {
    background: var(--white);
    border: 2px solid var(--border);
    border-radius: var(--rl);
    padding: 3rem 2.5rem;
    box-shadow: var(--shadow-lg);
    animation: fadein 0.5s ease;
}
.login-divider { height: 2px; background: var(--border-mid); margin: 2rem 0; }
</style>
""", unsafe_allow_html=True)

# ── Session state ──────────────────────────────────────────────────────────────
if "token" not in st.session_state:
    st.session_state.token = None
if "elder_id" not in st.session_state:
    st.session_state.elder_id = None
if "full_name" not in st.session_state:
    st.session_state.full_name = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "session_expired" not in st.session_state:
    st.session_state.session_expired = False

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
                st.session_state.session_expired = True
                st.rerun()
            else:
                st.error("Sorry, I couldn't process that. Please try again.")
        except Exception:
            st.error("⚠️ Connection lost. Please check your internet connection and try again.")

# ── LOGIN ─────────────────────────────────────────────────────────────────────
def login():
    if st.session_state.session_expired:
        st.error("Session expired. Please sign in again.")
        st.session_state.session_expired = False

    st.markdown("""
    <div class="login-brand">
        <div class="login-icon">🧠</div>
        <h1>SMARAN</h1>
        <p>Your Memory Companion</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="login-card">', unsafe_allow_html=True)
    with st.form("login_form"):
        username = st.text_input("Your Name (Username)", value="elder_123")
        password = st.text_input("Password", type="password", value="password123")
        st.markdown("<br>", unsafe_allow_html=True)
        submit = st.form_submit_button("Sign In")

    if submit:
        with st.spinner("Signing you in..."):
            try:
                res = requests.post(f"{API_BASE_URL}/auth/login", data={"username": username, "password": password}, timeout=10)
                if res.status_code == 200:
                    data = res.json()
                    st.session_state.token = data["access_token"]
                    st.session_state.elder_id = username
                    
                    # Fetch user full name safely
                    try:
                        me_res = requests.get(f"{API_BASE_URL}/auth/me", headers={"Authorization": f"Bearer {st.session_state.token}"})
                        if me_res.status_code == 200:
                            st.session_state.full_name = me_res.json().get("full_name", username)
                        else:
                            st.session_state.full_name = username
                    except:
                        st.session_state.full_name = username
                        
                    st.rerun()
                elif res.status_code == 401:
                    st.error("Incorrect details. Please try again or ask your caregiver.")
                else:
                    st.error("System error during sign in.")
            except Exception:
                st.error("System is offline. Please try again shortly.")
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="login-divider"></div>', unsafe_allow_html=True)
    
    with st.expander("New here? Create your account"):
        with st.form("register_form"):
            reg_full_name = st.text_input("Your Full Name")
            reg_username = st.text_input("Choose a Username", help="e.g. ramesh72, use your name")
            reg_email = st.text_input("Email Address")
            reg_password = st.text_input("Create Password", type="password", help="At least 8 characters with a number")
            reg_password_confirm = st.text_input("Confirm Password", type="password")
            st.markdown("<br>", unsafe_allow_html=True)
            reg_submit = st.form_submit_button("Create My Account")
            
        if reg_submit:
            if reg_password != reg_password_confirm:
                st.error("Passwords do not match")
            elif len(reg_password) < 8 or not any(char.isdigit() for char in reg_password):
                st.error("Password needs at least 8 characters and one number")
            else:
                with st.spinner("Creating account..."):
                    try:
                        payload = {
                            "username": reg_username,
                            "email": reg_email,
                            "password": reg_password,
                            "full_name": reg_full_name,
                            "role": "ELDER"
                        }
                        reg_res = requests.post(f"{API_BASE_URL}/auth/register", json=payload)
                        if reg_res.status_code == 200:
                            st.success("✅ Account created! You can now sign in above.")
                        elif reg_res.status_code == 409:
                            st.error(str(reg_res.json().get("detail", "This username or email is already taken.")))
                        else:
                            st.error("Registration failed. Please try again.")
                    except requests.exceptions.RequestException:
                        st.error("System is offline. Please try again shortly.")

# ── MAIN INTERFACE ────────────────────────────────────────────────────────────
def main_interface():
    # Detect current mood
    bot_msgs = [m for m in st.session_state.chat_history if m.get("role") == "bot"]
    current_mood = bot_msgs[-1].get("mood", "neutral") if bot_msgs else "neutral"
    mood_emoji = MOOD_EMOJI.get(current_mood, "😐")
    name_display = st.session_state.full_name or st.session_state.elder_id.replace("_", " ").title()

    if not st.session_state.chat_history:
        # First time experience
        welcome_msg = f"👋 Welcome to SMARAN, {name_display}! I'm here to help you remember. You can ask me about your medicines, appointments, or just have a chat. How are you feeling today?"
        st.session_state.chat_history.append({
            "role": "bot", 
            "text": welcome_msg, 
            "mood": "happy"
        })
        current_mood = "happy"
        mood_emoji = MOOD_EMOJI.get("happy")

    # ── Header ──
    hour = datetime.now().hour
    if hour < 12: greet = "Good Morning"
    elif hour < 17: greet = "Good Afternoon"
    else: greet = "Good Evening"
    
    st.markdown(f"""
    <div class="header-card">
        <div class="greeting">{greet}, {name_display}! 🌤️</div>
        <div class="datetime">{datetime.now().strftime('%A, %d %B %Y — %I:%M %p')}</div>
        <div class="mood-line">Your current mood: <strong>{current_mood.title()} {mood_emoji}</strong></div>
    </div>
    """, unsafe_allow_html=True)

    # ── Quick action buttons ──
    st.markdown('<div class="quick-label">How are you feeling right now?</div>', unsafe_allow_html=True)
    m1, m2, m3, m4 = st.columns(4)
    if m1.button("😊 Happy", use_container_width=True): send_message("I am feeling happy.")
    if m2.button("😐 Okay", use_container_width=True): send_message("I am feeling okay.")
    if m3.button("😢 Sad", use_container_width=True): send_message("I am feeling sad.")
    if m4.button("😰 Worried", use_container_width=True): send_message("I am feeling worried.")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    if not st.session_state.chat_history or len(st.session_state.chat_history) == 1:
        st.markdown('<div class="quick-label">Try asking me...</div>', unsafe_allow_html=True)
        s1, s2 = st.columns(2)
        if s1.button("💊 What medicines do I take?", use_container_width=True): send_message("What medicines do I take?")
        if s2.button("📅 What appointments do I have?", use_container_width=True): send_message("What appointments do I have?")
        s3, s4 = st.columns(2)
        if s3.button("🌸 Tell me something nice", use_container_width=True): send_message("Tell me something nice")
        if s4.button("🆘 I need help", use_container_width=True): send_message("I need help")
    else:
        st.markdown('<div class="quick-label">Suggestions to ask me</div>', unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        with c1:
            if st.button("💊 My Medicines", use_container_width=True):
                send_message("What medicines do I need to take?")
        with c2:
            if st.button("📅 My Appointments", use_container_width=True):
                send_message("What appointments do I have coming up?")
        with c3:
            if st.button("🧠 Remind Me...", use_container_width=True):
                send_message("What do you remember about me?")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Emergency button ──
    st.markdown('<div class="emergency-btn">', unsafe_allow_html=True)
    if st.button("🚨 CALL CAREGIVER — EMERGENCY", use_container_width=True):
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
                    <div class="who" style="font-size: 1.2rem; color: var(--text-soft); margin-bottom: 0.5rem; font-weight: bold;">You</div>
                    {prefix}{msg['text']}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="bubble-bot">
                    <div class="who">🧠 SMARAN</div>
                    {msg['text']}
                </div>
                """, unsafe_allow_html=True)

                # Audio
                if msg.get("audio") and len(msg["audio"]) > 100:
                    b64 = base64.b64encode(msg["audio"]).decode()
                    st.markdown(
                        f'<audio controls autoplay style="width:100%; height: 50px; margin:0.5rem 0 1rem; border-radius:30px; border: 2px solid #aecae6; outline: none;">'
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
                        '<div class="activity-card">💡 A helpful activity has been recommended for you.</div>',
                        unsafe_allow_html=True
                    )

        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    # ── Text input ──
    with st.form("chat_form", clear_on_submit=True):
        user_input = st.text_input(
            "Your Message",
            placeholder="Type your message here...",
            label_visibility="collapsed"
        )
        submitted = st.form_submit_button("Send Your Message")
        if submitted and user_input.strip():
            send_message(user_input.strip())

    # ── Sign out ──
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Sign Out completely"):
        st.session_state.token = None
        st.session_state.chat_history = []
        st.rerun()

# ── Entry ─────────────────────────────────────────────────────────────────────
if st.session_state.token is None:
    login()
else:
    main_interface()