"""
Unified Design System & CSS Styling for HR SaaS Attrition Dashboard.
Matches the professional navy sidebar, light workspace, and refined typography
inspired by modern enterprise SaaS design references.
"""

def get_global_css() -> str:
    """Return complete custom CSS stylesheet for injection."""
    return """
<style>
    /* Google Fonts Import */
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Inter:wght@400;500;600;700&display=swap');

    /* Global Root & Typography */
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
        color: #0F172A;
    }
    html, body, .stApp, [data-testid="stAppViewContainer"] {
        height: 100vh !important;
        overflow: hidden !important;
    }

    /* Main App Background */
    .stApp {
        background-color: #F8FAFC !important;
    }
    header[data-testid="stHeader"] {
        background: transparent !important;
        height: 0 !important;
    }
    [data-testid="stToolbar"],
    [data-testid="stDecoration"],
    div[data-testid="stStatusWidget"],
    div[data-testid="stSidebarHeader"],
    div[data-testid="stSidebarCollapsedControl"],
    button[data-testid="stSidebarCollapseButton"],
    section[data-testid="stSidebar"] [data-testid="stBaseButton-headerNoPadding"],
    section[data-testid="stSidebar"] [data-testid="baseButton-headerNoPadding"],
    section[data-testid="stSidebar"] button[kind="headerNoPadding"],
    button[data-testid="stBaseButton-headerNoPadding"]:has(svg),
    button[data-testid="baseButton-headerNoPadding"]:has(svg),
    button[kind="headerNoPadding"]:has(svg),
    [data-testid="stSidebarNavCollapseButton"],
    section[data-testid="stSidebar"] button[title*="collapse" i],
    section[data-testid="stSidebar"] button[aria-label*="collapse" i],
    section[data-testid="stSidebar"] button:has(svg):not(.st-emotion-cache-noop) {
        display: none !important;
    }
    [data-testid="stAppViewContainer"] {
        display: flex !important;
        align-items: stretch !important;
    }
    [data-testid="stMain"] {
        height: 100vh !important;
        overflow-y: auto !important;
        overflow-x: hidden !important;
        background: #F8FAFC !important;
    }

    /* Container padding */
    .block-container {
        padding-top: 1.6rem !important;
        padding-bottom: 2rem !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
        max-width: 1540px !important;
    }

    /* Top Navigation / Header in Main Content */
    .dashboard-top-spacer {
        height: 0.25rem;
    }
    .dashboard-title-block {
        background: transparent;
        border: 0;
        box-shadow: none;
        padding: 0;
        margin: 0;
    }
    .dashboard-header-gap {
        height: 0.7rem;
    }
    .page-title {
        font-size: clamp(2rem, 2.7vw, 2.55rem);
        font-weight: 800;
        color: #0F172A;
        margin: 0;
        letter-spacing: 0;
        line-height: 1.08;
    }
    .page-subtitle {
        font-size: 0.98rem;
        color: #64748B;
        margin-top: 0.35rem;
        margin-bottom: 0;
        line-height: 1.45;
    }
    .timestamp-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 9999px;
        padding: 0 12px;
        font-size: 0.80rem;
        font-weight: 500;
        color: #475569;
        white-space: nowrap;
        box-shadow: 0 1px 2px rgba(0,0,0,0.03);
        height: 38px;
        min-height: 38px;
        max-height: 38px;
        margin: 0 !important;
        box-sizing: border-box;
        max-width: 100%;
        overflow: hidden;
    }
    .status-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background-color: #10B981;
        display: inline-block;
        flex-shrink: 0;
    }
    .user-profile-badge {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 9999px;
        padding: 0 12px 0 6px;
        box-shadow: 0 1px 2px rgba(0,0,0,0.03);
        white-space: nowrap;
        height: 38px;
        min-height: 38px;
        max-height: 38px;
        max-width: 100%;
        margin: 0 !important;
        box-sizing: border-box;
        overflow: hidden;
    }

    /* Clean Top Header Row Alignment */
    div[data-testid="stHorizontalBlock"]:has(.dashboard-title-block) {
        align-items: center !important;
    }
    div[data-testid="stHorizontalBlock"]:has(.timestamp-badge) {
        align-items: center !important;
        display: flex !important;
    }
    div[data-testid="stHorizontalBlock"]:has(.timestamp-badge) > [data-testid="column"] {
        display: flex !important;
        align-items: center !important;
        justify-content: flex-end !important;
    }
    div[data-testid="stHorizontalBlock"]:has(.timestamp-badge) div[data-testid="stButton"] {
        margin: 0 !important;
        display: flex !important;
        align-items: center !important;
    }
    div[data-testid="stHorizontalBlock"]:has(.timestamp-badge) div[data-testid="stButton"] button {
        height: 38px !important;
        min-height: 38px !important;
        max-height: 38px !important;
        line-height: 38px !important;
        padding: 0 16px !important;
        margin: 0 !important;
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
        box-sizing: border-box !important;
    }
    .user-avatar {
        width: 30px;
        height: 30px;
        border-radius: 50%;
        background: linear-gradient(135deg, #2563EB, #1D4ED8);
        color: #FFFFFF;
        font-size: 0.80rem;
        font-weight: 700;
        display: flex;
        align-items: center;
        justify-content: center;
        flex-shrink: 0;
    }
    .user-meta {
        display: flex;
        flex-direction: column;
        line-height: 1.15;
        min-width: 0;
    }
    .user-name {
        font-size: 0.82rem;
        font-weight: 700;
        color: #0F172A;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    .user-email {
        font-size: 0.72rem;
        color: #64748B;
        overflow: hidden;
        text-overflow: ellipsis;
    }

    /* Dark Navy Vertical Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #0B132B !important;
        border-right: 1px solid #1E293B !important;
        width: 320px !important;
        min-width: 320px !important;
        max-width: 320px !important;
        height: 100vh !important;
        overflow: hidden !important;
        flex-shrink: 0 !important;
        transform: none !important;
    }
    section[data-testid="stSidebar"] [data-testid="stSidebarUserContent"],
    section[data-testid="stSidebar"] [data-testid="stSidebarContent"] {
        height: 100% !important;
        min-height: 100vh !important;
        display: flex !important;
        flex-direction: column !important;
        padding: 1.5rem 1rem 24px 1rem !important;
        box-sizing: border-box !important;
        overflow-y: auto !important;
        overflow-x: hidden !important;
    }
    section[data-testid="stSidebar"] [data-testid="stSidebarUserContent"] > div,
    section[data-testid="stSidebar"] [data-testid="stSidebarUserContent"] [data-testid="stVerticalBlock"],
    section[data-testid="stSidebar"] [data-testid="stSidebarUserContent"] .stVerticalBlock {
        min-height: calc(100vh - 1.5rem - 24px) !important;
        height: 100% !important;
        display: flex !important;
        flex-direction: column !important;
        flex: 1 1 auto !important;
    }

    /* Brand Logo & Header in Sidebar */
    .sidebar-brand-box {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 0.5rem 0.4rem 1.15rem 0.4rem;
        border-bottom: 1px solid #1E293B;
        margin-bottom: 1.25rem;
    }
    .brand-icon {
        width: 40px;
        height: 40px;
        border-radius: 10px;
        background: linear-gradient(135deg, #2563EB, #1D4ED8);
        display: flex;
        align-items: center;
        justify-content: center;
        color: #FFFFFF;
        font-size: 0.86rem;
        font-weight: 800;
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.35);
        flex-shrink: 0;
    }
    .brand-text-wrap {
        display: flex;
        flex-direction: column;
    }
    .brand-title {
        font-size: 1.05rem;
        font-weight: 800;
        color: #FFFFFF;
        letter-spacing: -0.01em;
        line-height: 1.2;
    }
    .brand-subtitle {
        font-size: 0.72rem;
        color: #94A3B8;
        font-weight: 500;
    }
    .sidebar-nav-start {
        height: 0.15rem;
    }
    /* Spacer element container expands to absorb space and anchor logout to bottom */
    section[data-testid="stSidebar"] div[data-testid="stElementContainer"]:has(.sidebar-bottom-spacer) {
        margin-top: auto !important;
        flex-grow: 1 !important;
        display: flex !important;
        flex-direction: column !important;
        justify-content: flex-end !important;
        width: 100% !important;
    }
    .sidebar-bottom-spacer {
        width: 100% !important;
        border-bottom: 1px solid #1E293B !important;
        margin: 0.75rem 0 0.5rem 0 !important;
        height: 1px !important;
    }
    section[data-testid="stSidebar"] div[data-testid="stElementContainer"]:has(.sidebar-bottom-spacer) + div[data-testid="stElementContainer"],
    section[data-testid="stSidebar"] div[data-testid="stElementContainer"]:last-child {
        margin-top: 0 !important;
        margin-bottom: 0 !important;
        width: 100% !important;
        flex-shrink: 0 !important;
    }

    /* Style Streamlit Buttons in Sidebar */
    section[data-testid="stSidebar"] div.stButton > button {
        width: 100%;
        text-align: left;
        justify-content: flex-start;
        border-radius: 8px;
        padding: 12px 14px;
        font-size: 0.9rem;
        font-weight: 600;
        background-color: transparent;
        color: #94A3B8;
        border: 1px solid transparent;
        transition: all 0.15s ease-in-out;
        margin-bottom: 0.45rem;
    }
    section[data-testid="stSidebar"] div.stButton > button:hover {
        background-color: #1E293B;
        color: #FFFFFF;
        border-color: #334155;
    }
    section[data-testid="stSidebar"] div.stButton > button:focus {
        box-shadow: none;
    }

    /* Bordered content card styling */
    div[data-testid="stVerticalBlockBorderWrapper"]:has(.card-title) {
        border-radius: 12px !important;
        border-color: #E2E8F0 !important;
        background-color: #FFFFFF !important;
        box-shadow: 0 1px 3px rgba(15, 23, 42, 0.04) !important;
        padding: 6px !important;
        overflow: hidden !important;
    }
    [data-testid="stMain"] .block-container > div[data-testid="stVerticalBlockBorderWrapper"],
    section[data-testid="stSidebar"] div[data-testid="stSidebarUserContent"] > div[data-testid="stVerticalBlockBorderWrapper"],
    div[data-testid="stVerticalBlockBorderWrapper"]:not(:has(.card-title)) {
        border-radius: 0 !important;
        border: 0 !important;
        background-color: transparent !important;
        box-shadow: none !important;
        padding: 0 !important;
        overflow: visible !important;
    }

    /* KPI Cards */
    .kpi-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 1.15rem 1.25rem;
        box-shadow: 0 1px 3px rgba(15, 23, 42, 0.04);
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        min-height: 167px;
        height: 100%;
        transition: transform 0.15s ease, box-shadow 0.15s ease;
    }
    .kpi-card:hover {
        box-shadow: 0 4px 12px rgba(15, 23, 42, 0.06);
    }
    .kpi-card-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 0.5rem;
    }
    .kpi-label {
        font-size: 0.84rem;
        font-weight: 600;
        color: #64748B;
    }
    .kpi-icon-wrap {
        width: 34px;
        height: 34px;
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.05rem;
    }
    .kpi-icon-blue { background-color: #EFF6FF; color: #2563EB; }
    .kpi-icon-red { background-color: #FEF2F2; color: #DC2626; }
    .kpi-icon-amber { background-color: #FFFBEB; color: #D97706; }
    .kpi-icon-purple { background-color: #FAF5FF; color: #9333EA; }

    .kpi-value {
        font-size: 2.15rem;
        font-weight: 800;
        color: #0F172A;
        line-height: 1.1;
        letter-spacing: -0.02em;
    }
    .kpi-value-red { color: #DC2626; }

    .kpi-subtext {
        font-size: 0.82rem;
        color: #64748B;
        font-weight: 500;
        margin-top: 0.4rem;
    }

    /* Content Card Titles */
    .card-title {
        font-size: 1.05rem;
        font-weight: 700;
        color: #0F172A;
        margin-bottom: 0.15rem;
        line-height: 1.25;
    }
    .card-subtitle {
        font-size: 0.84rem;
        color: #64748B;
        margin-bottom: 0.85rem;
        line-height: 1.45;
    }

    /* Overview-specific dashboard layout */
    body:has(.overview-page-marker) [data-testid="stMain"] .block-container {
        padding-top: 1.5rem !important;
    }
    body:has(.overview-page-marker) [data-testid="stHorizontalBlock"] {
        align-items: stretch !important;
    }
    body:has(.overview-page-marker) [data-testid="stHorizontalBlock"] > [data-testid="column"] {
        min-width: 0 !important;
    }
    body:has(.overview-page-marker) .overview-table-scroll {
        display: block;
        width: 100%;
        max-width: 100%;
        box-sizing: border-box;
        contain: inline-size;
        overflow-x: auto !important;
        overflow-y: hidden;
        padding-bottom: 8px;
        scrollbar-gutter: stable;
    }
    body:has(.overview-page-marker) .overview-table-scroll table {
        min-width: 520px;
    }
    body:has(.overview-page-marker) .overview-table-scroll::-webkit-scrollbar {
        height: 10px;
    }
    body:has(.overview-page-marker) .overview-table-scroll::-webkit-scrollbar-track {
        background: #F1F5F9;
        border-radius: 999px;
    }
    body:has(.overview-page-marker) .overview-table-scroll::-webkit-scrollbar-thumb {
        background: #CBD5E1;
        border-radius: 999px;
    }
    body:has(.overview-page-marker) .overview-risk-legend {
        display: flex;
        justify-content: center;
        gap: 12px;
        flex-wrap: wrap;
        margin-top: 4px;
        font-size: 0.78rem;
    }
    body:has(.overview-page-marker) .overview-risk-legend > div {
        display: flex;
        align-items: center;
        gap: 6px;
    }
    body:has(.overview-page-marker) .overview-risk-legend span {
        white-space: nowrap;
    }
    body:has(.overview-page-marker) div[data-testid="stVerticalBlockBorderWrapper"]:has(.overview-risk-legend) {
        min-height: 500px !important;
        overflow: visible !important;
    }
    body:has(.overview-page-marker) div[data-testid="stVerticalBlockBorderWrapper"]:has(.overview-table-scroll) {
        min-height: 500px !important;
        overflow: visible !important;
    }
    body:has(.overview-page-marker) [data-testid="stMain"] {
        scroll-padding-top: 1.5rem;
    }

    /* High-risk employee action list layout */
    body:has(.high-risk-page-marker) [data-testid="stMain"] .block-container {
        padding-top: 1.1rem !important;
        padding-right: 2rem !important;
        max-width: 1480px !important;
    }
    body:has(.high-risk-page-marker) [data-testid="stHorizontalBlock"] {
        align-items: stretch !important;
    }
    body:has(.high-risk-page-marker) [data-testid="stHorizontalBlock"] > [data-testid="column"] {
        min-width: 0 !important;
    }
    body:has(.high-risk-page-marker) div[data-testid="stVerticalBlockBorderWrapper"] {
        overflow: visible !important;
    }
    body:has(.high-risk-page-marker) .dashboard-top-spacer {
        height: 0.1rem;
    }
    body:has(.high-risk-page-marker) .dashboard-header-gap {
        height: 0.25rem;
    }
    body:has(.high-risk-page-marker) .page-title {
        font-size: clamp(2rem, 2.45vw, 2.35rem);
        line-height: 1.05;
        max-width: none;
    }
    body:has(.high-risk-page-marker) .page-subtitle {
        margin-top: 0.35rem;
        max-width: 620px;
    }
    body:has(.high-risk-page-marker) div[data-testid="stVerticalBlockBorderWrapper"]:not(:has(.card-title)) {
        overflow: visible !important;
    }

    /* Filter Toolbar Row - Vertically centered controls in one clean row */
    body:has(.high-risk-page-marker) div[data-testid="stVerticalBlockBorderWrapper"]:has(.stTextInput):has(.stMultiSelect):has(.stSelectbox) {
        padding: 0 !important;
        margin-top: 0.35rem !important;
        margin-bottom: 0.65rem !important;
        overflow: visible !important;
        border: none !important;
        background: transparent !important;
    }
    body:has(.high-risk-page-marker) div[data-testid="stVerticalBlockBorderWrapper"]:has(.stTextInput):has(.stMultiSelect):has(.stSelectbox) [data-testid="stHorizontalBlock"] {
        align-items: center !important;
        gap: 0.65rem !important;
    }
    body:has(.high-risk-page-marker) div[data-testid="stVerticalBlockBorderWrapper"]:has(.stTextInput):has(.stMultiSelect):has(.stSelectbox) [data-testid="column"] {
        min-width: 0 !important;
        position: relative !important;
        display: flex !important;
        flex-direction: column !important;
        justify-content: center !important;
    }
    body:has(.high-risk-page-marker) div[data-testid="stVerticalBlockBorderWrapper"]:has(.stTextInput):has(.stMultiSelect):has(.stSelectbox) label,
    body:has(.high-risk-page-marker) .high-risk-sort-label {
        display: none !important;
        height: 0 !important;
        min-height: 0 !important;
        margin: 0 !important;
        padding: 0 !important;
        visibility: hidden !important;
        opacity: 0 !important;
        pointer-events: none !important;
    }
    body:has(.high-risk-page-marker) div[data-testid="stVerticalBlockBorderWrapper"]:has(.stTextInput):has(.stMultiSelect):has(.stSelectbox) [data-testid="stElementContainer"] {
        margin: 0 !important;
        padding: 0 !important;
        width: 100% !important;
    }
    body:has(.high-risk-page-marker) .stSelectbox,
    body:has(.high-risk-page-marker) [data-testid="stMultiSelect"],
    body:has(.high-risk-page-marker) .stTextInput,
    body:has(.high-risk-page-marker) [data-testid="stTextInput"] {
        min-width: 0 !important;
        margin-bottom: 0 !important;
        height: 42px !important;
        min-height: 42px !important;
        max-height: 42px !important;
    }
    body:has(.high-risk-page-marker) .stTextInput input,
    body:has(.high-risk-page-marker) .stSelectbox [data-baseweb="select"] {
        min-height: 42px !important;
        height: 42px !important;
        max-height: 42px !important;
        align-items: center !important;
        box-sizing: border-box !important;
        font-size: 0.82rem !important;
    }
    body:has(.high-risk-page-marker) [data-testid="stMultiSelect"] [data-baseweb="select"] {
        min-height: 42px !important;
        height: 42px !important;
        max-height: 42px !important;
        align-items: center !important;
        box-sizing: border-box !important;
        overflow: hidden !important;
    }
    body:has(.high-risk-page-marker) [data-testid="stMultiSelect"] div:has(> [data-baseweb="tag"]),
    body:has(.high-risk-page-marker) [data-testid="stMultiSelect"] [data-testid="stMultiSelectTagsContainer"] {
        flex-wrap: nowrap !important;
        overflow-x: auto !important;
        overflow-y: hidden !important;
        max-height: 38px !important;
        scrollbar-width: none !important;
        -ms-overflow-style: none !important;
    }
    body:has(.high-risk-page-marker) [data-testid="stMultiSelect"] [data-testid="stMultiSelectTagsContainer"]::-webkit-scrollbar {
        display: none !important;
    }
    body:has(.high-risk-page-marker) [data-testid="stMultiSelect"] [data-baseweb="tag"] {
        max-width: 110px !important;
        height: 24px !important;
        line-height: 24px !important;
        margin: 0 4px 0 0 !important;
        padding-top: 0 !important;
        padding-bottom: 0 !important;
        padding-left: 6px !important;
        padding-right: 3px !important;
        border-radius: 6px !important;
        background-color: #F1F5F9 !important;
        color: #1E293B !important;
        border: 1px solid #CBD5E1 !important;
        flex-shrink: 0 !important;
        display: inline-flex !important;
        align-items: center !important;
        box-sizing: border-box !important;
    }
    body:has(.high-risk-page-marker) [data-testid="stMultiSelect"] [data-baseweb="tag"] span {
        font-size: 0.74rem !important;
        font-weight: 500 !important;
        color: #1E293B !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
        white-space: nowrap !important;
        max-width: 80px !important;
        display: inline-block !important;
    }
    body:has(.high-risk-page-marker) [data-testid="stMultiSelect"] [data-baseweb="tag"] button {
        color: #64748B !important;
        padding: 0 2px !important;
        margin: 0 !important;
        flex-shrink: 0 !important;
    }
    body:has(.high-risk-page-marker) [data-testid="stMultiSelect"] [data-baseweb="tag"] button:hover {
        color: #DC2626 !important;
    }

    /* Replace "No results" with "All departments selected" in multiselect dropdown */
    div[data-testid="stMultiSelectDropdown"] ul > span,
    div[data-testid="stMultiSelectDropdown"] [data-baseweb="menu"] span {
        font-size: 0 !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        min-height: 42px !important;
        padding: 8px 14px !important;
        color: #64748B !important;
        background: #FFFFFF !important;
    }
    div[data-testid="stMultiSelectDropdown"] ul > span::after,
    div[data-testid="stMultiSelectDropdown"] [data-baseweb="menu"] span::after {
        content: "All departments selected" !important;
        font-size: 0.84rem !important;
        color: #64748B !important;
        font-weight: 500 !important;
        display: inline-block !important;
    }

    /* Hide marker elements */
    .high-risk-page-marker,
    .high-risk-filter-marker,
    .high-risk-table-marker,
    .high-risk-table-card-marker,
    .high-risk-details-marker {
        display: none !important;
        height: 0 !important;
        width: 0 !important;
        margin: 0 !important;
        padding: 0 !important;
    }

    body:has(.high-risk-page-marker) .badge {
        white-space: nowrap;
    }
    body:has(.high-risk-page-marker) div[data-testid="stVerticalBlockBorderWrapper"]:has(.high-risk-table-marker) {
        overflow: visible !important;
        max-width: 100% !important;
    }
    body:has(.high-risk-page-marker) div[data-testid="stVerticalBlockBorderWrapper"]:has(.high-risk-table-card-marker) {
        overflow: visible !important;
        max-width: 100% !important;
        padding: 1.1rem !important;
    }
    body:has(.high-risk-page-marker) div[data-testid="stVerticalBlockBorderWrapper"]:has(.high-risk-table-card-marker) [data-testid="stHorizontalBlock"] {
        align-items: center !important;
        margin-bottom: 0.45rem !important;
    }
    body:has(.high-risk-page-marker) div[data-testid="stVerticalBlockBorderWrapper"]:has(.high-risk-table-card-marker) div[data-testid="stDownloadButton"] button {
        min-height: 38px !important;
        height: 38px !important;
    }
    body:has(.high-risk-page-marker) .high-risk-table-scroll {
        width: 100% !important;
        max-width: 100% !important;
        height: 350px !important;
        max-height: 350px !important;
        overflow-x: scroll !important;
        overflow-y: scroll !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 8px !important;
        background: #FFFFFF !important;
        scrollbar-width: thin !important;
        scrollbar-color: #94A3B8 #F1F5F9 !important;
    }
    body:has(.high-risk-page-marker) .high-risk-table-scroll::-webkit-scrollbar {
        width: 10px !important;
        height: 12px !important;
        display: block !important;
    }
    body:has(.high-risk-page-marker) .high-risk-table-scroll::-webkit-scrollbar-track {
        background: #F1F5F9 !important;
        border-radius: 6px !important;
    }
    body:has(.high-risk-page-marker) .high-risk-table-scroll::-webkit-scrollbar-thumb {
        background-color: #94A3B8 !important;
        border-radius: 6px !important;
        border: 2px solid #F1F5F9 !important;
        min-width: 40px !important;
    }
    body:has(.high-risk-page-marker) .high-risk-table-scroll::-webkit-scrollbar-thumb:hover {
        background-color: #64748B !important;
    }
    body:has(.high-risk-page-marker) .high-risk-table-scroll::-webkit-scrollbar-corner {
        background: #F1F5F9 !important;
    }
    body:has(.high-risk-page-marker) .high-risk-employee-table {
        min-width: 1120px;
        width: max-content;
        border-collapse: separate;
        border-spacing: 0;
        font-size: 0.82rem;
        color: #0F172A;
    }
    body:has(.high-risk-page-marker) .high-risk-employee-table th,
    body:has(.high-risk-page-marker) .high-risk-employee-table td {
        padding: 10px 12px;
        border-right: 1px solid #E5E7EB;
        border-bottom: 1px solid #E5E7EB;
        white-space: nowrap;
        text-align: left;
        vertical-align: middle;
    }
    body:has(.high-risk-page-marker) .high-risk-employee-table thead th {
        position: sticky;
        top: 0;
        z-index: 1;
        background: #F8FAFC;
        color: #64748B;
        font-size: 0.76rem;
        font-weight: 600;
    }
    body:has(.high-risk-page-marker) .high-risk-employee-table .cell-number {
        text-align: right;
        font-variant-numeric: tabular-nums;
    }
    body:has(.high-risk-page-marker) .high-risk-employee-table .cell-status {
        font-weight: 700;
    }
    body:has(.high-risk-page-marker) .high-risk-employee-table .cell-high,
    body:has(.high-risk-page-marker) .high-risk-employee-table .cell-yes {
        background: #FEE2E2;
        color: #DC2626;
    }
    body:has(.high-risk-page-marker) .high-risk-employee-table .cell-medium {
        background: #FEF3C7;
        color: #D97706;
    }
    body:has(.high-risk-page-marker) .high-risk-employee-table .cell-low {
        background: #DCFCE7;
        color: #16A34A;
    }
    body:has(.high-risk-page-marker) .high-risk-employee-table .cell-no {
        background: #F1F5F9;
        color: #64748B;
    }
    body:has(.high-risk-page-marker) div[data-testid="stVerticalBlockBorderWrapper"]:has(.high-risk-details-marker) {
        max-width: 100% !important;
        overflow: hidden !important;
        contain: inline-size;
    }
    body:has(.high-risk-page-marker) div[data-testid="stVerticalBlockBorderWrapper"]:has(.high-risk-details-marker) [data-testid="stSelectbox"] {
        margin-bottom: 1rem !important;
    }

    /* Risk analytics filters */
    body:has(.risk-analytics-page-marker) [data-testid="stMain"] .block-container {
        padding-top: 1.25rem !important;
    }
    body:has(.risk-analytics-page-marker) [data-testid="stHorizontalBlock"] {
        align-items: stretch !important;
    }
    body:has(.risk-analytics-page-marker) [data-testid="stHorizontalBlock"] > [data-testid="column"] {
        min-width: 0 !important;
    }
    body:has(.risk-analytics-page-marker) div[data-testid="stVerticalBlockBorderWrapper"]:has(.stSelectbox):not(:has(.card-title)) {
        padding: 0 !important;
        margin-top: 0.1rem !important;
        overflow: visible !important;
    }
    body:has(.risk-analytics-page-marker) div[data-testid="stVerticalBlockBorderWrapper"]:has(.stSelectbox):not(:has(.card-title)) [data-testid="stHorizontalBlock"] {
        align-items: flex-start !important;
        gap: 0.75rem !important;
    }
    body:has(.risk-analytics-page-marker) .stSelectbox {
        min-width: 0 !important;
    }
    body:has(.risk-analytics-page-marker) .stSelectbox label {
        min-height: 20px !important;
        line-height: 20px !important;
        margin-bottom: 6px !important;
        overflow: visible !important;
    }
    body:has(.risk-analytics-page-marker) .stSelectbox [data-baseweb="select"] {
        min-height: 46px !important;
    }

    /* Key attrition drivers layout */
    body:has(.key-drivers-page-marker) [data-testid="stMain"] .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 4rem !important;
    }
    body:has(.key-drivers-page-marker) div[data-testid="stVerticalBlockBorderWrapper"]:has(.card-title) {
        overflow: visible !important;
    }
    body:has(.key-drivers-page-marker) div[data-testid="stVerticalBlockBorderWrapper"]:has(.key-driver-info-card) {
        min-height: 210px !important;
    }
    body:has(.key-drivers-page-marker) .key-driver-info-card {
        padding-bottom: 0.5rem;
    }

    /* Pipeline page layout */
    body:has(.pipeline-page-marker) [data-testid="stMain"] .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 4rem !important;
    }
    body:has(.pipeline-page-marker) [data-testid="stHorizontalBlock"] {
        align-items: stretch !important;
    }
    body:has(.pipeline-page-marker) [data-testid="stHorizontalBlock"] > [data-testid="column"] {
        min-width: 0 !important;
    }
    body:has(.pipeline-page-marker) div[data-testid="stVerticalBlockBorderWrapper"]:has(.pipeline-architecture-content) {
        min-height: 292px !important;
        overflow: visible !important;
    }
    body:has(.pipeline-page-marker) .pipeline-architecture-content {
        padding-bottom: 0.65rem;
    }

    /* Risk analytics table scroll affordance */
    body:has(.risk-analytics-page-marker) .survey-sentiment-scroll {
        width: 100%;
        max-width: 100%;
        overflow-x: scroll !important;
        overflow-y: hidden;
        padding-bottom: 10px;
        scrollbar-gutter: stable;
    }
    body:has(.risk-analytics-page-marker) .survey-sentiment-scroll::-webkit-scrollbar {
        height: 10px;
    }
    body:has(.risk-analytics-page-marker) .survey-sentiment-scroll::-webkit-scrollbar-track {
        background: #F1F5F9;
        border-radius: 999px;
    }
    body:has(.risk-analytics-page-marker) .survey-sentiment-scroll::-webkit-scrollbar-thumb {
        background: #A8AEB8;
        border-radius: 999px;
    }
    body:has(.risk-analytics-page-marker) table.survey-sentiment-table {
        min-width: 680px;
        width: max-content;
        border-collapse: separate;
        border-spacing: 0;
        font-size: 0.86rem;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        overflow: hidden;
    }
    body:has(.risk-analytics-page-marker) table.survey-sentiment-table th,
    body:has(.risk-analytics-page-marker) table.survey-sentiment-table td {
        padding: 10px 12px;
        border-right: 1px solid rgba(226, 232, 240, 0.85);
        border-bottom: 1px solid rgba(226, 232, 240, 0.85);
        white-space: nowrap;
        min-width: 118px;
        text-align: right;
    }
    body:has(.risk-analytics-page-marker) table.survey-sentiment-table th:first-child,
    body:has(.risk-analytics-page-marker) table.survey-sentiment-table td:first-child {
        text-align: left;
        min-width: 92px;
    }
    body:has(.risk-analytics-page-marker) table.survey-sentiment-table thead th {
        color: #64748B;
        font-weight: 600;
        background: #F8FAFC;
    }

    /* Risk Badges */
    .badge {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        padding: 3px 8px;
        border-radius: 6px;
        font-size: 0.76rem;
        font-weight: 700;
        letter-spacing: 0.02em;
        line-height: 1.2;
    }
    .badge-high {
        background-color: #FEE2E2;
        color: #DC2626;
        border: 1px solid #FECACA;
    }
    .badge-medium {
        background-color: #FEF3C7;
        color: #D97706;
        border: 1px solid #FDE68A;
    }
    .badge-low {
        background-color: #DCFCE7;
        color: #16A34A;
        border: 1px solid #BBF7D0;
    }

    /* Primary Blue Action Buttons */
    div.stButton > button[kind="primary"],
    div[data-testid="stFormSubmitButton"] > button,
    button[data-testid="stBaseButton-primary"],
    button[kind="primaryFormSubmit"] {
        background-color: #0062FF !important;
        border-color: #0062FF !important;
        color: #FFFFFF !important;
        font-weight: 600 !important;
        border-radius: 9px !important;
        box-shadow: 0 4px 14px rgba(0, 98, 255, 0.35) !important;
    }
    div.stButton > button[kind="primary"]:hover,
    div[data-testid="stFormSubmitButton"] > button:hover,
    button[data-testid="stBaseButton-primary"]:hover,
    button[kind="primaryFormSubmit"]:hover {
        background-color: #0052CC !important;
        border-color: #0052CC !important;
        box-shadow: 0 6px 18px rgba(0, 98, 255, 0.45) !important;
    }

    /* Clean Streamlit Dataframe / Table */
    [data-testid="stDataFrame"] {
        border: 1px solid #E2E8F0 !important;
        border-radius: 10px !important;
        overflow: hidden !important;
    }

    @media (max-width: 1180px) {
        .block-container {
            padding-left: 1.25rem !important;
            padding-right: 1.25rem !important;
        }
        .page-title {
            font-size: 2rem;
        }
        .timestamp-badge,
        .user-profile-badge {
            justify-content: center;
            width: 100%;
        }
        body:has(.overview-page-marker) [data-testid="stMain"] .block-container [data-testid="stHorizontalBlock"] {
            flex-wrap: wrap !important;
        }
        body:has(.overview-page-marker) [data-testid="stMain"] .block-container [data-testid="stHorizontalBlock"] > [data-testid="column"] {
            min-width: min(100%, 320px) !important;
            flex: 1 1 320px !important;
        }
        body:has(.high-risk-page-marker) [data-testid="stMain"] .block-container [data-testid="stHorizontalBlock"] {
            flex-wrap: wrap !important;
        }
        body:has(.high-risk-page-marker) [data-testid="stMain"] .block-container [data-testid="stHorizontalBlock"] > [data-testid="column"] {
            min-width: min(100%, 340px) !important;
            flex: 1 1 340px !important;
        }
    }

    @media (max-width: 700px) {
        html, body, .stApp, [data-testid="stAppViewContainer"] {
            overflow: auto !important;
            height: auto !important;
        }
        [data-testid="stAppViewContainer"] {
            display: block !important;
        }
        [data-testid="stMain"] {
            height: auto !important;
            overflow: visible !important;
        }
        section[data-testid="stSidebar"] {
            position: relative !important;
            width: 100% !important;
            min-width: 0 !important;
            max-width: none !important;
            height: auto !important;
        }
        section[data-testid="stSidebar"] [data-testid="stSidebarUserContent"] {
            height: auto !important;
            overflow: visible !important;
        }
        section[data-testid="stSidebar"] [data-testid="stSidebarUserContent"] > div {
            min-height: 0 !important;
        }
        .sidebar-bottom-spacer {
            flex: 0 0 auto;
            min-height: 0.5rem;
        }
    }
</style>
"""
