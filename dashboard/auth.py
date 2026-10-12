"""
Secure Authentication Module for HR SaaS Attrition Dashboard.
Uses PBKDF2-HMAC-SHA256 password hashing and secure session management.
Keeps credentials externalized in .env or local environment variables.
"""

import os
import hmac
import hashlib
from pathlib import Path
from typing import Tuple, Dict, Any, Optional

import streamlit as st
from dotenv import load_dotenv

# Ensure environment is loaded from project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent
ENV_PATH = PROJECT_ROOT / ".env"
if ENV_PATH.exists():
    load_dotenv(dotenv_path=ENV_PATH)
else:
    load_dotenv()

# Demo fallback defaults if not provided in .env
DEFAULT_DEMO_EMAIL = "hr@company.com"
DEFAULT_DEMO_SALT = "639d90687e3af242da2bfe25f3aed7d9"
DEFAULT_DEMO_HASH = "9e4e9c3a4915a7a9d9f16ee6e581ee1f4a16b27691d180fd071bed737b2064aa"


def hash_password(password: str, salt: Optional[str] = None) -> Tuple[str, str]:
    """
    Hash a password using PBKDF2-HMAC-SHA256 with 100,000 iterations.
    Returns (hex_hash, hex_salt).
    """
    if salt is None:
        salt = os.urandom(16).hex()
    pwd_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        100_000
    ).hex()
    return pwd_hash, salt


def verify_password(password: str, salt: str, expected_hash: str) -> bool:
    """Verify input password against expected PBKDF2 hash in constant time."""
    calc_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        100_000
    ).hex()
    return hmac.compare_digest(calc_hash, expected_hash)


def get_auth_config() -> Dict[str, str]:
    """
    Load authentication configuration from environment variables.
    If none set, falls back to secure default hashed demo credentials.
    """
    email = os.getenv("DASHBOARD_ADMIN_EMAIL", DEFAULT_DEMO_EMAIL).strip().lower()
    salt = os.getenv("DASHBOARD_ADMIN_SALT", DEFAULT_DEMO_SALT).strip()
    pwd_hash = os.getenv("DASHBOARD_ADMIN_PWD_HASH", DEFAULT_DEMO_HASH).strip()

    # Optional plaintext override if user explicitly put DASHBOARD_ADMIN_PASSWORD in .env
    plaintext_override = os.getenv("DASHBOARD_ADMIN_PASSWORD")
    if plaintext_override:
        pwd_hash, salt = hash_password(plaintext_override, salt=salt or None)

    return {
        "email": email,
        "salt": salt,
        "hash": pwd_hash
    }


def authenticate(identifier: str, password: str) -> Tuple[bool, str]:
    """
    Validate user credentials against local environment configuration.
    Returns (is_valid, message).
    """
    clean_identifier = identifier.strip().lower()
    clean_password = password.strip()

    if not clean_identifier or not clean_password:
        return False, "Please enter both email/username and password."

    config = get_auth_config()
    configured_email = config["email"]
    # Allow logging in with either the full email or username prefix
    configured_username = configured_email.split("@")[0] if "@" in configured_email else configured_email

    if clean_identifier != configured_email and clean_identifier != configured_username:
        return False, "Invalid email/username or password. Please verify your credentials."

    if not verify_password(clean_password, config["salt"], config["hash"]):
        return False, "Invalid email/username or password. Please verify your credentials."

    return True, "Authentication successful."


def login_user(email: str, remember_me: bool = False) -> None:
    """Establish authenticated session in Streamlit session state."""
    st.session_state["authenticated"] = True
    st.session_state["user_email"] = email
    st.session_state["user_name"] = "HR Admin"
    st.session_state["user_role"] = "Talent & Retention Intelligence"
    st.session_state["remember_me"] = remember_me
    if "active_page" not in st.session_state:
        st.session_state["active_page"] = "overview"


def logout_user() -> None:
    """Clear session-based authentication state and redirect to login."""
    st.session_state["authenticated"] = False
    st.session_state["user_email"] = None
    st.session_state["user_name"] = None
    st.session_state["user_role"] = None
    st.session_state["active_page"] = "overview"
    st.rerun()


def is_authenticated() -> bool:
    """Check if the current user session is authenticated."""
    return st.session_state.get("authenticated", False) is True


def get_current_user() -> Dict[str, Any]:
    """Retrieve current session user information."""
    return {
        "email": st.session_state.get("user_email", "hr@company.com"),
        "name": st.session_state.get("user_name", "HR Admin"),
        "role": st.session_state.get("user_role", "HR Administrator")
    }
