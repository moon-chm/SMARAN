import streamlit as st
import streamlit.components.v1 as components
import requests
import json
import time

API_BASE_URL = "http://api:8000"

st.set_page_config(
    page_title="SMARAN — Caregiver Portal",
    layout="wide",
    page_icon="🏥",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@300;400;500;600;700&family=IBM+Plex+Mono:wght@400;500&family=Playfair+Display:wght@600;700&display=swap');

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
    --text-faint: #aabccc;
    --shadow-sm:  0 1px 4px rgba(11,37,69,0.07);
    --shadow-md:  0 4px 16px rgba(11,37,69,0.10);
    --shadow-lg:  0 12px 40px rgba(11,37,69,0.13);
    --r:  12px;
    --rl: 18px;
}

html, body, .stApp {
    background: var(--bg) !important;
    color: var(--text) !important;
    font-family: 'IBM Plex Sans', sans-serif !important;
}
.stApp::before { display: none; }

::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: var(--border-mid); border-radius: 3px; }

/* SIDEBAR */
section[data-testid="stSidebar"] {
    background: var(--navy) !important;
    border-right: none !important;
    box-shadow: 4px 0 24px rgba(11,37,69,0.18) !important;
}
section[data-testid="stSidebar"] > div { padding-top: 0 !important; }

.sb-top {
    padding: 2rem 1.4rem 1.5rem;
    border-bottom: 1px solid rgba(255,255,255,0.07);
    margin-bottom: 1.3rem;
}
.sb-logo { display:flex; align-items:center; gap:0.7rem; margin-bottom:0.2rem; }
.sb-icon {
    width:42px; height:42px; border-radius:10px;
    background: linear-gradient(135deg,#1a6ecc,#0097a7);
    display:flex; align-items:center; justify-content:center;
    font-size:20px; flex-shrink:0;
    box-shadow:0 4px 12px rgba(0,150,200,0.3);
}
.sb-logo h2 {
    font-family:'Playfair Display',serif !important;
    font-weight:700 !important; font-size:1.35rem !important;
    color:#fff !important; letter-spacing:0.04em; margin:0 !important;
}
.sb-sub { font-size:0.65rem; color:rgba(255,255,255,0.3); text-transform:uppercase; letter-spacing:0.15em; padding-left:52px; }

.sb-pill {
    display:inline-flex; align-items:center; gap:0.4rem;
    background:rgba(27,138,90,0.18); border:1px solid rgba(27,138,90,0.32);
    border-radius:20px; padding:0.28rem 0.8rem;
    font-size:0.68rem; color:#5dd4a0; font-weight:500;
    margin:0 1.4rem 1.3rem;
}
.sb-pill .dot {
    width:6px; height:6px; border-radius:50%;
    background:#5dd4a0; box-shadow:0 0 6px rgba(93,212,160,0.8);
    animation:blink 2.5s ease-in-out infinite;
}
@keyframes blink { 0%,100%{opacity:1}50%{opacity:0.3} }

.sb-section-label {
    font-size:0.62rem; text-transform:uppercase; letter-spacing:0.15em;
    color:rgba(255,255,255,0.28); font-weight:600;
    padding:0 1.4rem; margin-bottom:0.4rem;
}
.elder-chip {
    margin:0 0.8rem 1.3rem;
    background:rgba(255,255,255,0.05); border:1px solid rgba(255,255,255,0.09);
    border-radius:var(--r); padding:0.85rem 1rem;
}
.elder-chip .lbl { font-size:0.62rem; text-transform:uppercase; letter-spacing:0.12em; color:rgba(255,255,255,0.28); margin-bottom:0.3rem; }
.elder-chip .val { font-family:'IBM Plex Mono',monospace; font-size:0.84rem; color:rgba(255,255,255,0.82); font-weight:500; }

section[data-testid="stSidebar"] .stTextInput > div > div > input {
    background:rgba(255,255,255,0.06) !important; border:1px solid rgba(255,255,255,0.13) !important;
    border-radius:8px !important; color:#fff !important;
    font-family:'IBM Plex Mono',monospace !important; font-size:0.82rem !important;
    padding:0.5rem 0.8rem !important;
}
section[data-testid="stSidebar"] .stTextInput label {
    color:rgba(255,255,255,0.35) !important; font-size:0.62rem !important;
    text-transform:uppercase !important; letter-spacing:0.12em !important;
}
section[data-testid="stSidebar"] .stTextInput > div > div > input:focus {
    border-color:rgba(0,151,167,0.65) !important;
    box-shadow:0 0 0 3px rgba(0,151,167,0.13) !important; outline:none !important;
}

section[data-testid="stSidebar"] button[kind="secondary"] {
    background:rgba(192,57,43,0.1) !important; color:#ff8a80 !important;
    border:1px solid rgba(192,57,43,0.28) !important; border-radius:8px !important;
    font-size:0.82rem !important; font-weight:500 !important; width:100% !important;
    transition:all 0.2s ease !important;
}
section[data-testid="stSidebar"] button[kind="secondary"]:hover {
    background:rgba(192,57,43,0.2) !important; color:#fff !important;
    border-color:rgba(192,57,43,0.5) !important;
}
section[data-testid="stSidebar"] button[kind="primary"] {
    background:rgba(21, 87, 192, 0.2) !important; color:#85b4ff !important;
    border:1px solid rgba(21, 87, 192, 0.4) !important; border-radius:8px !important;
    font-size:0.82rem !important; font-weight:500 !important; width:100% !important;
    transition:all 0.2s ease !important;
}
section[data-testid="stSidebar"] button[kind="primary"]:hover {
    background:rgba(21, 87, 192, 0.4) !important; color:#fff !important;
    border-color:rgba(21, 87, 192, 0.6) !important;
}

/* MAIN BUTTONS */
.main button[kind="primary"] {
    background:var(--blue) !important; color:#fff !important;
    border:none !important; border-radius:8px !important;
    font-family:'IBM Plex Sans',sans-serif !important;
    font-weight:600 !important; font-size:0.82rem !important;
    letter-spacing:0.02em !important; padding:0.5rem 1.1rem !important;
    transition:all 0.2s ease !important; box-shadow:var(--shadow-sm) !important;
}
.main button[kind="primary"]:hover {
    background:var(--navy-mid) !important;
    box-shadow:var(--shadow-md) !important; transform:translateY(-1px) !important;
}

/* TABS */
.stTabs [data-baseweb="tab-list"] {
    background:var(--white) !important; border-radius:var(--r) !important;
    padding:4px !important; border:1px solid var(--border) !important;
    gap:2px !important; box-shadow:var(--shadow-sm) !important;
}
.stTabs [data-baseweb="tab"] {
    background:transparent !important; border-radius:8px !important;
    color:var(--text-soft) !important; font-family:'IBM Plex Sans',sans-serif !important;
    font-weight:500 !important; font-size:0.82rem !important;
    padding:0.45rem 1.1rem !important; transition:all 0.2s ease !important; border:none !important;
}
.stTabs [aria-selected="true"] {
    background:var(--navy) !important; color:#fff !important;
    box-shadow:0 2px 8px rgba(11,37,69,0.2) !important;
}
.stTabs [data-baseweb="tab-highlight"],.stTabs [data-baseweb="tab-border"] { display:none !important; }

/* INPUTS */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stSelectbox > div > div {
    background:var(--white) !important; border:1.5px solid var(--border) !important;
    border-radius:8px !important; color:var(--text) !important;
    font-family:'IBM Plex Sans',sans-serif !important; transition:all 0.2s ease !important;
}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color:var(--blue) !important; box-shadow:0 0 0 3px rgba(21,87,192,0.1) !important; outline:none !important;
}
.stTextInput label,.stTextArea label,.stSelectbox label {
    color:var(--text-mid) !important; font-size:0.74rem !important;
    font-weight:600 !important; letter-spacing:0.05em !important; text-transform:uppercase !important;
}

/* ALERTS */
.stSuccess { background:var(--green-lt) !important; border:1px solid #a3d9bd !important; border-radius:var(--r) !important; color:var(--green) !important; }
.stError   { background:var(--red-lt) !important;   border:1px solid #f0a8a1 !important; border-radius:var(--r) !important; color:var(--red) !important; }
.stWarning { background:var(--amber-lt) !important;  border:1px solid #f0d080 !important; border-radius:var(--r) !important; }
.stInfo    { background:var(--blue-lt) !important;   border:1px solid #b0c8f0 !important; border-radius:var(--r) !important; color:var(--navy-mid) !important; }
.stSpinner > div { border-top-color:var(--blue) !important; }

.stFileUploader > div {
    background:var(--white) !important; border:2px dashed var(--border-mid) !important;
    border-radius:var(--r) !important; transition:all 0.2s ease !important;
}
.stFileUploader > div:hover { border-color:var(--blue) !important; background:var(--blue-lt) !important; }

/* PAGE */
.main .block-container {
    animation:fadein 0.4s ease; padding-top:2rem !important;
    max-width:100% !important; padding-left:2rem !important; padding-right:2rem !important;
}
@keyframes fadein { from{opacity:0;transform:translateY(8px)} to{opacity:1;transform:translateY(0)} }

/* CUSTOM COMPONENTS */
.pg-header {
    display:flex; align-items:flex-end; justify-content:space-between;
    margin-bottom:1.8rem; padding-bottom:1.2rem; border-bottom:2px solid var(--border);
}
.pg-header h1 {
    font-family:'Playfair Display',serif !important; font-size:1.9rem !important;
    font-weight:700 !important; color:var(--navy) !important; line-height:1.1 !important; margin:0 !important;
}
.pg-sub { font-size:0.77rem; color:var(--text-soft); margin-top:0.3rem; }
.pg-badge {
    background:var(--blue-lt); color:var(--blue); border:1px solid #c0d4f5;
    border-radius:20px; padding:0.28rem 0.85rem;
    font-size:0.68rem; font-weight:700; letter-spacing:0.1em; text-transform:uppercase;
}

.metric-row { display:grid; grid-template-columns:repeat(4,1fr); gap:1rem; margin-bottom:2rem; }
.mc {
    background:var(--white); border:1px solid var(--border); border-radius:var(--rl);
    padding:1.4rem 1.3rem; position:relative; overflow:hidden;
    box-shadow:var(--shadow-sm); transition:all 0.25s ease;
}
.mc:hover { box-shadow:var(--shadow-md); transform:translateY(-2px); border-color:var(--border-mid); }
.mc::after {
    content:''; position:absolute; top:0; left:0; right:0;
    height:4px; border-radius:var(--rl) var(--rl) 0 0;
}
.mc-teal::after  { background:linear-gradient(90deg,#0097a7,#26c6da); }
.mc-blue::after  { background:linear-gradient(90deg,#1557c0,#42a5f5); }
.mc-amber::after { background:linear-gradient(90deg,#c47a00,#f5a623); }
.mc-green::after { background:linear-gradient(90deg,#1b8a5a,#4caf87); }
.mc-icon { font-size:1.5rem; margin-bottom:0.65rem; }
.mc-label { font-size:0.67rem; text-transform:uppercase; letter-spacing:0.12em; color:var(--text-soft); font-weight:600; margin-bottom:0.32rem; }
.mc-value { font-family:'Playfair Display',serif; font-size:2.4rem; font-weight:700; color:var(--navy); line-height:1; }
.mc-sub { font-size:0.68rem; color:var(--text-faint); margin-top:0.28rem; }

.sec-head { display:flex; align-items:center; gap:0.7rem; margin-bottom:1.2rem; }
.sec-head h3 {
    font-family:'IBM Plex Sans',sans-serif !important; font-size:0.8rem !important;
    font-weight:700 !important; text-transform:uppercase !important;
    letter-spacing:0.12em !important; color:var(--text-mid) !important; margin:0 !important; white-space:nowrap;
}
.sec-line { flex:1; height:1px; background:var(--border); }
.sec-note { font-size:0.67rem; color:var(--text-faint); white-space:nowrap; }

.rec-card {
    background:var(--white); border:1px solid var(--border); border-radius:var(--r);
    padding:1rem 1.1rem; margin-bottom:0.65rem;
    transition:all 0.2s ease; box-shadow:var(--shadow-sm);
}
.rec-card:hover { box-shadow:var(--shadow-md); border-color:var(--border-mid); }
.rec-title { font-weight:600; font-size:0.88rem; color:var(--navy); margin-bottom:0.18rem; }
.rec-sub { font-size:0.75rem; color:var(--text-soft); margin-bottom:0.55rem; }
.cbar { height:5px; background:var(--bg); border-radius:3px; overflow:hidden; margin-bottom:0.22rem; border:1px solid var(--border); }
.cfill { height:100%; border-radius:3px; }
.clabel { font-size:0.67rem; color:var(--text-faint); }

.col-tag {
    display:inline-flex; align-items:center; gap:0.35rem;
    padding:0.32rem 0.8rem; border-radius:6px;
    font-size:0.7rem; font-weight:700; text-transform:uppercase; letter-spacing:0.1em;
    margin-bottom:0.9rem;
}
.ct-teal  { color:var(--teal);  background:var(--teal-lt);  border:1px solid #b0e0e6; }
.ct-amber { color:var(--amber); background:var(--amber-lt); border:1px solid #f5d580; }
.ct-blue  { color:var(--blue);  background:var(--blue-lt);  border:1px solid #b0c8f0; }

.sr-item {
    background:var(--white); border:1px solid var(--border);
    border-left:4px solid var(--teal); border-radius:0 var(--r) var(--r) 0;
    padding:0.9rem 1.1rem; margin-bottom:0.65rem;
    box-shadow:var(--shadow-sm); transition:all 0.2s ease;
}
.sr-item:hover { border-left-color:var(--blue); box-shadow:var(--shadow-md); }
.sr-score { font-family:'IBM Plex Mono',monospace; font-size:0.68rem; font-weight:500; color:var(--teal); text-transform:uppercase; letter-spacing:0.08em; margin-bottom:0.28rem; }
.sr-text { font-size:0.87rem; color:var(--text-mid); line-height:1.55; }

.conflict-card {
    background:var(--red-lt); border:1px solid #f0a8a1; border-left:4px solid var(--red);
    border-radius:0 var(--r) var(--r) 0; padding:0.8rem 1.1rem;
    color:var(--red); font-size:0.83rem; margin-top:0.5rem;
    animation:slideIn 0.3s ease;
}
@keyframes slideIn { from{opacity:0;transform:translateX(-8px)} to{opacity:1;transform:translateX(0)} }

.info-panel {
    background:var(--blue-lt); border:1px solid #c0d4f5;
    border-radius:var(--r); padding:1.2rem 1.3rem; margin-bottom:1rem;
}
.info-panel h4 { font-weight:700; font-size:0.76rem; text-transform:uppercase; letter-spacing:0.1em; color:var(--navy-mid); margin-bottom:0.6rem; }
.info-panel ul { margin:0; padding-left:1rem; font-size:0.79rem; color:var(--text-mid); line-height:1.85; }

.req-box {
    background:var(--green-lt); border:1px solid #a3d9bd;
    border-radius:var(--r); padding:1.2rem 1.3rem;
}
.req-box h4 { font-weight:700; font-size:0.76rem; text-transform:uppercase; letter-spacing:0.1em; color:var(--green); margin-bottom:0.6rem; }
.req-box ul { margin:0; padding-left:1rem; font-size:0.79rem; color:var(--text-mid); line-height:1.85; }

.ingest-wrap {
    background:var(--white); border:1px solid var(--border);
    border-radius:var(--rl); padding:2rem; box-shadow:var(--shadow-sm);
}
.graph-wrap { border:1px solid var(--border); border-radius:var(--rl); overflow:hidden; box-shadow:var(--shadow-md); margin-top:1rem; }

.login-brand { text-align:center; margin-bottom:1.8rem; }
.login-icon {
    width:68px; height:68px; border-radius:16px;
    background:linear-gradient(135deg,var(--navy),var(--navy-mid));
    display:flex; align-items:center; justify-content:center;
    font-size:30px; margin:0 auto 1rem;
    box-shadow:0 8px 24px rgba(11,37,69,0.22);
}
.login-brand h1 {
    font-family:'Playfair Display',serif !important; font-size:2rem !important;
    font-weight:700 !important; color:var(--navy) !important; letter-spacing:0.04em; margin:0 !important;
}
.login-brand p { font-size:0.7rem !important; color:var(--text-soft) !important; text-transform:uppercase; letter-spacing:0.2em; margin-top:0.3rem; }
.login-divider { height:1px; background:var(--border); margin:1.4rem 0; }
.login-footer { text-align:center; margin-top:1.4rem; font-size:0.68rem; color:var(--text-faint); }
</style>
""", unsafe_allow_html=True)

# ── Session state ──────────────────────────────────────────────────────────────
if "token" not in st.session_state:
    st.session_state.token = None
if "username" not in st.session_state:
    st.session_state.username = None
if "full_name" not in st.session_state:
    st.session_state.full_name = None
if "elder_id" not in st.session_state:
    st.session_state.elder_id = None
if "session_expired" not in st.session_state:
    st.session_state.session_expired = False
if "registered_username" not in st.session_state:
    st.session_state.registered_username = ""

# ── Helpers ───────────────────────────────────────────────────────────────────
def fetch_data(endpoint):
    try:
        res = requests.get(f"{API_BASE_URL}/api/{endpoint}", headers={"Authorization": f"Bearer {st.session_state.token}"})
        if res.status_code == 401:
            st.session_state.token = None
            st.session_state.session_expired = True
            st.rerun()
        return res.json().get("data", []) if res.status_code == 200 else []
    except:
        return []

def reinforce_node(node_id):
    res = requests.post(f"{API_BASE_URL}/api/memory/reinforce/{node_id}", headers={"Authorization": f"Bearer {st.session_state.token}"})
    if res.status_code == 401:
        st.session_state.token = None
        st.session_state.session_expired = True
        st.rerun()
    st.toast("Memory reinforced ✓" if res.status_code == 200 else "Failed to reinforce", icon="✅" if res.status_code == 200 else "❌")

def conf_bar(score):
    pct = int((score or 0) * 100)
    color = "#1b8a5a" if pct >= 70 else "#c47a00" if pct >= 40 else "#c0392b"
    return f'<div class="cbar"><div class="cfill" style="width:{pct}%;background:{color};"></div></div><div class="clabel" style="color:{color};">{pct}% confidence</div>'


# ── LOGIN ─────────────────────────────────────────────────────────────────────
def login():
    if st.session_state.session_expired:
        st.error("Session expired")
        st.session_state.session_expired = False

    _, col, _ = st.columns([1, 1, 1])
    with col:
        st.markdown("""
        <div class="login-brand">
            <div class="login-icon">🏥</div>
            <h1>SMARAN</h1>
            <p>Caregiver Intelligence Portal</p>
        </div>
        """, unsafe_allow_html=True)
        
        t_login, t_register = st.tabs(["🔐 Sign In", "📝 Register"])
        
        with t_login:
            with st.form("lf"):
                val = st.session_state.registered_username if st.session_state.registered_username else ""
                username = st.text_input("Username", value=val)
                password = st.text_input("Password", type="password")
                st.markdown("<br>", unsafe_allow_html=True)
                submit = st.form_submit_button("Sign In  →", use_container_width=True, type="primary")
            if submit:
                with st.spinner("Verifying credentials..."):
                    try:
                        res = requests.post(f"{API_BASE_URL}/api/auth/login", data={"username": username, "password": password})
                        if res.status_code == 200:
                            data = res.json()
                            st.session_state.token = data["access_token"]
                            
                            # Fetch user profile
                            me_res = requests.get(f"{API_BASE_URL}/api/auth/me", headers={"Authorization": f"Bearer {st.session_state.token}"})
                            if me_res.status_code == 200:
                                profile = me_res.json()
                                st.session_state.username = profile.get("username", username)
                                st.session_state.full_name = profile.get("full_name", username)
                            st.session_state.registered_username = "" # clear after use
                            st.rerun()
                        elif res.status_code == 401:
                            st.error("Incorrect username or password")
                        else:
                            st.error("Server error during login.")
                    except requests.exceptions.RequestException:
                        st.error("Cannot connect to server")
                        
        with t_register:
            with st.form("rf"):
                reg_full_name = st.text_input("Full Name")
                reg_username = st.text_input("Username", help="lowercase, no spaces")
                reg_email = st.text_input("Email")
                reg_password = st.text_input("Password", type="password", help="min 8 chars, 1 number")
                reg_password_confirm = st.text_input("Confirm Password", type="password")
                st.markdown("<br>", unsafe_allow_html=True)
                reg_submit = st.form_submit_button("Register", use_container_width=True, type="primary")
            
            if reg_submit:
                if reg_password != reg_password_confirm:
                    st.error("Passwords do not match.")
                elif len(reg_password) < 8 or not any(char.isdigit() for char in reg_password):
                    st.error("Password must be at least 8 characters with one number.")
                else:
                    with st.spinner("Registering..."):
                        try:
                            payload = {
                                "username": reg_username,
                                "email": reg_email,
                                "password": reg_password,
                                "full_name": reg_full_name,
                                "role": "CAREGIVER"
                            }
                            reg_res = requests.post(f"{API_BASE_URL}/api/auth/register", json=payload)
                            if reg_res.status_code == 200:
                                st.success("Registration successful! Please sign in.")
                                st.session_state.registered_username = reg_username
                            elif reg_res.status_code == 409:
                                err_detail = str(reg_res.json().get("detail", ""))
                                if "Username" in err_detail:
                                    st.error("Username already taken. Try a different one.")
                                elif "Email" in err_detail:
                                    st.error("Email already registered. Try signing in instead.")
                                else:
                                    st.error(err_detail)
                            else:
                                st.error(f"Registration failed: {reg_res.text}")
                        except requests.exceptions.RequestException:
                            st.error("Cannot connect to server")
                            
        st.markdown('<div class="login-footer">SMARAN v1.0 · Secure Clinical Interface</div>', unsafe_allow_html=True)


# ── DASHBOARD ─────────────────────────────────────────────────────────────────
def dashboard():
    headers = {"Authorization": f"Bearer {st.session_state.token}"}

    with st.sidebar:
        st.markdown(f"""
        <div class="sb-top">
            <div class="sb-logo"><div class="sb-icon">🧠</div><h2>SMARAN</h2></div>
            <div class="sb-sub">Memory Care Intelligence</div>
        </div>
        """, unsafe_allow_html=True)
        
        fn = st.session_state.get("full_name") or st.session_state.get("username") or "Caregiver"
        st.markdown(f'<div style="padding:0 1.4rem; font-size: 0.9rem; font-weight:600; color:#fff; margin-bottom:0.6rem;">Welcome, {fn}!</div>', unsafe_allow_html=True)
        if st.session_state.get("username") == "caregiver_demo":
            st.markdown('<div style="background:#fef3c7;color:#d97706;padding:10px;border-radius:8px;margin:0 1.4rem 1rem;font-size:0.8rem;text-align:center;"><strong>Demo Mode Active</strong><br>Using sample caregiver credentials.</div>', unsafe_allow_html=True)
        st.markdown('<div class="login-divider" style="margin:0.5rem 1.4rem 1rem;"></div>', unsafe_allow_html=True)
        
        elder_input = st.text_input("Target Elder ID", value=st.session_state.elder_id if st.session_state.elder_id else "")
        if st.button("Load Elder  →", type="primary", use_container_width=True):
            st.session_state.elder_id = elder_input
            st.rerun()
            
        if st.session_state.elder_id:
            if st.button("🔄 Refresh Data", type="secondary", use_container_width=True):
                st.rerun()

            node_count = 0
            try:
                # Lightweight way to get count if possible or default to checking graph presence
                res = requests.get(f"{API_BASE_URL}/api/memory/mindmap/{st.session_state.elder_id}", headers=headers)
                if res.status_code == 200:
                    data = res.json()
                    # Example mapping extracting length or keeping safe fallback
                    node_count = len(data.get("nodes", []))
                elif res.status_code == 401:
                    st.session_state.token = None
                    st.session_state.session_expired = True
                    st.rerun()
            except:
                pass
            st.markdown(f'<div class="elder-chip" style="margin-top:1rem;"><div class="lbl">Monitoring</div><div class="val">{st.session_state.elder_id}</div><div class="lbl" style="margin-top:0.6rem; color:var(--teal)">Total Memories: {node_count}</div></div>', unsafe_allow_html=True)
            
            
        st.markdown('<div class="login-divider" style="margin:1rem 1.4rem;"></div>', unsafe_allow_html=True)
        if st.button("Logout", type="secondary"):
            try:
                requests.post(f"{API_BASE_URL}/api/auth/logout", headers=headers)
            except:
                pass
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

    if not st.session_state.elder_id:
        st.markdown('<div style="margin-top:5rem;text-align:center;font-size:1.3rem;color:var(--text-soft);">👆 Enter an Elder ID in the sidebar to get started.</div>', unsafe_allow_html=True)
        return

    meds  = fetch_data(f"memory/medicines/{st.session_state.elder_id}")
    appts = fetch_data(f"memory/appointments/{st.session_state.elder_id}")
    syms  = fetch_data(f"memory/symptoms/{st.session_state.elder_id}")

    with st.sidebar:
        export_data = json.dumps({
            "elder_id": st.session_state.elder_id,
            "export_time": datetime.now().isoformat(),
            "medicines": meds,
            "appointments": appts,
            "symptoms": syms
        }, indent=2)
        st.download_button("📥 Export Medical Summary (JSON)", data=export_data, file_name=f"smaran_summary_{st.session_state.elder_id}.json", mime="application/json", use_container_width=True)

    t1, t2, t3, t4, t5 = st.tabs(["📊  Dashboard", "🏥  Medical Records", "📝  Ingest Memory", "🧠  Brain Map", "🎙️  Voice Profiles"])

    # ── TAB 1 ────────────────────────────────────────────────────────────────
    with t1:
        st.markdown(f'<div class="pg-header"><div><h1>Patient Overview</h1><div class="pg-sub">Real-time clinical intelligence · {st.session_state.elder_id}</div></div><span class="pg-badge">Live Data</span></div>', unsafe_allow_html=True)
        st.markdown(f"""
        <div class="metric-row">
            <div class="mc mc-teal"><div class="mc-icon">💊</div><div class="mc-label">Active Medicines</div><div class="mc-value">{len(meds)}</div><div class="mc-sub">Tracked prescriptions</div></div>
            <div class="mc mc-blue"><div class="mc-icon">📅</div><div class="mc-label">Appointments</div><div class="mc-value">{len(appts)}</div><div class="mc-sub">Scheduled visits</div></div>
            <div class="mc mc-amber"><div class="mc-icon">🌡️</div><div class="mc-label">Symptoms</div><div class="mc-value">{len(syms)}</div><div class="mc-sub">Reported & logged</div></div>
            <div class="mc mc-green"><div class="mc-icon">⚡</div><div class="mc-label">System State</div><div class="mc-value" style="font-size:1.25rem;color:var(--green);padding-top:0.4rem;">ONLINE</div><div class="mc-sub">All services active</div></div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown('<div class="sec-head"><h3>Semantic Memory Search</h3><div class="sec-line"></div><span class="sec-note">FAISS + Neo4j Graph</span></div>', unsafe_allow_html=True)
        q = st.text_input("Search", placeholder="e.g. 'back pain', 'Metformin', 'Dr. Gupta appointment'...", label_visibility="collapsed")
        if q:
            start_search = time.time()
            with st.spinner("Searching memory graph..."):
                res = requests.get(f"{API_BASE_URL}/api/memory/search/{st.session_state.elder_id}?query={q}", headers=headers)
            search_ms = int((time.time() - start_search)*1000)
            
            if res.status_code == 200:
                results = res.json().get("results", [])
                if not results:
                    st.markdown('<p style="color:var(--text-faint);font-size:0.83rem;">🧠 No memories found. Use Memory Ingestion to add some.</p>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div style="font-size:0.75rem;color:var(--text-soft);margin-bottom:0.8rem;">{len(results)} result(s) found in {search_ms}ms</div>', unsafe_allow_html=True)
                    for r in results:
                        st.markdown(f'<div class="sr-item"><div class="sr-score">↗ Score {r.get("semantic_score",0):.3f}</div><div class="sr-text">{r.get("context","No context")}</div></div>', unsafe_allow_html=True)
                        st.code(r.get("context", ""), language=None)
            elif res.status_code == 401:
                st.session_state.token = None
                st.session_state.session_expired = True
                st.rerun()
            else:
                st.error("Search failed.")

    # ── TAB 2 ────────────────────────────────────────────────────────────────
    with t2:
        st.markdown(f'<div class="pg-header"><div><h1>Medical Records</h1><div class="pg-sub">Live extraction from knowledge graph · {st.session_state.elder_id}</div></div><span class="pg-badge">Neo4j Graph</span></div>', unsafe_allow_html=True)
        cm, cs, ca = st.columns(3)
        with cm:
            st.markdown('<span class="col-tag ct-teal">💊 Medicines</span>', unsafe_allow_html=True)
            if meds:
                for m in meds:
                    st.markdown(f'<div class="rec-card"><div class="rec-title">{m.get("name","Unknown")}</div><div class="rec-sub">{m.get("dosage","No dosage info")}</div>{conf_bar(m.get("confidence_score",0))}</div>', unsafe_allow_html=True)
                    st.button("↑ Reinforce", key=f"rm_{m.get('id')}", use_container_width=True, on_click=reinforce_node, args=(m.get('id'),))
            else:
                st.markdown('<p style="color:var(--text-faint);font-size:0.83rem;">💊 No medicines recorded yet for this elder.</p>', unsafe_allow_html=True)
        with cs:
            st.markdown('<span class="col-tag ct-amber">🌡️ Symptoms</span>', unsafe_allow_html=True)
            if syms:
                for s in syms:
                    st.markdown(f'<div class="rec-card"><div class="rec-title">{s.get("name","Unknown")}</div><div class="rec-sub">Severity: {s.get("severity","unspecified")}</div>{conf_bar(s.get("confidence_score",0))}</div>', unsafe_allow_html=True)
                    st.button("↑ Reinforce", key=f"rs_{s.get('id')}", use_container_width=True, on_click=reinforce_node, args=(s.get('id'),))
            else:
                st.markdown('<p style="color:var(--text-faint);font-size:0.83rem;">🤒 No symptoms recorded yet.</p>', unsafe_allow_html=True)
        with ca:
            st.markdown('<span class="col-tag ct-blue">📅 Appointments</span>', unsafe_allow_html=True)
            if appts:
                for a in appts:
                    st.markdown(f'<div class="rec-card"><div class="rec-title">{a.get("title","Appointment")}</div><div class="rec-sub">{a.get("datetime","Date TBD")}</div>{conf_bar(a.get("confidence_score",0))}</div>', unsafe_allow_html=True)
                    st.button("↑ Reinforce", key=f"ra_{a.get('id')}", use_container_width=True, on_click=reinforce_node, args=(a.get('id'),))
            else:
                st.markdown('<p style="color:var(--text-faint);font-size:0.83rem;">📅 No appointments recorded yet.</p>', unsafe_allow_html=True)

    # ── TAB 3 ────────────────────────────────────────────────────────────────
    with t3:
        st.markdown('<div class="pg-header"><div><h1>Ingest Memory</h1><div class="pg-sub">NLP extraction pipeline → Neo4j knowledge graph</div></div><span class="pg-badge">spaCy + Graph</span></div>', unsafe_allow_html=True)
        cf, ci = st.columns([5, 3])
        with cf:
            st.markdown('<div class="ingest-wrap">', unsafe_allow_html=True)
            with st.form("if"):
                mem_text = st.text_area("Clinical Observation", placeholder="e.g. 'Ramesh reported chest tightness this morning after a short walk. BP was 140/90.'", height=140)
                source = st.selectbox("Source Type", ["caregiver_input", "sensor", "document", "medical_record"])
                st.markdown("<br>", unsafe_allow_html=True)
                sub = st.form_submit_button("Process & Ingest  →", use_container_width=True, type="primary")
            st.markdown('</div>', unsafe_allow_html=True)
            if sub and mem_text:
                with st.spinner("Running NLP pipeline..."):
                    res = requests.post(f"{API_BASE_URL}/api/memory/ingest", json={"elder_id": st.session_state.elder_id, "text": mem_text, "source_type": source}, headers=headers)
                if res.status_code == 200:
                    d = res.json()
                    n = len(d.get("created_nodes", []))
                    st.success(f"✓ {n} memory node{'s' if n!=1 else ''} written to graph.")
                    for a in d.get("conflict_alerts", []):
                        st.markdown(f'<div class="conflict-card">🚨 <strong>Conflict</strong> — {a["field"]}: was <em>\'{a["old_value"]}\'</em>, now <em>\'{a["new_value"]}\'</em></div>', unsafe_allow_html=True)
                elif res.status_code == 401:
                    st.session_state.token = None
                    st.session_state.session_expired = True
                    st.rerun()
                else:
                    st.error("Ingestion failed. Check API logs.")
        with ci:
            st.markdown("""
            <div class="info-panel">
                <h4>Processing Pipeline</h4>
                <ul>
                    <li>① spaCy named-entity extraction</li>
                    <li>② Intent & category classification</li>
                    <li>③ Conflict detection vs. graph</li>
                    <li>④ Neo4j graph node creation</li>
                    <li>⑤ FAISS vector index update</li>
                </ul>
            </div>
            <div style="background:var(--amber-lt);border:1px solid #f5d580;border-radius:var(--r);padding:1.2rem 1.3rem;">
                <h4 style="font-weight:700;font-size:0.76rem;text-transform:uppercase;letter-spacing:0.1em;color:var(--amber);margin-bottom:0.6rem;">Conflict Detection</h4>
                <ul style="margin:0;padding-left:1rem;font-size:0.79rem;color:var(--text-mid);line-height:1.85;">
                    <li>Alerts fire when new data contradicts nodes with confidence &gt;0.7</li>
                    <li>Review all conflicts before accepting updates</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)

    # ── TAB 4 ────────────────────────────────────────────────────────────────
    with t4:
        st.markdown('<div class="pg-header"><div><h1>Brain Map</h1><div class="pg-sub">Interactive knowledge graph — Pyvis + Neo4j</div></div><span class="pg-badge">Live Graph</span></div>', unsafe_allow_html=True)
        cb, _ = st.columns([1, 4])
        with cb:
            gen = st.button("Generate Graph  →", use_container_width=True, type="primary")
        if gen:
            with st.spinner("Fetching graph topology..."):
                res = requests.get(f"{API_BASE_URL}/api/memory/mindmap/{st.session_state.elder_id}", headers=headers)
            if res.status_code == 200:
                html_map = res.json().get("graph_html")
                if html_map:
                    st.markdown('<div class="graph-wrap">', unsafe_allow_html=True)
                    components.html(html_map, height=640, scrolling=True)
                    st.markdown('</div>', unsafe_allow_html=True)
            elif res.status_code == 401:
                st.session_state.token = None
                st.session_state.session_expired = True
                st.rerun()
            else:
                st.error("Graph fetch failed.")

    # ── TAB 5 ────────────────────────────────────────────────────────────────
    with t5:
        st.markdown('<div class="pg-header"><div><h1>Voice Profiles</h1><div class="pg-sub">ElevenLabs instant voice cloning for Elder panel</div></div><span class="pg-badge">TTS Engine</span></div>', unsafe_allow_html=True)
        cv, cr = st.columns([3, 2])
        with cv:
            st.markdown("""
            <div class="info-panel">
                <h4>About Voice Cloning</h4>
                <ul>
                    <li>Uploaded samples replace standard TTS with a personalised cloned voice</li>
                    <li>Requires ElevenLabs <strong>Creator plan</strong> or above</li>
                    <li>Longer, cleaner samples produce better quality clones</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
            uploaded = st.file_uploader("Upload Voice Sample (.wav or .mp3)", type=["wav", "mp3"])
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Upload & Activate Profile  →", use_container_width=True, type="primary"):
                if uploaded:
                    with st.spinner("Uploading voice profile..."):
                        res = requests.post(f"{API_BASE_URL}/api/voice/upload", files={"file": (uploaded.name, uploaded.getvalue(), uploaded.type)}, data={"elder_id": st.session_state.elder_id}, headers=headers)
                    if res.status_code == 200:
                        st.success("✓ Voice profile uploaded and activated.") 
                    elif res.status_code == 401:
                        st.session_state.token = None
                        st.session_state.session_expired = True
                        st.rerun()
                    else:
                        st.error("Upload failed — verify ElevenLabs API key permissions.")
                else:
                    st.warning("Please select an audio file first.")
        with cr:
            st.markdown("""
            <div class="req-box">
                <h4>Requirements</h4>
                <ul>
                    <li>.wav or .mp3 format</li>
                    <li>30+ seconds recommended</li>
                    <li>Clear audio, minimal background noise</li>
                    <li>Single speaker recording only</li>
                    <li>ElevenLabs Creator plan or above</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)

# ── Entry ─────────────────────────────────────────────────────────────────────
if st.session_state.token is None:
    login()
else:
    dashboard()