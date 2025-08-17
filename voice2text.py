import streamlit as st
import speech_recognition as sr
import tempfile
import os
from pydub import AudioSegment
import sqlite3
from datetime import datetime

# ===== LOCAL DB =====
DB_PATH = "responses.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
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
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO responses (
            location, category, prompt, mode, text_response, timestamp
        ) VALUES (?, ?, ?, ?, ?, ?)
    """, (data["location"], data["category"], data["prompt"], data["mode"], data["text_response"], data["timestamp"]))
    conn.commit()
    conn.close()

# ===== CATEGORY LIST =====
CATEGORIES = [
    "Fables", "Events", "Music", "Places", "Food", "People", "Literature",
    "Architecture", "Skills", "Images", "Culture", "Flora & Fauna",
    "Education", "Vegetation", "Folk Tales", "Folk Songs",
    "Traditional Skills", "Local Cultural History", "Local History",
    "Food & Agriculture", "Newspapers Older Than 1980s"
]

# ===== VOICE TO TEXT =====
def run():
    init_db()
    st.title("🎤 Telugu Voice to Text")
    st.markdown("Upload a short audio file in Telugu or English to get instant transcription.")

    selected_category = st.selectbox("Select Category for your Audio", CATEGORIES)

    audio_file = st.file_uploader("📂 Upload your audio file", type=["wav", "mp3", "m4a"])

    if audio_file is not None:
        # Convert to WAV if necessary
        temp_wav_path = tempfile.NamedTemporaryFile(delete=False, suffix=".wav").name
        file_ext = audio_file.name.split(".")[-1].lower()
        if file_ext in ["mp3", "m4a"]:
            audio = AudioSegment.from_file(audio_file)
            audio.export(temp_wav_path, format="wav")
        else:
            with open(temp_wav_path, "wb") as f:
                f.write(audio_file.read())

        recognizer = sr.Recognizer()
        with sr.AudioFile(temp_wav_path) as source:
            st.info("Processing your audio...")
            audio_data = recognizer.record(source)

        transcription = ""
        try:
            transcription = recognizer.recognize_google(audio_data, language="te-IN")
            if not transcription.strip():
                transcription = recognizer.recognize_google(audio_data, language="en-IN")
        except sr.UnknownValueError:
            st.error("Could not understand the audio.")
            return
        except sr.RequestError:
            st.error("Speech recognition service error.")
            return

        st.success(f"**Transcription:** {transcription}")

        # ===== Upload Button =====
        if st.button("✅ Upload Transcription"):
            from datetime import datetime
            submission = {
                "location": "Unavailable",
                "category": selected_category,
                "prompt": f"Audio: {audio_file.name}",
                "mode": "Audio",
                "text_response": transcription,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            insert_response(submission)
            st.success(f"✅ Audio logged locally under category **{selected_category}**!")

            st.info("You can now upload to API if needed (replace URL logic here).")
