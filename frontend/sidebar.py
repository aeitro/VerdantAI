"""
frontend/sidebar.py
────────────────────
📁 Save as: PLANTDISEASEPROJ/frontend/sidebar.py

Reusable sidebar component for all PlantAI dashboard pages.

Usage (in every page):
    import sys, os
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    from sidebar import render_sidebar
    render_sidebar('dashboard')

Active page keys:
    'dashboard' | 'analyse' | 'history' | 'reports' | 'profile'

Fix notes
─────────
  • Uses st.page_link() instead of st.button() for navigation.
    st.button() rendered as visible green pills and duplicated nav items.
  • Hides Streamlit's auto-generated pages/ navigation via CSS
    (data-testid="stSidebarNav") so there is only ONE nav in the sidebar.
  • Hides the default Streamlit header/footer/menu chrome.
"""

import streamlit as st

# ── CSS ───────────────────────────────────────────────────────────────────────
_SIDEBAR_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&family=DM+Mono:wght@400;500&display=swap');

/* ── Hide ALL Streamlit auto-generated chrome ── */
#MainMenu, footer, header          { visibility: hidden; }

/* This is the key fix — hides the auto pages/ nav Streamlit renders */
div[data-testid="stSidebarNav"]            { display: none !important; }
div[data-testid="collapsedControl"]        { display: none !important; }

/* ── Sidebar shell ── */
section[data-testid="stSidebar"] {
    width: 220px !important;
    min-width: 220px !important;
    background: #0d0d0d !important;
    border-right: 1px solid #1a1a1a !important;
}
section[data-testid="stSidebar"] > div:first-child {
    padding: 0 !important;
    padding-top: 0 !important;
}

/* ── Logo ── */
.sb-logo {
    font-family: 'DM Sans', sans-serif;
    font-size: 1.2rem;
    font-weight: 600;
    letter-spacing: -0.5px;
    color: #f0f0f0;
    padding: 1.4rem 1.2rem 0.2rem 1.2rem;
    display: block;
}
.sb-logo span { color: #5bde8a; }
.sb-tagline {
    font-family: 'DM Sans', sans-serif;
    font-size: 0.6rem;
    color: #2e2e2e;
    letter-spacing: 1px;
    text-transform: uppercase;
    padding: 0 1.2rem 1.2rem 1.2rem;
    display: block;
}

/* ── Divider ── */
.sb-divider {
    border: none;
    border-top: 1px solid #1a1a1a;
    margin: 0 1rem 0.8rem 1rem;
}

/* ── Section label ── */
.sb-section {
    font-family: 'DM Sans', sans-serif;
    font-size: 0.56rem;
    font-weight: 500;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    color: #2e2e2e;
    padding: 0 1.2rem 0.5rem 1.2rem;
    display: block;
}

/* ── st.page_link overrides — make them look like nav items ── */
/* Target the page_link anchor inside the sidebar */
section[data-testid="stSidebar"] a[data-testid="stPageLink-NavLink"] {
    display: flex !important;
    align-items: center !important;
    padding: 0.5rem 1rem !important;
    margin: 0.05rem 0.4rem !important;
    border-radius: 10px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.84rem !important;
    font-weight: 400 !important;
    color: #444 !important;
    text-decoration: none !important;
    border-left: 2px solid transparent !important;
    transition: background 0.15s, color 0.15s !important;
    background: transparent !important;
}
section[data-testid="stSidebar"] a[data-testid="stPageLink-NavLink"]:hover {
    background: rgba(255,255,255,0.03) !important;
    color: #888 !important;
}

/* Active state — injected via .sb-active wrapper */
section[data-testid="stSidebar"] .sb-active a[data-testid="stPageLink-NavLink"] {
    border-left: 2px solid #5bde8a !important;
    background: rgba(91, 222, 138, 0.05) !important;
    color: #5bde8a !important;
    font-weight: 500 !important;
}

/* Remove the default page_link icon/arrow that Streamlit adds */
section[data-testid="stSidebar"] a[data-testid="stPageLink-NavLink"] svg {
    display: none !important;
}

/* ── User card ── */
.sb-user-card {
    background: #141414;
    border: 1px solid #1f1f1f;
    border-radius: 10px;
    padding: 0.65rem 0.9rem;
    margin: 0 0.8rem 0.5rem 0.8rem;
}
.sb-user-label {
    font-size: 0.58rem;
    color: #2e2e2e;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 0.2rem;
    font-family: 'DM Sans', sans-serif;
}
.sb-username {
    font-size: 0.82rem;
    color: #5bde8a;
    font-weight: 500;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    font-family: 'DM Sans', sans-serif;
}

/* ── Logout button — ONLY target button inside sidebar ── */
section[data-testid="stSidebar"] div[data-testid="stButton"] > button {
    background: transparent !important;
    color: #333 !important;
    border: 1px solid #1f1f1f !important;
    border-radius: 8px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.75rem !important;
    font-weight: 400 !important;
    padding: 0.3rem 0.75rem !important;
    width: 100% !important;
    margin-top: 0.3rem !important;
    transition: border-color 0.15s, color 0.15s !important;
    transform: none !important;
}
section[data-testid="stSidebar"] div[data-testid="stButton"] > button:hover {
    border-color: #f5665d !important;
    color: #f5665d !important;
    background: rgba(245,102,93,0.05) !important;
    transform: none !important;
}
</style>
"""

# ── Nav definitions ───────────────────────────────────────────────────────────
_NAV_ITEMS = [
    {"key": "dashboard", "icon": "⬡", "label": "Dashboard", "page": "pages/1_Dashboard.py"},
    {"key": "analyse",   "icon": "◎", "label": "Analyse",   "page": "pages/2_Analyse.py"},
    {"key": "history",   "icon": "≡", "label": "History",   "page": "pages/3_History.py"},
    {"key": "reports",   "icon": "⬒", "label": "Reports",   "page": "pages/4_Reports.py"},
    {"key": "profile",   "icon": "◌", "label": "Profile",   "page": "pages/5_Profile.py"},
]


# ── Public API ────────────────────────────────────────────────────────────────

def render_sidebar(active_page: str) -> None:
    """
    Render the PlantAI sidebar.

    Parameters
    ----------
    active_page : str
        'dashboard' | 'analyse' | 'history' | 'reports' | 'profile'
    """
    st.markdown(_SIDEBAR_CSS, unsafe_allow_html=True)

    with st.sidebar:

        # ── Logo ─────────────────────────────────────────────────────────────
        st.markdown("""
        <span class="sb-logo">Plant<span>AI</span></span>
        <span class="sb-tagline">Leaf disease detection</span>
        <hr class="sb-divider">
        <span class="sb-section">Navigation</span>
        """, unsafe_allow_html=True)

        # ── Nav items via st.page_link() ──────────────────────────────────────
        # Wrap in .sb-active div for active CSS to apply
        for item in _NAV_ITEMS:
            is_active = (item["key"] == active_page)
            label_with_icon = f"{item['icon']}  {item['label']}"

            if is_active:
                st.markdown('<div class="sb-active">', unsafe_allow_html=True)

            st.page_link(
                item["page"],
                label=label_with_icon,
                use_container_width=True,
            )

            if is_active:
                st.markdown("</div>", unsafe_allow_html=True)

        # ── Account section ───────────────────────────────────────────────────
        st.markdown("""
        <hr class="sb-divider" style="margin-top:0.8rem;">
        <span class="sb-section">Account</span>
        """, unsafe_allow_html=True)

        # User card
        user     = st.session_state.get("user", {})
        username = user.get("username", "—") if isinstance(user, dict) else "—"

        st.markdown(f"""
        <div class="sb-user-card">
          <div class="sb-user-label">Signed in as</div>
          <div class="sb-username">🌿 {username}</div>
        </div>
        """, unsafe_allow_html=True)

        # Logout
        if st.button("Log out", key="sb_logout"):
            try:
                import sys, os
                sys.path.insert(
                    0, os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
                )
                from auth.database import revoke_session
                token = st.session_state.get("session_token")
                if token:
                    revoke_session(token)
            except Exception:
                pass
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.switch_page("app.py")