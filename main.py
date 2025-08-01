# main_app.py
import streamlit as st
from story_classifier import run as run_story_classifier
from prompt_collector import run_prompt_collector


st.set_page_config(page_title="All-in-One AI Tools", layout="centered")
st.sidebar.title("📂 App Navigation")
app_choice = st.sidebar.radio("Choose a module", ["🧠 Values Vault", "🎙️ Prompt Collector"])

if app_choice == "🧠 Values Vault":
    run_story_classifier()
else:
    run_prompt_collector()
