import streamlit as st
from transformers import pipeline
import requests
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

# ===== API CONFIG =====
API_BASE_URL = "https://api.corpus.swecha.org/api/v1"

# Ensure token is set
if "auth_token" not in st.session_state:
    st.session_state["auth_token"] = "YOUR_REAL_BEARER_TOKEN"

BEARER_TOKEN = st.session_state["auth_token"]
headers = {
    "Authorization": f"Bearer {BEARER_TOKEN}",
    "Content-Type": "application/json"
}

def create_record(
    title,
    media_type,
    user_id,
    category_id,
    file_url=None,
    file_name=None,
    file_size=None,
    description=None,
    status="pending",
    location=None
):
    payload = {
        "title": title,
        "description": description,
        "media_type": media_type,
        "file_url": file_url,
        "file_name": file_name,
        "file_size": file_size,
        "status": status,
        "location": location or {"latitude": 17.385, "longitude": 78.4867},
        "reviewed": False,
        "reviewed_by": None,
        "reviewed_at": None,
        "user_id": user_id,
        "category_id": category_id
    }
    response = requests.post(f"{API_BASE_URL}/records/", headers=headers, json=payload)
    if response.status_code in (200, 201):
        return response.json()
    else:
        st.error(f"Error {response.status_code}: {response.text}")
        return None

# ===== LOAD CLASSIFIER =====
@st.cache_resource
def load_classifier():
    return pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

# ===== CATEGORY MAPPING =====
CATEGORY_MAP = {
    "Fables": "UUID_FOR_FABLES",
    "Events": "UUID_FOR_EVENTS",
    "Music": "UUID_FOR_MUSIC",
    "Places": "UUID_FOR_PLACES",
    "Food": "UUID_FOR_FOOD",
    "People": "UUID_FOR_PEOPLE",
    "Literature": "UUID_FOR_LITERATURE",
    "Architecture": "UUID_FOR_ARCHITECTURE",
    "Skills": "UUID_FOR_SKILLS",
    "Images": "UUID_FOR_IMAGES",
    "Culture": "UUID_FOR_CULTURE",
    "Flora & Fauna": "UUID_FOR_FLORA_FAUNA",
    "Education": "UUID_FOR_EDUCATION",
    "Vegetation": "UUID_FOR_VEGETATION",
    "Folk Tales": "UUID_FOR_FOLK_TALES",
    "Folk Songs": "UUID_FOR_FOLK_SONGS",
    "Traditional Skills": "UUID_FOR_TRADITIONAL_SKILLS",
    "Local Cultural History": "UUID_FOR_LOCAL_CULTURE",
    "Local History": "UUID_FOR_LOCAL_HISTORY",
    "Food & Agriculture": "UUID_FOR_FOOD_AGRI",
    "Newspapers Older Than 1980s": "UUID_FOR_NEWSPAPERS"
}

CATEGORIES = list(CATEGORY_MAP.keys())

# ===== MAIN APP =====
def run():
    init_db()
    classifier = load_classifier()
    values = ["Honesty", "Kindness", "Respect", "Responsibility", "Courage", 
              "Empathy", "Forgiveness", "Perseverance", "Gratitude"]

    st.title("🧠 Values Vault – Personality Development Story Collector")

    # ===== CATEGORY SELECTION =====
    selected_category = st.selectbox("Select Category for your Story", CATEGORIES)
    category_id = CATEGORY_MAP[selected_category]

    story = st.text_area("✏️ Share a short story that taught you a life lesson:", height=150)

    if st.button("Submit Story"):
        if story.strip():
            with st.spinner("Classifying story..."):
                result = classifier(story, values)
                predicted_value = result['labels'][0]

            selected_value = st.selectbox(
                "💡 Suggested Value (you can change if needed):",
                values,
                index=values.index(predicted_value)
            )

            st.success("✅ Story Submitted!")
            st.markdown(f"📖 **Your Story:** {story}")
            st.markdown(f"🏷️ **Tagged Value:** {selected_value}")

            # ===== LOCAL LOGGING =====
            submission = {
                "location": "Unavailable",
                "category": selected_category,
                "prompt": f"Story: {selected_value}",
                "mode": "Text",
                "text_response": story,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            insert_response(submission)
            st.info(f"📝 Logged locally under category **{selected_category}**")

            # ===== UPLOAD TO API =====
            user_id = st.session_state.get("user", {}).get("id", "DEFAULT_USER_ID")
            api_response = create_record(
                title=f"Story: {selected_value}",
                media_type="text",
                user_id=user_id,
                category_id=category_id,
                description=story
            )
            if api_response:
                st.success("✅ Story uploaded to API successfully!")
        else:
            st.warning("Please write a story before submitting.")
