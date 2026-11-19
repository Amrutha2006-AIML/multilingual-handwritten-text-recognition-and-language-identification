import hashlib
import json
import os
import re
import secrets
from datetime import datetime
from typing import Dict, Optional, Tuple

import streamlit as st

EMAIL_REGEX = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")


def _users_file_path() -> str:
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out_dir = os.path.join(base_dir, "htr_app", "htr_outputs")
    os.makedirs(out_dir, exist_ok=True)
    return os.path.join(out_dir, "users_db.json")


def _load_users() -> Dict[str, dict]:
    path = _users_file_path()
    if not os.path.exists(path):
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def _save_users(users: Dict[str, dict]) -> None:
    path = _users_file_path()
    with open(path, "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=2)


def _hash_password(password: str, salt_hex: Optional[str] = None) -> Tuple[str, str]:
    salt = bytes.fromhex(salt_hex) if salt_hex else secrets.token_bytes(16)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 120_000)
    return salt.hex(), dk.hex()


def make_user_id(email: str) -> str:
    return hashlib.sha256(email.strip().lower().encode("utf-8")).hexdigest()[:8]


def register_user(
    first_name: str, last_name: str, email: str, password: str
) -> Tuple[bool, str, Optional[dict]]:
    fn = first_name.strip()
    ln = last_name.strip()
    full_name = f"{fn} {ln}".strip()
    email_clean = email.strip().lower()

    if not EMAIL_REGEX.match(email_clean):
        return False, "Please enter a valid email address.", None
    if len(password) < 6:
        return False, "Password must be at least 6 characters long.", None
    if len(fn) < 1 or len(ln) < 1:
        return False, "Please enter both your first name and last name.", None

    users = _load_users()
    if email_clean in users:
        return False, "An account with this email already exists. Please sign in instead.", None

    salt_hex, hash_hex = _hash_password(password)
    user_record = {
        "user_id": make_user_id(email_clean),
        "first_name": fn,
        "last_name": ln,
        "name": full_name,
        "email": email_clean,
        "salt": salt_hex,
        "password_hash": hash_hex,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "settings": {
            "default_target_lang": "English",
            "review_threshold": 80,
            "translation_beams": 1,
        },
    }
    users[email_clean] = user_record
    _save_users(users)
    return True, "Account created successfully.", user_record


def update_user_profile(
    email: str, first_name: str, last_name: str, settings: dict
) -> Optional[dict]:
    email_clean = email.strip().lower()
    users = _load_users()
    record = users.get(email_clean)
    if not record:
        return None
    fn = first_name.strip()
    ln = last_name.strip()
    record["first_name"] = fn
    record["last_name"] = ln
    record["name"] = f"{fn} {ln}".strip()
    record["settings"] = settings
    users[email_clean] = record
    _save_users(users)
    return record


def authenticate_user(email: str, password: str) -> Tuple[bool, str, Optional[dict]]:
    email_clean = email.strip().lower()
    if not EMAIL_REGEX.match(email_clean):
        return False, "Please enter a valid email address.", None
    if not password:
        return False, "Please enter your password.", None

    users = _load_users()
    record = users.get(email_clean)
    if not record:
        return False, "No account found with this email. Please register first.", None

    _, check_hash = _hash_password(password, salt_hex=record.get("salt"))
    if not secrets.compare_digest(check_hash, record.get("password_hash", "")):
        return False, "Incorrect password. Please try again.", None

    if "settings" not in record:
        record["settings"] = {
            "default_target_lang": "English",
            "review_threshold": 80,
            "translation_beams": 1,
        }
    return True, "Signed in successfully.", record


def render_auth_page() -> None:
    """Render Transkribus-style Sign In / Register page."""
    if "auth_mode" not in st.session_state:
        st.session_state.auth_mode = "login"

    st.markdown(
        '<div class="sb-auth-brand">'
        '<svg width="36" height="36" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">'
        '<path d="M20.71 4.04C21.1 3.65 21.1 3 20.71 2.63L18.37 0.29C18 -0.1 17.35 -0.1 16.96 0.29L15 2.25L18.75 6M17.75 7L14 3.25L4 13.25V17H7.75L17.75 7Z" fill="#142952"/>'
        '<path d="M2 20H22V22H2V20Z" fill="#142952"/>'
        '</svg>'
        '<span class="sb-auth-brand-title">ScriptBridge</span>'
        '</div>',
        unsafe_allow_html=True,
    )

    _, center_col, _ = st.columns([1.25, 1.5, 1.25])
    with center_col:
        with st.container(border=True):
            if st.session_state.auth_mode == "login":
                st.markdown('<div class="sb-auth-heading">Sign in to your account</div>', unsafe_allow_html=True)

                with st.form("login_form", clear_on_submit=False):
                    login_email = st.text_input("Email", placeholder="you@example.com")
                    login_pass = st.text_input("Password", type="password", placeholder="••••••••")
                    st.checkbox("Remember me", value=True)
                    login_submit = st.form_submit_button("Sign In", type="primary", use_container_width=True)

                if login_submit:
                    ok, msg, user_rec = authenticate_user(login_email, login_pass)
                    if ok and user_rec:
                        st.session_state.auth_user = user_rec
                        st.rerun()
                    else:
                        st.error(msg)

                st.markdown('<div class="sb-auth-footer">New user?</div>', unsafe_allow_html=True)
                if st.button("Register", use_container_width=True):
                    st.session_state.auth_mode = "register"
                    st.rerun()

            else:
                st.markdown('<div class="sb-auth-heading">Create your free ScriptBridge account.</div>', unsafe_allow_html=True)
                st.markdown('<div class="sb-auth-sub">Unlocking Devanagari manuscripts together.</div>', unsafe_allow_html=True)

                with st.form("signup_form", clear_on_submit=False):
                    reg_email = st.text_input("Email", placeholder="you@example.com")
                    reg_pass = st.text_input("Password", type="password", placeholder="Minimum 6 characters")
                    reg_first = st.text_input("First name", placeholder="Amrutha")
                    reg_last = st.text_input("Last name", placeholder="Dasari")
                    reg_submit = st.form_submit_button("Register", type="primary", use_container_width=True)

                if reg_submit:
                    ok, msg, user_rec = register_user(reg_first, reg_last, reg_email, reg_pass)
                    if ok and user_rec:
                        st.session_state.auth_user = user_rec
                        st.rerun()
                    else:
                        st.error(msg)

                st.markdown('<div class="sb-auth-footer">Already have an account?</div>', unsafe_allow_html=True)
                if st.button("« Back to Login", use_container_width=True):
                    st.session_state.auth_mode = "login"
                    st.rerun()