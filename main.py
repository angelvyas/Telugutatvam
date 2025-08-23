import streamlit as st
import requests

# Must be the very first Streamlit command
st.set_page_config(page_title="Telugu Tatvam", layout="centered")

from meme_generator import run as run_meme_generator
from prompt_collector import run_prompt_collector
from story_classifier import run as run_story_classifier
from voice2text import run as run_voice_to_text
from offline_chatbot import run as run_offline_chatbot
from meme_gallery import run as run_meme_gallery

API_BASE = "https://api.corpus.swecha.org/api/v1"
REQ_TIMEOUT = 15  # seconds

st.session_state.logged_in = True
st.session_state.auth_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NTYwMTgwODQsInN1YiI6IjZlYWI4NGI2LTY5OWMtNDY1NC05NDVmLTgyNGViNzc4YmZmMiJ9._vTfO0eJGCQ8qKvEMO11VnUgcasPRxFfmVh69hvZbUM"
st.success("Login successful! 🎉")

# ---------------- Session defaults ----------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "auth_token" not in st.session_state:
    st.session_state.auth_token = None
if "user" not in st.session_state:
    st.session_state.user = None
if "categories" not in st.session_state:
    st.session_state.categories = []

# ---------------- Small helpers ----------------
def _auth_headers():
    token = st.session_state.get("auth_token")
    return {"Authorization": f"Bearer {token}"} if token else {}

def _nice_error(resp):
    try:
        j = resp.json()
        msg = j.get("detail") or j.get("message") or j
    except Exception:
        msg = resp.text
    return f"{resp.status_code}: {msg}"

# ---------------- API CALLS ----------------
def signup_user(name, phone, email, gender, dob, place, password, has_given_consent):
    payload = {
        "phone": phone,
        "name": name,
        "email": email,
        "gender": gender,
        "date_of_birth": dob.isoformat(),
        "place": place,
        "password": password,
        "role_ids": [2],
        "has_given_consent": has_given_consent,
    }
    return requests.post(f"{API_BASE}/users", json=payload, timeout=REQ_TIMEOUT)

def login_user(phone, password):
    payload = {"phone": phone, "password": password}
    return requests.post(f"{API_BASE}/auth/login", json=payload, timeout=REQ_TIMEOUT)

def get_current_user():
    try:
        resp = requests.get(f"{API_BASE}/auth/me", headers=_auth_headers(), timeout=REQ_TIMEOUT)
        if resp.status_code == 200:
            return resp.json()
        else:
            st.error(f"Failed to fetch user: {_nice_error(resp)}")
            return []
    except requests.RequestException as e:
        st.error(f"Network error while fetching current user: {e}")
        return []  

def get_categories():
    try:
        resp = requests.get(f"{API_BASE}/categories/", headers=_auth_headers(), timeout=REQ_TIMEOUT)
        if resp.status_code == 200:
            return resp.json()
        else:
            st.error(f"Failed to fetch categories: {_nice_error(resp)}")
            return []
    except requests.RequestException as e:
        st.error(f"Network error while fetching categories: {e}")
        return []

# ---------------- AUTH UI ----------------
def run_auth_box():
    style = """
    <style>
    .reportview-container { background: linear-gradient(135deg, #00c6ff, #0072ff); height: 100vh;
        display: flex; flex-direction: column; align-items: center; justify-content: center;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
    .welcome-text { font-size: 3rem; font-weight: 700; color: white; margin-bottom: 30px;
        user-select: none; text-align: center; text-shadow: 1px 1px 5px rgba(0,0,0,0.4); }
    .auth-box { background: white; border-radius: 10px; padding: 40px 50px; max-width: 400px; width: 100%;
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.15); }
    .powered { margin-top: 25px; font-size: 13px; color: #e0e0e0; user-select: none;
        font-family: monospace; text-align: center; text-shadow: 0 0 3px rgba(0,0,0,0.3); }
    a { color: #0072ff !important; text-decoration: none; } a:hover { text-decoration: underline; }
    </style>
    """
    st.markdown(style, unsafe_allow_html=True)
    st.markdown('<div class="welcome-text">Welcome</div>', unsafe_allow_html=True)
    # st.markdown('<div class="auth-box">', unsafe_allow_html=True)

    choice = st.radio("", ["Login", "Register"], horizontal=True, key="auth_choice")

    if choice == "Login":
        phone = st.text_input("Phone Number", key="login_phone")
        password = st.text_input("Password", type="password", key="login_password")

        if st.button("Login", key="login_button"):
            try:
                resp = login_user(phone, password)
                if resp.status_code == 200:
                    data = resp.json()
                    token = data.get("access_token")
                    if token:
                        st.session_state.logged_in = True
                        st.session_state.auth_token = token
                        st.success("Login successful! 🎉")
                        st.rerun()
                    else:
                        st.error("Login failed: No token returned.")
                else:
                    st.error(f"Login failed: {_nice_error(resp)}")
            except requests.RequestException as e:
                st.error(f"Network error: {e}")

    else:  # Signup
        full_name = st.text_input("Full Name", key="signup_full_name")
        phone = st.text_input("Phone Number", key="signup_phone")
        email = st.text_input("Email Address", key="signup_email")
        gender = st.selectbox("Gender", ["Male", "Female", "Other"], key="signup_gender")
        dob = st.date_input("Date of Birth", key="signup_dob")
        place = st.text_input("Place", key="signup_place")
        password = st.text_input("Create Password", type="password", key="signup_password")
        confirm_password = st.text_input("Confirm Password", type="password", key="signup_confirm_password")
        tos = st.checkbox("I agree to the Terms of Service and Privacy Policy", key="signup_tos")

        if st.button("Create Account", key="signup_button"):
            if not tos:
                st.error("You must agree to the Terms of Service to continue.")
            elif password != confirm_password:
                st.error("Passwords do not match.")
            else:
                try:
                    resp = signup_user(full_name, phone, email, gender, dob, place, password, tos)
                    if resp.status_code in (200, 201):
                        st.success("Signup successful! Please log in.")
                    else:
                        st.error(f"Signup failed: {_nice_error(resp)}")
                except requests.RequestException as e:
                    st.error(f"Network error: {e}")

    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('<div class="powered">Powered by Swecha</div>', unsafe_allow_html=True)

# ---------------- DASHBOARD ----------------
def run_dashboard():
    st.sidebar.title("Navigation")
    choice = st.sidebar.radio(
        "Go to",
        [
            "🧠 Values Vault",
            "🎙️ Prompt Collector",
            "🎭 Meme Generator",
            "🎤 Voice to Text",
            "💬 Assistant",
            "🖼️ Meme Gallery",
        ],
    )

    if choice == "🎭 Meme Generator":
        run_meme_generator()
    elif choice == "🧠 Values Vault":
        run_story_classifier()
    elif choice == "🎙️ Prompt Collector":
        run_prompt_collector()
    
    elif choice == "🎤 Voice to Text":
        run_voice_to_text()
    elif choice == "💬 Assistant":
        run_offline_chatbot()
    elif choice == "🖼️ Meme Gallery":
        run_meme_gallery()

    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.pop("auth_token", None)
        st.session_state.pop("user", None)
        st.session_state.pop("categories", None)
        st.rerun()

# ---------------- MAIN APP ----------------



if st.session_state.logged_in:
    st.session_state.categories = get_categories()
    st.session_state.user = get_current_user()
    run_dashboard()
    #run_prompt_collector()
else:
    run_auth_box()
