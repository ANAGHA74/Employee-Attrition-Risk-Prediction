"""
Top header bar component.
"""

import textwrap
import streamlit as st
from dashboard.auth import get_current_user


def render_top_header(title: str, subtitle: str, last_updated: str = "Live") -> None:
    """Render the dashboard title, data status, refresh action, and user badge."""
    user = get_current_user()
    user_name = user.get("name", "HR Admin")
    user_email = user.get("email", "hr@company.com")
    initials = "".join([part[0].upper() for part in user_name.split()[:2]]) if user_name else "HA"

    st.markdown('<div class="dashboard-top-spacer"></div>', unsafe_allow_html=True)

    col_left, col_right = st.columns([1.0, 1.28], gap="large")

    with col_left:
        st.markdown(
            textwrap.dedent(f"""
            <div class="dashboard-title-block">
                <h1 class="page-title">{title}</h1>
                <p class="page-subtitle">{subtitle}</p>
            </div>
            """),
            unsafe_allow_html=True
        )

    with col_right:
        r1, r2, r3 = st.columns([1.5, 0.58, 1.05], gap="medium")
        with r1:
            st.markdown(
                textwrap.dedent(f"""
                <div class="timestamp-badge">
                    <span class="status-dot"></span>
                    <span>Data: {last_updated}</span>
                </div>
                """),
                unsafe_allow_html=True
            )
        with r2:
            if st.button("Refresh", key=f"refresh_btn_{title.lower().replace(' ', '_')}", type="primary"):
                st.cache_data.clear()
                st.rerun()
        with r3:
            st.markdown(
                textwrap.dedent(f"""
                <div class="user-profile-badge">
                    <div class="user-avatar">{initials}</div>
                    <div class="user-meta">
                        <span class="user-name">{user_name}</span>
                        <span class="user-email">{user_email}</span>
                    </div>
                </div>
                """),
                unsafe_allow_html=True
            )

    st.markdown("<div class='dashboard-header-gap'></div>", unsafe_allow_html=True)
