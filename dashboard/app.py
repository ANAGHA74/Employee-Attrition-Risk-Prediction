"""
AttritionRisk HR - Enterprise Employee Retention Intelligence SaaS Platform.
Redesigned with modular architecture, secure session authentication,
executive overview, interactive risk analytics, high-risk employee action list,
key attrition driver signals, and separate technical HDFS pipeline controls.
"""
# Updated UI layout for filter toolbar and sidebar bottom anchoring
import sys
from pathlib import Path
import streamlit as st

# Setup page configuration
st.set_page_config(
    page_title="AttritionRisk HR | Retention Intelligence",
    page_icon="👥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Project root paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "dashboard"))
sys.path.insert(0, str(PROJECT_ROOT / "hdfs"))
sys.path.insert(0, str(PROJECT_ROOT / "ml"))

from dashboard.styles import get_global_css
from dashboard.auth import is_authenticated
from dashboard.data_loader import load_and_score_data
from dashboard.components.sidebar import render_sidebar
from dashboard.views.login_view import render_login_page
from dashboard.views.overview_view import render_overview_page
from dashboard.views.risk_analytics_view import render_risk_analytics_page
from dashboard.views.high_risk_view import render_high_risk_page
from dashboard.views.key_drivers_view import render_key_drivers_page
from dashboard.views.pipeline_view import render_pipeline_page


def main():
    # Inject Global Design System CSS
    st.markdown(get_global_css(), unsafe_allow_html=True)

    # Enterprise Security Barrier: Render pixel-perfect branded authentication gateway.
    if not is_authenticated():
        render_login_page()
        return

    # Authenticated User Experience: Persistent Sidebar Navigation
    active_page = render_sidebar()

    # Load and score employee records
    display_df, meta = load_and_score_data()

    # Page Routing
    if active_page == "overview":
        render_overview_page(display_df, meta)
    elif active_page == "risk_analytics":
        render_risk_analytics_page(display_df, meta)
    elif active_page == "high_risk":
        render_high_risk_page(display_df, meta)
    elif active_page == "key_drivers":
        render_key_drivers_page(meta)
    elif active_page == "pipeline":
        render_pipeline_page(display_df, meta)
    else:
        render_overview_page(display_df, meta)


if __name__ == "__main__":
    main()
