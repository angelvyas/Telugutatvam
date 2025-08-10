import streamlit as st
from datetime import date

# Session state for login
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# ------------------ LOGIN PAGE ------------------
def run_login_page():
    st.title("🔐 Login")

    phone = st.text_input("Phone Number", key="login_phone")
    password = st.text_input("Password", type="password", key="login_password")

    if st.button("Login", key="login_button"):
        # Replace with your real authentication logic
        if phone == "123" and password == "123":
            st.session_state.logged_in = True
            st.success("Login successful ✅")
        else:
            st.error("Invalid phone number or password")

    st.write("---")
    st.write("Don't have an account? Sign up below 👇")
    run_signup_page()

# ------------------ SIGNUP PAGE ------------------
def run_signup_page():
    st.subheader("📝 Sign Up")

    full_name = st.text_input("Full Name", key="signup_full_name")
    phone = st.text_input("Phone Number", key="signup_phone")
    email = st.text_input("Email Address", key="signup_email")
    gender = st.selectbox("Gender", ["Male", "Female", "Other"], key="signup_gender")
    dob = st.date_input("Date of Birth", key="signup_dob", min_value=date(1900, 1, 1))
    place = st.text_input("Place", key="signup_place")
    password = st.text_input("Create Password", type="password", key="signup_password")
    confirm_password = st.text_input("Confirm Password", type="password", key="signup_confirm_password")
    tos = st.checkbox("I agree to the Terms of Service and Privacy Policy", key="signup_tos")

    if st.button("Sign Up", key="signup_button"):
        if not tos:
            st.error("You must agree to the Terms of Service to continue.")
        elif password != confirm_password:
            st.error("Passwords do not match.")
        else:
            st.success("Signup successful! 🎉")
            # Save to DB here

# ------------------ APP PAGES ------------------
def meme_generator():
    st.title("🎭 Meme Generator")
    st.write("Your meme generator code here...")

def leaderboard():
    st.title("🏆 Meme Leaderboard")
    st.write("Your leaderboard code here...")

def chatbot():
    st.title("💬 AI Chatbot")
    st.write("Your chatbot code here...")

# ------------------ MAIN APP FLOW ------------------
if not st.session_state.logged_in:
    run_login_page()
else:
    menu = ["Meme Generator", "Leaderboard", "Chatbot"]
    choice = st.sidebar.selectbox("Navigate", menu)

    if choice == "Meme Generator":
        meme_generator()
    elif choice == "Leaderboard":
        leaderboard()
    elif choice == "Chatbot":
        chatbot()
