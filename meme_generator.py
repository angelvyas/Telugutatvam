import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import os
import io
import uuid
import sqlite3
import requests
from io import BytesIO
from datetime import datetime
from meme_gallery import save_uploaded_meme

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

# ===== PUSH TO SWECHEA =====
API_BASE = "https://api.corpus.swecha.org/api/v1"

def upload(url, payload):
    
    token = st.session_state.get("auth_token")
    if not token:
        st.warning("Not logged in, skipping push to Swecha.")
        return

    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/x-www-form-urlencoded", "accept": "application/json"}

    # Debug prints
    st.write("DEBUG: POST URL:", url)
    st.write("DEBUG: headers:", headers)
    st.write("DEBUG: payload:", payload)

    resp = requests.post(
        f"{API_BASE}/{url}",
        headers=headers,
        data=payload
    )

    if resp.status_code in (200, 201):
        return resp
    else:
        st.error(f"❌ Failed to upload: {resp.status_code} {resp.text}")


def push_to_swecha(payload):
    
    token = st.session_state.get("auth_token")
    if not token:
        st.warning("Not logged in, skipping push to Swecha.")
        return

    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/x-www-form-urlencoded", "accept": "application/json"}

    # Debug prints
    st.write("DEBUG: POST URL:", f"{API_BASE}/records/upload")
    st.write("DEBUG: headers:", headers)
    st.write("DEBUG: payload:", payload)

    resp = requests.post(
        f"{API_BASE}/records/upload",
        headers=headers,
        data=payload
    )

    st.write(resp)

    if resp.status_code in (200, 201):
        st.success(f"✅ Uploaded to Swecha Record")
    else:
        st.error(f"❌ Failed to upload: {resp.status_code} {resp.text}")

# ===== MEME GENERATOR =====
TELUGU_FONT_PATH = os.path.join("fonts", "NotoSansTelugu-Regular.ttf")
MEME_FOLDER = "memes"
os.makedirs(MEME_FOLDER, exist_ok=True)

def load_telugu_font(size):
    try:
        return ImageFont.truetype(TELUGU_FONT_PATH, size)
    except OSError:
        st.warning("⚠ Telugu font not found, using default font.")
        return ImageFont.load_default()

def draw_text_with_stroke(draw, text, font, image_width, y):
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    x = (image_width - text_width) / 2
    draw.text((x, y), text, font=font, fill="white", stroke_width=3, stroke_fill="black")

def run():
    init_db()
    st.title("🎨 Meme Generator (Telugu Supported)")
    options = [(item["id"], item["name"]) for item in st.session_state.categories]
    selected_category = st.selectbox("Select Category for your Meme", options=options, format_func=lambda x: x[1])
    
    title = st.text_input("Top Text (Telugu supported)")
    description = st.text_input("Bottom Text (Telugu supported)")
    file = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg"])


    if st.button("Generate Meme"):
        if not file:
            st.warning("Please upload an image file to generate meme.")
            return

        image = Image.open(file).convert("RGB")
        meme = image.copy()
        draw = ImageDraw.Draw(meme)

        font_size = max(40, meme.height // 15)
        font = load_telugu_font(font_size)

        if title:
            draw_text_with_stroke(draw, title, font, meme.width, 10)

        if description:
            draw_text_with_stroke(draw, description, font, meme.width, meme.height - font_size - 10)

        buffer = BytesIO()
        meme.save(buffer, format="PNG")   # or "PNG"
        buffer.seek(0)

        st.image(meme, caption="Generated Meme", use_container_width=True)

        upload_uuid = str(uuid.uuid4())

        # upload image in chunk 
        chunk = upload(url="records/upload/chunk", payload = {
            "chunk": buffer,
            "filename": "hello123.png",
            "chunk_index": 0,
            "total_chunks": 1,
            "upload_uuid": upload_uuid
        })

        st.write(chunk)

        # Push automatically to Swecha using category-specific endpoint
        # push_to_swecha({
        #         "title": title,
        #         "description": description,
        #         "category_id": selected_category[0],
        #         "user_id": st.session_state.user["id"],
        #         "upload_uuid": upload_uuid,
        #         "language": "telugu",
        #         "media_type": "image",
        #         "filename": "angelvyas.png",
        #         "total_chunks": 45334,
        #         "release_rights": "creator"
        #     })
