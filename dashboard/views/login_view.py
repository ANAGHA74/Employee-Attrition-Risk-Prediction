"""
Page 1: Login Page.
Implements the professional branded split-screen login page matching the exact design reference.

Fixes applied:
- Left panel has guaranteed deep navy background (#081630) with rich gradient and wave graphics.
- White login card on the right has natural, compact spacing (no empty gaps between Password and Remember me).
- Password input is full-width with embedded lock icon and native show/hide eye toggle matching the reference image.
- Royal blue Sign In button (#0062FF).
- 'or continue with' and social login buttons completely removed.
- Demo credentials box embedded at the bottom of the card.
"""

import streamlit as st
from dashboard.auth import authenticate, login_user


def clean_html(html_str: str) -> str:
    """
    Remove all indentation and empty lines from HTML strings.
    Prevents CommonMark from mistakenly interpreting indented lines as code blocks.
    """
    return "\n".join(line.strip() for line in html_str.splitlines() if line.strip())


def render_login_page():
    """Render the login screen matching the visual reference."""
    # 1. Inject Page-specific Layout and Component CSS
    login_css = clean_html("""
    <style>
        /* Hide all Streamlit default chrome on login page */
        header[data-testid="stHeader"] {
            display: none !important;
        }
        footer {
            display: none !important;
        }
        section[data-testid="stSidebar"] {
            display: none !important;
        }
        div[data-testid="stSidebarCollapsedControl"] {
            display: none !important;
        }
        #MainMenu {
            display: none !important;
        }
        [data-testid="stToolbar"] {
            display: none !important;
        }
        [data-testid="stDecoration"] {
            display: none !important;
        }

        /* App Background & Layout Container */
        .stApp {
            background-color: #EDF2F8 !important;
            font-family: 'Plus Jakarta Sans', 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
        }
        .stApp > div {
            min-height: 100vh !important;
        }
        [data-testid="stMain"] .block-container,
        .main .block-container {
            max-width: 1180px !important;
            min-height: 100vh !important;
            padding-top: clamp(1rem, 2.4vh, 1.5rem) !important;
            padding-bottom: clamp(1rem, 2.4vh, 1.5rem) !important;
            padding-left: 1.5rem !important;
            padding-right: 1.5rem !important;
            margin: 0 auto !important;
            display: flex !important;
            align-items: center !important;
        }
        [data-testid="stMain"] .block-container > div,
        .main .block-container > div {
            width: 100% !important;
        }
        [data-testid="stMain"] .block-container div[data-testid="stVerticalBlockBorderWrapper"]:has(.left-hero-card),
        body:has(.left-hero-card) .main .block-container div[data-testid="stVerticalBlockBorderWrapper"] {
            background: transparent !important;
            border: 0 !important;
            box-shadow: none !important;
            padding: 0 !important;
        }

        /* Left Hero Card - Guaranteed Deep Navy Background */
        .left-hero-card {
            background-color: #071530 !important;
            background-image:
                radial-gradient(circle at 12% 16%, rgba(0, 194, 255, 0.12), transparent 26%),
                linear-gradient(168deg, #06132C 0%, #091B3A 45%, #0B244E 100%) !important;
            border-radius: 20px !important;
            padding: 34px 40px 28px 40px !important;
            color: #FFFFFF !important;
            min-height: 0 !important;
            height: min(620px, calc(100vh - 3rem)) !important;
            display: flex !important;
            flex-direction: column !important;
            justify-content: space-between !important;
            position: relative !important;
            overflow: hidden !important;
            box-shadow: 0 15px 35px rgba(7, 21, 48, 0.35) !important;
        }

        /* Ensure markdown container inside the first column does not enforce white background */
        [data-testid="column"]:first-of-type [data-testid="stMarkdownContainer"] {
            background: transparent !important;
        }

        /* White Login Card (stForm) - Natural Compact Spacing (No space-between gaps) */
        div[data-testid="stForm"] {
            background: #FFFFFF !important;
            border: 1px solid rgba(226, 232, 240, 0.95) !important;
            border-radius: 20px !important;
            padding: 32px 38px 26px 38px !important;
            box-shadow: 0 15px 35px rgba(15, 23, 42, 0.07) !important;
            display: block !important;
            height: auto !important;
            min-height: 0 !important;
            max-height: calc(100vh - 3rem) !important;
            overflow: visible !important;
        }
        div[data-testid="stForm"] > div {
            display: flex !important;
            flex-direction: column !important;
            gap: 0 !important;
            height: auto !important;
            min-height: 0 !important;
        }
        div[data-testid="stForm"] [data-testid="stMarkdownContainer"] {
            margin: 0 !important;
        }
        div[data-testid="stForm"] div[data-testid="stTextInput"] {
            margin-bottom: 12px !important;
        }
        div[data-testid="stForm"] div[data-testid="stTextInput"] > div {
            height: auto !important;
        }
        div[data-testid="stForm"] [data-testid="stHorizontalBlock"] {
            align-items: center !important;
            gap: 1rem !important;
            margin: 0 0 14px 0 !important;
        }
        div[data-testid="stForm"] [data-testid="stHorizontalBlock"] [data-testid="column"] {
            min-height: 0 !important;
        }

        /* Form Labels */
        div[data-testid="stTextInput"] label p {
            font-size: 0.86rem !important;
            font-weight: 600 !important;
            color: #334155 !important;
            margin-bottom: 3px !important;
        }

        /* Text Input Base Styling */
        div[data-testid="stTextInput"] input {
            background-color: #F8FAFC !important;
            border: 1px solid #E2E8F0 !important;
            border-radius: 9px !important;
            font-size: 0.90rem !important;
            color: #0F172A !important;
            height: 44px !important;
            transition: border-color 0.2s ease, box-shadow 0.2s ease, background-color 0.2s ease !important;
        }
        div[data-testid="stTextInput"] input:focus {
            background-color: #FFFFFF !important;
            border-color: #0062FF !important;
            box-shadow: 0 0 0 3px rgba(0, 98, 255, 0.12) !important;
            outline: none !important;
        }

        /* Embedded Mail Icon inside Email Input */
        input[aria-label="Email or Username"] {
            padding-left: 40px !important;
            background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='17' height='17' viewBox='0 0 24 24' fill='none' stroke='%2364748B' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Crect width='20' height='16' x='2' y='4' rx='2'/%3E%3Cpath d='m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7'/%3E%3C/svg%3E") !important;
            background-repeat: no-repeat !important;
            background-position: 13px center !important;
        }

        /* Embedded Lock Icon inside Password Input */
        input[aria-label="Password"] {
            padding-left: 40px !important;
            padding-right: 42px !important;
            background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='17' height='17' viewBox='0 0 24 24' fill='none' stroke='%2364748B' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Crect width='18' height='11' x='3' y='11' rx='2' ry='2'/%3E%3Cpath d='M7 11V7a5 5 0 0 1 10 0v4'/%3E%3C/svg%3E") !important;
            background-repeat: no-repeat !important;
            background-position: 13px center !important;
        }

        /* Password Show/Hide Toggle Button inside the input */
        button[data-testid="stTextInputToggleVisibility"] {
            color: #64748B !important;
            height: 44px !important;
            width: 40px !important;
            margin: 0 !important;
            padding: 0 !important;
            display: inline-flex !important;
            align-items: center !important;
            justify-content: center !important;
        }
        button[data-testid="stTextInputToggleVisibility"]:hover {
            color: #0062FF !important;
        }

        /* Checkbox Styling */
        div[data-testid="stCheckbox"] {
            margin: 0 !important;
            padding: 0 !important;
        }
        div[data-testid="stCheckbox"] label {
            display: inline-flex !important;
            align-items: center !important;
            gap: 8px !important;
            min-height: 24px !important;
        }
        div[data-testid="stCheckbox"] label p {
            font-size: 0.85rem !important;
            font-weight: 500 !important;
            color: #334155 !important;
            margin: 0 !important;
        }

        /* Prominent Royal Blue Sign In Button */
        div[data-testid="stFormSubmitButton"] {
            margin-top: 0 !important;
            margin-bottom: 0 !important;
        }
        div[data-testid="stFormSubmitButton"] > button {
            background: #0062FF !important;
            background-color: #0062FF !important;
            color: #FFFFFF !important;
            border: none !important;
            border-radius: 9px !important;
            font-size: 0.96rem !important;
            font-weight: 600 !important;
            height: 46px !important;
            line-height: 46px !important;
            box-shadow: 0 4px 14px rgba(0, 98, 255, 0.35) !important;
            transition: all 0.2s ease !important;
            letter-spacing: 0.01em !important;
        }
        div[data-testid="stFormSubmitButton"] > button:hover {
            background: #0052CC !important;
            background-color: #0052CC !important;
            box-shadow: 0 6px 20px rgba(0, 98, 255, 0.45) !important;
            transform: translateY(-1px) !important;
        }
        div[data-testid="stFormSubmitButton"] > button:active {
            transform: translateY(0) !important;
        }

        @media (max-width: 900px) {
            [data-testid="stMain"] .block-container,
            .main .block-container {
                display: block !important;
                padding-top: 1rem !important;
                padding-bottom: 1rem !important;
            }
            [data-testid="stMain"] .block-container div[data-testid="stVerticalBlockBorderWrapper"]:has(.left-hero-card) > div > [data-testid="stVerticalBlock"] > [data-testid="stHorizontalBlock"],
            body:has(.left-hero-card) .main .block-container [data-testid="stHorizontalBlock"] {
                flex-direction: column !important;
            }
            [data-testid="stMain"] .block-container div[data-testid="stVerticalBlockBorderWrapper"]:has(.left-hero-card) > div > [data-testid="stVerticalBlock"] > [data-testid="stHorizontalBlock"] > [data-testid="column"],
            body:has(.left-hero-card) .main .block-container [data-testid="stHorizontalBlock"] > [data-testid="column"] {
                width: 100% !important;
            }
            div[data-testid="stForm"] [data-testid="stHorizontalBlock"] {
                flex-direction: row !important;
            }
            div[data-testid="stForm"] [data-testid="stHorizontalBlock"] > [data-testid="column"] {
                width: calc(50% - 0.5rem) !important;
            }
            .left-hero-card {
                height: auto !important;
                min-height: 420px !important;
                padding: 28px !important;
                margin-bottom: 1rem !important;
            }
            div[data-testid="stForm"] {
                max-height: none !important;
                padding: 28px !important;
            }
        }

        @media (max-height: 720px) and (min-width: 901px) {
            .left-hero-card {
                height: calc(100vh - 2rem) !important;
                padding: 26px 34px 24px 34px !important;
            }
            div[data-testid="stForm"] {
                padding: 26px 34px 22px 34px !important;
            }
            div[data-testid="stForm"] div[data-testid="stTextInput"] {
                margin-bottom: 10px !important;
            }
        }
    </style>
    """)
    st.markdown(login_css, unsafe_allow_html=True)

    # 2. Main Two-Column Layout
    col_hero, col_form = st.columns([1.18, 1.0], gap="large")

    # ================= LEFT HERO PANEL =================
    with col_hero:
        hero_content_html = clean_html("""
        <div class="left-hero-card" style="background-color: #071530; background-image: radial-gradient(circle at 12% 16%, rgba(0, 194, 255, 0.12), transparent 26%), linear-gradient(168deg, #06132C 0%, #091B3A 45%, #0B244E 100%); border-radius: 20px; padding: 34px 40px 28px 40px; color: #FFFFFF; min-height: 0; height: min(620px, calc(100vh - 3rem)); display: flex; flex-direction: column; justify-content: space-between; position: relative; overflow: hidden; box-shadow: 0 15px 35px rgba(7, 21, 48, 0.35);">
            <!-- Subtle Layered Wave Background Graphics matching Reference -->
            <svg viewBox="0 0 600 700" preserveAspectRatio="none" style="position: absolute; bottom: 0; left: 0; width: 100%; height: 50%; pointer-events: none; z-index: 1; opacity: 0.85;">
                <defs>
                    <linearGradient id="wave1" x1="0" y1="0" x2="1" y2="1">
                        <stop offset="0%" stop-color="#0E2D5E" stop-opacity="0.6"/>
                        <stop offset="100%" stop-color="#07193C" stop-opacity="0.95"/>
                    </linearGradient>
                    <linearGradient id="wave2" x1="0" y1="0" x2="1" y2="0">
                        <stop offset="0%" stop-color="#123E7C" stop-opacity="0.7"/>
                        <stop offset="100%" stop-color="#0A2452" stop-opacity="0.85"/>
                    </linearGradient>
                    <linearGradient id="wave3" x1="0" y1="1" x2="1" y2="0">
                        <stop offset="0%" stop-color="#1650A2" stop-opacity="0.55"/>
                        <stop offset="100%" stop-color="#0E2F66" stop-opacity="0.2"/>
                    </linearGradient>
                </defs>
                <path d="M0,320 C180,270 380,440 600,310 L600,700 L0,700 Z" fill="url(#wave1)"/>
                <path d="M0,410 C200,350 420,510 600,390 L600,700 L0,700 Z" fill="url(#wave2)"/>
                <path d="M0,500 C260,440 420,590 600,480 L600,700 L0,700 Z" fill="url(#wave3)"/>
            </svg>

            <!-- Top Header & Main Content -->
            <div style="position: relative; z-index: 2;">
                <!-- Brand Logo & Header -->
                <div style="display: flex; align-items: center; gap: 14px; margin-bottom: 2.2rem;">
                    <div style="width: 44px; height: 44px; border-radius: 12px; background: linear-gradient(135deg, #1D68FE, #0052CC); display: flex; align-items: center; justify-content: center; box-shadow: 0 8px 20px rgba(29, 104, 254, 0.35); flex-shrink: 0;">
                        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#FFFFFF" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                            <path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/>
                            <circle cx="9" cy="7" r="4"/>
                            <path d="M22 21v-2a4 4 0 0 0-3-3.87"/>
                            <path d="M16 3.13a4 4 0 0 1 0 7.75"/>
                        </svg>
                    </div>
                    <div>
                        <div style="font-size: 1.35rem; font-weight: 800; letter-spacing: -0.015em; line-height: 1.2;">
                            <span style="color: #FFFFFF;">AttritionRisk</span> <span style="color: #00A3FF;">HR</span>
                        </div>
                        <div style="font-size: 0.80rem; color: #94A3B8; font-weight: 500; margin-top: 1px;">
                            Employee Retention Intelligence
                        </div>
                    </div>
                </div>

                <!-- Headline -->
                <h1 style="font-size: 2.3rem; font-weight: 800; line-height: 1.15; margin: 0 0 0.9rem 0; letter-spacing: -0.025em; color: #FFFFFF;">
                    Turn Data into<br>
                    <span style="color: #00C2FF;">Retention Action</span>
                </h1>

                <!-- Subtitle Description -->
                <p style="font-size: 0.92rem; color: #CBD5E1; line-height: 1.55; margin-bottom: 2rem; max-width: 440px;">
                    Identify at-risk employees early, understand key drivers, and support a healthier, more engaged workforce with data-driven insights.
                </p>

                <!-- Three Key Feature Highlights -->
                <div style="display: flex; flex-direction: column; gap: 16px;">
                    <!-- Feature 1: AI-powered risk prediction -->
                    <div style="display: flex; align-items: center; gap: 14px;">
                        <div style="width: 40px; height: 40px; border-radius: 50%; background: #132B50; border: 1px solid rgba(255, 255, 255, 0.1); display: flex; align-items: center; justify-content: center; flex-shrink: 0; box-shadow: 0 4px 10px rgba(0,0,0,0.2);">
                            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#38BDF8" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                <line x1="18" y1="20" x2="18" y2="10"/>
                                <line x1="12" y1="20" x2="12" y2="4"/>
                                <line x1="6" y1="20" x2="6" y2="14"/>
                            </svg>
                        </div>
                        <div>
                            <div style="font-size: 0.92rem; font-weight: 700; color: #FFFFFF; line-height: 1.2;">AI-powered risk prediction</div>
                            <div style="font-size: 0.80rem; color: #94A3B8; margin-top: 2px;">Leverage machine learning to detect attrition risk early</div>
                        </div>
                    </div>

                    <!-- Feature 2: Big Data pipeline (Kafka + HDFS) -->
                    <div style="display: flex; align-items: center; gap: 14px;">
                        <div style="width: 40px; height: 40px; border-radius: 50%; background: #132B50; border: 1px solid rgba(255, 255, 255, 0.1); display: flex; align-items: center; justify-content: center; flex-shrink: 0; box-shadow: 0 4px 10px rgba(0,0,0,0.2);">
                            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#38BDF8" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                <ellipse cx="12" cy="5" rx="9" ry="3"/>
                                <path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"/>
                                <path d="M3 12c0 1.66 4 3 9 3s9-1.34 9-3"/>
                            </svg>
                        </div>
                        <div>
                            <div style="font-size: 0.92rem; font-weight: 700; color: #FFFFFF; line-height: 1.2;">Big Data pipeline (Kafka + HDFS)</div>
                            <div style="font-size: 0.80rem; color: #94A3B8; margin-top: 2px;">Scalable and reliable data processing</div>
                        </div>
                    </div>

                    <!-- Feature 3: Actionable insights for HR -->
                    <div style="display: flex; align-items: center; gap: 14px;">
                        <div style="width: 40px; height: 40px; border-radius: 50%; background: #132B50; border: 1px solid rgba(255, 255, 255, 0.1); display: flex; align-items: center; justify-content: center; flex-shrink: 0; box-shadow: 0 4px 10px rgba(0,0,0,0.2);">
                            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#38BDF8" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                <path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/>
                                <circle cx="9" cy="7" r="4"/>
                                <path d="M22 21v-2a4 4 0 0 0-3-3.87"/>
                                <path d="M16 3.13a4 4 0 0 1 0 7.75"/>
                            </svg>
                        </div>
                        <div>
                            <div style="font-size: 0.92rem; font-weight: 700; color: #FFFFFF; line-height: 1.2;">Actionable insights for HR</div>
                            <div style="font-size: 0.80rem; color: #94A3B8; margin-top: 2px;">Empower teams with data-driven decisions</div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Bottom Left Secure Access Footer -->
            <div style="display: flex; align-items: center; gap: 12px; margin-top: 2rem; position: relative; z-index: 2;">
                <div style="width: 38px; height: 38px; border-radius: 10px; background: rgba(14, 44, 91, 0.85); border: 1px solid rgba(56, 189, 248, 0.35); display: flex; align-items: center; justify-content: center; flex-shrink: 0;">
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#38BDF8" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
                        <rect width="8" height="6" x="8" y="11" rx="1"/>
                        <path d="M10 11V9a2 2 0 1 1 4 0v2"/>
                    </svg>
                </div>
                <div>
                    <div style="font-size: 0.88rem; font-weight: 700; color: #E2E8F0; line-height: 1.2;">Secure Access</div>
                    <div style="font-size: 0.76rem; color: #94A3B8; margin-top: 2px;">Your data is protected and confidential</div>
                </div>
            </div>
        </div>
        """)
        st.markdown(hero_content_html, unsafe_allow_html=True)

    # ================= RIGHT FORM PANEL =================
    with col_form:
        # Wrap entire card inside st.form (using normal block layout, no flex stretch)
        with st.form("login_form", clear_on_submit=False):
            # Card Header: Centered Blue Icon, Heading, and Subheading
            card_header_html = clean_html("""
            <div style="text-align: center; margin-bottom: 20px;">
                <div style="display: inline-flex; align-items: center; justify-content: center; width: 44px; height: 44px; margin-bottom: 10px;">
                    <svg width="38" height="38" viewBox="0 0 24 24" fill="#0062FF">
                        <path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/>
                        <circle cx="9" cy="7" r="4"/>
                        <path d="M22 21v-2a4 4 0 0 0-3-3.87"/>
                        <path d="M16 3.13a4 4 0 0 1 0 7.75"/>
                    </svg>
                </div>
                <h2 style="font-size: 1.65rem; font-weight: 800; color: #0F172A; margin: 0 0 4px 0; letter-spacing: -0.02em;">
                    Welcome Back
                </h2>
                <p style="font-size: 0.86rem; color: #64748B; margin: 0; font-weight: 400;">
                    Sign in to access the HR Dashboard
                </p>
            </div>
            """)
            st.markdown(card_header_html, unsafe_allow_html=True)

            # Email or Username Input (Full width, embedded mail icon)
            email_input = st.text_input(
                "Email or Username",
                value="hr@company.com",
                placeholder="hr@company.com"
            )

            # Password Input (Full width, embedded lock icon, native eye show/hide control on right)
            password_input = st.text_input(
                "Password",
                value="hr123",
                type="password",
                placeholder="••••••••"
            )

            # Remember me & Forgot password? Row (clean, immediate vertical alignment right below password)
            col_rem, col_forgot = st.columns([1, 1])
            with col_rem:
                remember_me = st.checkbox("Remember me", value=True)
            with col_forgot:
                forgot_link_html = clean_html("""
                <div style="text-align: right; padding-top: 1px;">
                    <a href="#" style="font-size: 0.84rem; color: #0062FF; font-weight: 600; text-decoration: none;">
                        Forgot password?
                    </a>
                </div>
                """)
                st.markdown(forgot_link_html, unsafe_allow_html=True)

            # Prominent Blue Submit Button (never red)
            submit_btn = st.form_submit_button(
                "Sign In  →",
                type="primary",
                use_container_width=True
            )

            # Demo Credentials Info Panel (Note: social buttons removed per instruction)
            demo_credentials_html = clean_html("""
            <div style="background: #F0F8FF; border: 1px solid #BAE6FD; border-radius: 10px; padding: 12px 14px; margin-top: 16px;">
                <div style="display: flex; align-items: center; gap: 7px; margin-bottom: 5px;">
                    <div style="width: 16px; height: 16px; border-radius: 50%; background: #0284C7; color: #FFFFFF; display: flex; align-items: center; justify-content: center; font-size: 10px; font-weight: 700; flex-shrink: 0;">i</div>
                    <span style="font-size: 0.84rem; font-weight: 700; color: #0369A1;">
                        Demo Credentials (for project use)
                    </span>
                </div>
                <div style="font-size: 0.80rem; color: #334155; line-height: 1.5; padding-left: 23px;">
                    <div><strong>Email:</strong> <span style="color: #059669; font-weight: 600;">hr@company.com</span></div>
                    <div><strong>Password:</strong> <span style="color: #059669; font-weight: 600;">hr123</span></div>
                </div>
            </div>
            """)
            st.markdown(demo_credentials_html, unsafe_allow_html=True)

        # Handle form submission and server-side verification
        if submit_btn:
            is_valid, message = authenticate(email_input, password_input)
            if is_valid:
                login_user(email_input, remember_me=remember_me)
                st.success("Authentication successful! Redirecting to dashboard...")
                st.rerun()
            else:
                st.error(f"⚠️ {message}")
