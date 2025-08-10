import streamlit as st

# Must be the very first Streamlit command
st.set_page_config(page_title="Telugu Tatvam", layout="centered")

from meme_generator import run as run_meme_generator
from prompt_collector import run_prompt_collector
from story_classifier import run as run_story_classifier
from voice2text import run as run_voice_to_text
from offline_chatbot import run as run_offline_chatbot
from meme_gallery import run as run_meme_gallery

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

def run_auth_box():
    # Styling for gradient background and white box for form only
    style = """
    <style>
    /* Full page gradient background */
    .reportview-container {
        background: linear-gradient(135deg, #00c6ff, #0072ff);
        height: 100vh;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    /* Welcome text - outside the box, transparent bg */
    .welcome-text {
        font-size: 3rem;
        font-weight: 700;
        color: white;
        margin-bottom: 30px;
        user-select: none;
        text-align: center;
        text-shadow: 1px 1px 5px rgba(0,0,0,0.4);
    }
    /* Auth box - white background, subtle shadow */
    .auth-box {
        background: white;
        border-radius: 10px;
        padding: 40px 50px;
        max-width: 400px;
        width: 100%;
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.15);
    }
    /* Powered by text below the box */
    .powered {
        margin-top: 25px;
        font-size: 13px;
        color: #e0e0e0;
        user-select: none;
        font-family: monospace;
        text-align: center;
        text-shadow: 0 0 3px rgba(0,0,0,0.3);
    }
    /* Style links */
    a {
        color: #0072ff !important;
        text-decoration: none;
    }
    a:hover {
        text-decoration: underline;
    }
    </style>
    """
    st.markdown(style, unsafe_allow_html=True)

    st.markdown('<div class="welcome-text">Welcome</div>', unsafe_allow_html=True)
    st.markdown('<div class="auth-box">', unsafe_allow_html=True)

    choice = st.radio("", ["Login", "Signup"], horizontal=True, key="auth_choice")

    if choice == "Login":
        phone = st.text_input("Phone Number", key="login_phone")
        password = st.text_input("Password", type="password", key="login_password")

        st.markdown('<div style="text-align:right; margin-top:-10px; margin-bottom:15px;"><a href="#">Forgot password?</a></div>', unsafe_allow_html=True)

        if st.button("Login", key="login_button"):
            # Replace with your real auth logic
            if phone == "123" and password == "pass":
                st.session_state.logged_in = True
                st.success("Login successful! 🎉")
                st.rerun()
            else:
                st.error("Invalid phone number or password")

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
                st.success("Signup successful! 🎉")
                # Add user registration logic here

    st.markdown('</div>', unsafe_allow_html=True)  # Close auth-box

    st.markdown('<div class="powered">Powered by Swecha</div>', unsafe_allow_html=True)

def run_dashboard():
    st.sidebar.title("Navigation")
    choice = st.sidebar.radio("Go to", [
        "🧠 Values Vault",
        "🎙️ Prompt Collector",
        "🎭 Meme Generator",
        "🎤 Voice to Text",
        "💬 Assistant",
        "🖼️ Meme Gallery"
    ])

    if choice == "🧠 Values Vault":
        run_story_classifier()
    elif choice == "🎙️ Prompt Collector":
        run_prompt_collector()
    elif choice == "🎭 Meme Generator":
        run_meme_generator()
    elif choice == "🎤 Voice to Text":
        run_voice_to_text()
    elif choice == "💬 Assistant":
        run_offline_chatbot()
    elif choice == "🖼️ Meme Gallery":
        run_meme_gallery()

    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

if st.session_state.logged_in:
    run_dashboard()
else:
    run_auth_box()
