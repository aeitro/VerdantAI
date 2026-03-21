"""
frontend/app.py
────────────────
📁 Save as: PLANTDISEASEPROJ/frontend/app.py
           (replaces the existing single-page app)

Entry point for the PlantAI dashboard.
- Injects global CSS / fonts
- Calls require_auth() from existing auth/auth_ui.py
- On successful login → redirects to pages/1_Dashboard.py
- No sidebar on this page
"""

import sys
import os

# ── Path setup — must come before any local imports ───────────────────────────
# Running from inside frontend/, so go one level up to reach auth/ and backend/
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
from auth.auth_ui import require_auth
from db import init_db

# ── Page config — must be the very first Streamlit call ──────────────────────
st.set_page_config(
    page_title="PlantAI",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Initialise scan database on first run ────────────────────────────────────
init_db()

# ── Global CSS & fonts ────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&family=DM+Mono:wght@400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif !important;
    background-color: #0d0d0d !important;
    color: #e8e8e8 !important;
}

/* Hide Streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }

/* Collapsed sidebar on login page */
section[data-testid="stSidebar"] { display: none !important; }

/* Center the auth form vertically */
.main .block-container {
    padding-top: 6vh !important;
    padding-bottom: 3rem !important;
    max-width: 100% !important;
}

/* Input fields */
div[data-testid="stTextInput"] input {
    background: #141414 !important;
    border: 1px solid #2a2a2a !important;
    border-radius: 10px !important;
    color: #e8e8e8 !important;
    font-size: 0.88rem !important;
}
div[data-testid="stTextInput"] input:focus {
    border-color: #5bde8a !important;
    box-shadow: 0 0 0 2px #5bde8a22 !important;
}

/* Tab styling */
div[data-testid="stTabs"] button[role="tab"] {
    font-size: 0.88rem !important;
    font-weight: 500 !important;
    color: #666 !important;
    background: transparent !important;
}
div[data-testid="stTabs"] button[role="tab"][aria-selected="true"] {
    color: #5bde8a !important;
    border-bottom-color: #5bde8a !important;
}

/* Primary button (Log In / Create Account) */
div[data-testid="stButton"] > button[kind="primary"] {
    background: #5bde8a !important;
    color: #0d0d0d !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    font-size: 0.88rem !important;
    width: 100% !important;
    margin-top: 0.4rem !important;
}
div[data-testid="stButton"] > button[kind="primary"]:hover {
    opacity: 0.88 !important;
    transform: none !important;
}
</style>
""", unsafe_allow_html=True)

# ── Auth gate ─────────────────────────────────────────────────────────────────
# require_auth() handles everything:
#   • Not logged in  → renders login/signup UI, calls st.stop()
#   • Logged in      → validates token, rotates if needed, renders sidebar badge
#                      then returns so we can proceed
require_auth()

# ── If we reach here the user is authenticated — redirect to Dashboard ────────
st.switch_page("pages/1_Dashboard.py")