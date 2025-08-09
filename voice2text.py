# voice2text.py
import streamlit as st
import speech_recognition as sr
import tempfile

def run():
    st.title("🎤 Telugu Voice to Text")
    st.markdown("Upload a short audio file in Telugu or English to get instant transcription.")

    audio_file = st.file_uploader("📂 Upload your audio file", type=["wav", "mp3", "m4a"])

    if audio_file is not None:
        # Save uploaded audio to a temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp:
            temp.write(audio_file.read())
            temp_path = temp.name

        recognizer = sr.Recognizer()
        with sr.AudioFile(temp_path) as source:
            st.info("Processing your audio...")
            audio_data = recognizer.record(source)

        # Try Telugu first, then English
        try:
            text_te = recognizer.recognize_google(audio_data, language="te-IN")
            if text_te.strip():
                st.success(f"**Telugu transcription:** {text_te}")
            else:
                text_en = recognizer.recognize_google(audio_data, language="en-IN")
                st.success(f"**English transcription:** {text_en}")
        except sr.UnknownValueError:
            st.error("Could not understand the audio.")
        except sr.RequestError:
            st.error("Speech recognition service error.")
