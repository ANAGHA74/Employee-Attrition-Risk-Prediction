"""
Persistent dark navy sidebar navigation component.
"""

import streamlit as st
from dashboard.auth import logout_user

NAV_ITEMS = [
    ("overview", "Overview"),
    ("risk_analytics", "Risk Analytics"),
    ("high_risk", "High-Risk Employees"),
    ("key_drivers", "Key Attrition Drivers"),
    ("pipeline", "Pipeline & Data"),
]

def render_sidebar() -> str:
    """
    Render persistent sidebar navigation.
    Returns the currently active page ID.
    """
    if "active_page" not in st.session_state:
        st.session_state["active_page"] = "overview"

    with st.sidebar:
        st.markdown(
            """
            <div class="sidebar-brand-box">
                <div class="brand-icon">HR</div>
                <div class="brand-text-wrap">
                    <span class="brand-title">AttritionRisk HR</span>
                    <span class="brand-subtitle">Employee Retention Intelligence</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        current_page = st.session_state["active_page"]
        st.markdown("<div class='sidebar-nav-start'></div>", unsafe_allow_html=True)

        for page_id, label in NAV_ITEMS:
            is_active = (current_page == page_id)
            btn_type = "primary" if is_active else "secondary"

            if st.button(
                label,
                key=f"nav_btn_{page_id}",
                type=btn_type,
                use_container_width=True
            ):
                if current_page != page_id:
                    st.session_state["active_page"] = page_id
                    st.rerun()

        st.markdown("<div class='sidebar-bottom-spacer'></div>", unsafe_allow_html=True)

        if st.button("Logout", key="logout_sidebar_btn", use_container_width=True):
            logout_user()

    return st.session_state["active_page"]
