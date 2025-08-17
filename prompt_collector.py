import streamlit as st
import geocoder
from datetime import datetime
import os
import random
import sqlite3

# ======== Prompt Categories & Questions ========
prompt_categories = {
    "People": [
        "Describe an inspiring person you know.",
        "Who is your role model and why?"
    ],
    "Events": [
        "What was the most memorable event you attended?",
        "Describe a festival unique to your culture."
    ],
    "Music": [
        "What type of music do you enjoy the most?",
        "Describe a song that moves you deeply."
    ],
    "Places": [
        "What is your favorite place to visit?",
        "Describe a place in your town that has historical significance."
    ],
    "Food": [
        "What is your favorite dish? - మీకు ఇష్టమైన వంటకం ఏమిటి?",
        "Do you prefer spicy or sweet? - మీరు కారంగా ఇష్టపడతారా లేదా తీపిగా?"
    ],
    "People": [
        "Describe a person who made a difference in your life.",
        "Who inspires you and why?"
    ],
    "Literature": [
        "Who is your favorite author or poet?",
        "What book changed your perspective?"
    ],
    "Architecture": [
        "Describe an architectural landmark you like.",
        "What building style is common in your area?"
    ],
    "Skills": [
        "What skill are you proud of?",
        "What new skill would you like to learn?"
    ],
    "Images": [
        "Describe a picture that you cherish.",
        "What kind of images inspire you?"
    ],
    "Culture": [
        "What festival do you celebrate most? - మీరు ఎక్కువగా జరుపుకునే పండుగ ఏమిటి?",
        "Do you follow any traditions at home? - మీ ఇంట్లో ఏవైనా సంప్రదాయాలు పాటిస్తారా?"
    ],
    "Flora & Fauna": [
        "What plants or animals are common around your home?",
        "Do you have a favorite tree, flower, or animal?"
    ],
    "Education": [
        "What is your favorite subject in school?",
        "Describe an inspiring teacher."
    ],
    "Vegetation": [
        "What plants grow around your home?",
        "Do you have a favorite tree or flower?"
    ],
    "Folk Tales": [
        "Share a folk tale from your region.",
        "What lessons do folk tales teach us?"
    ],
    "Folk Songs": [
        "Share a folk song from your culture.",
        "Do you know the meaning of any folk songs?"
    ],
    "Traditional Skills": [
        "What traditional skill do you know?",
        "Describe a traditional craft or art from your region."
    ],
    "Local Cultural History": [
        "Describe a local cultural festival.",
        "What traditions are unique to your community?"
    ],
    "Local History": [
        "What is an interesting fact about your town’s history?",
        "Describe a historical event that shaped your community."
    ],
    "Food & Agriculture": [
        "Describe a traditional farming practice.",
        "What local foods are special in your area?"
    ],
    "Newspapers Older Than 1980s": [
        "Have you seen old newspapers? What stood out?",
        "How did newspapers influence people in older times?"
    ]
}

# ======== SQLite DB ========
def init_db():
    conn = sqlite3.connect("responses.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS responses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            location TEXT,
            category TEXT,
            prompt TEXT,
            mode TEXT,
            text_response TEXT,
            timestamp TEXT
        )
    """)
    conn.commit()
    conn.close()

def insert_response(data):
    conn = sqlite3.connect("responses.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO responses (
            location,
            category,
            prompt,
            mode,
            text_response,
            timestamp
        ) VALUES (?, ?, ?, ?, ?, ?)
    """, (
        data["location"],
        data["category"],
        data["prompt"],
        data["mode"],
        data["text_response"],
        data["timestamp"]
    ))
    conn.commit()
    conn.close()

# ======== Main App ========
def run_prompt_collector():
    st.title("🎙️ Choose a category to contribute content")

    # Location detection
    try:
        location_info = geocoder.ip('me')
        location = f"{location_info.city}, {location_info.country}" if location_info.ok else "Unavailable"
    except:
        location = "Unavailable"

    st.markdown(f"📍 **Your Location:** `{location}`")

    # Prompt selection
    st.subheader("📂 Select a Category")
    selected_category = st.selectbox("Choose a category", list(prompt_categories.keys()))
    if 'prompt_index' not in st.session_state:
        st.session_state.prompt_index = 0

    prompt_list = prompt_categories[selected_category]
    prompt = prompt_list[st.session_state.prompt_index]
    st.subheader("📝 Prompt")
    st.markdown(f"**{prompt}**")

    if st.button("🔄 Refresh Question"):
        st.session_state.prompt_index = random.randint(0, len(prompt_list) - 1)
        st.rerun()

    # Submission Mode
    st.subheader("🔴 Recording/Typing")
    mode = st.radio("Submission Mode", ["Audio", "Video", "Text"])

    text_response = ""
    uploaded_file = None

    if mode == "Text":
        text_response = st.text_area("Write your response here")
    else:
        uploaded_file = st.file_uploader(f"Upload your {mode.lower()} file here", type=["mp3", "wav", "m4a", "mp4", "webm", "mkv"])

    if st.button("✅ Submit"):
        if mode in ["Audio", "Video"] and not uploaded_file:
            st.error("Please upload your file.")
        elif mode == "Text" and not text_response.strip():
            st.error("Please write your response.")
        else:
            submission = {
                "location": location,
                "prompt": prompt,
                "category": selected_category,
                "mode": mode,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "text_response": ""
            }

            # Save uploaded file if any
            if uploaded_file:
                user_dir = os.path.join("user_uploads")
                os.makedirs(user_dir, exist_ok=True)

                file_ext = uploaded_file.name.split('.')[-1]
                filename = f"{mode}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{file_ext}"
                file_path = os.path.join(user_dir, filename)

                with open(file_path, "wb") as f:
                    f.write(uploaded_file.read())

                submission["text_response"] = f"File uploaded: {file_path}"
            elif mode == "Text":
                submission["text_response"] = text_response

            insert_response(submission)
            st.success("✅ Submitted successfully!")

# ======== Run App ========
if __name__ == "__main__":
    init_db()
    run_prompt_collector()
