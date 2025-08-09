import streamlit as st
from story_classifier import run as run_story_classifier
from prompt_collector import run_prompt_collector
from meme_generator import run as run_meme_generator
from voice2text import run as run_voice_to_text  # Updated import to voice2text
from offline_chatbot import run as run_offline_chatbot
from meme_gallery import run as run_meme_gallery



st.set_page_config(page_title="All-in-One AI Tools", layout="centered")
st.sidebar.title("📂 App Navigation")

app_choice = st.sidebar.radio(
    "Choose a module",
    [
        "🧠 Values Vault",
        "🎙️ Prompt Collector",
        "🎭 Meme Generator",
        "🎤 Voice to Text",
        "💬 Assistant",
        "🖼️ Meme Gallery" 
    ]
)

if app_choice == "🧠 Values Vault":
    run_story_classifier()
elif app_choice == "🎙️ Prompt Collector":
    run_prompt_collector()
elif app_choice == "🎭 Meme Generator":
    run_meme_generator()
elif app_choice == "🎤 Voice to Text":
    run_voice_to_text()
elif app_choice == "💬 Assistant":
    run_offline_chatbot()
elif app_choice ==  "🖼️ Meme Gallery":
    run_meme_gallery()

