import streamlit as st
import geocoder
from datetime import datetime
import os
import json
import random
import sqlite3

# Define prompt categories
prompt_categories = {
    "Food": [
        "What is your favorite dish? - మీకు ఇష్టమైన వంటకం ఏమిటి?",
        "Do you prefer spicy or sweet? - మీరు కారంగా ఇష్టపడతారా లేదా తీపిగా?",
    ],
    "Culture": [
        "What festival do you celebrate most? - మీరు ఎక్కువగా జరుపుకునే పండుగ ఏమిటి?",
        "Do you follow any traditions at home? - మీ ఇంట్లో ఏవైనా సంప్రదాయాలు పాటిస్తారా?",
    ],
    "Travel": [
        "Where did you go on your last trip? - మీరు గతంలో ఎక్కడికి ప్రయాణించారు?",
        "Do you prefer beaches or hills? - మీరు బీచ్‌లను ఇష్టపడతారా లేక కొండలను?",
    ],
    "Childhood": [
        "What is your favorite childhood memory? - మీకు ఇష్టమైన చిన్ననాటి జ్ఞాపకం ఏమిటి?",
        "Did you enjoy school? - మీకు పాఠశాల నచ్చిందా?",
    ]
}

# Initialize SQLite DB
def init_db():
    conn = sqlite3.connect("responses.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS responses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT,
            swecha_username TEXT,
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

# Insert submission into DB
def insert_response(data):
    conn = sqlite3.connect("responses.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO responses (
            name, email, swecha_username, location,
            category, prompt, mode, text_response, timestamp
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data["name"],
        data["email"],
        data["swecha_username"],
        data["location"],
        data["category"],
        data["prompt"],
        data["mode"],
        data["text_response"],
        data["timestamp"]
    ))
    conn.commit()
    conn.close()

# ---------- Main App ----------
def run_prompt_collector():
    st.title("🎙️ Swecha Summer of AI - Prompt Collector (ప్రాంప్ట్ ఆధారిత డేటా సేకరణ)")

    # Location
    try:
        location_info = geocoder.ip('me')
        location = f"{location_info.city}, {location_info.country}" if location_info.ok else "Unavailable / అందుబాటులో లేదు"
    except:
        location = "Unavailable / అందుబాటులో లేదు"

    st.markdown(f"📍 **Your Location (మీ స్థానం):** `{location}`")

    # User details
    st.subheader("👤 Participant Details (పాల్గొనేవరి వివరాలు)")
    user_name = st.text_input("Full Name (పూర్తి పేరు)")
    user_email = st.text_input("Email Address (ఈమెయిల్)")
    swecha_username = st.text_input("Swecha Username (స్వేచ్చ యూజర్నేమ్)")

    # Prompt selection
    st.subheader("📂 Select a Prompt Category")
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
    st.subheader("🔴 Recording/Typing (రికార్డింగ్ లేదా టైపింగ్)")
    mode = st.radio("Submission Mode (సమర్పణ రకం)", ["Audio", "Video", "Text"])

    text_response = ""
    uploaded_file = None

    if mode == "Text":
        text_response = st.text_area("Write your response here (ఇక్కడ మీ స్పందనను రాయండి)")
    else:
        uploaded_file = st.file_uploader(f"Upload your {mode.lower()} file here", type=["mp3", "wav", "m4a", "mp4", "webm", "mkv"])

    if st.button("✅ Submit (సమర్పించండి)"):
        if not user_name or not user_email or not swecha_username:
            st.error("Please fill all fields. / దయచేసి అన్ని వివరాలను పూరించండి.")
        elif mode in ["Audio", "Video"] and not uploaded_file:
            st.error("Please upload your file. / దయచేసి మీ ఫైల్‌ను అప్‌లోడ్ చేయండి.")
        else:
            submission = {
                "name": user_name,
                "email": user_email,
                "swecha_username": swecha_username,
                "location": location,
                "prompt": prompt,
                "category": selected_category,
                "mode": mode,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "text_response": ""
            }

            # Save file if applicable
            if uploaded_file:
                user_dir = os.path.join("user_uploads", swecha_username)
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

# Run app
if __name__ == "__main__":
    init_db()
    run_prompt_collector()
