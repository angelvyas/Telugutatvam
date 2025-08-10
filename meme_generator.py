import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import os
import io
import requests
from meme_gallery import save_uploaded_meme

# ===== API CONFIG =====
API_BASE_URL = "https://api.corpus.swecha.org/api/v1"  # Correct base URL
BEARER_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NTQ5MjA0ODUsInN1YiI6IjZlYWI4NGI2LTY5OWMtNDY1NC05NDVmLTgyNGViNzc4YmZmMiJ9.ijdfyhPmhqrZR1tCtqcnB1Df1G4RzhzkTSxKqTMdavE"  # Replace with your real token
USER_ID = "3fa85f64-5717-4562-b3fc-2c963f66afa6"       # Replace with real UUID
CATEGORY_ID = "3fa85f64-5717-4562-b3fc-2c963f66afa6"   # Replace with real UUID

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
    # Add trailing slash to avoid 404
    response = requests.post(f"{API_BASE_URL}/records/", headers=headers, json=payload)
    if response.status_code in (200, 201):
        return response.json()
    else:
        st.error(f"Error {response.status_code}: {response.text}")
        return None

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
    st.title("🎨 Meme Generator (Telugu Supported)")

    top_text = st.text_input("Top Text (Telugu supported)")
    bottom_text = st.text_input("Bottom Text (Telugu supported)")
    uploaded_file = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg"])

    if st.button("Generate Meme"):
        if not uploaded_file:
            st.warning("Please upload an image file to generate meme.")
            return

        image = Image.open(uploaded_file).convert("RGB")
        meme = image.copy()
        draw = ImageDraw.Draw(meme)

        font_size = max(40, meme.height // 15)
        font = load_telugu_font(font_size)

        if top_text:
            draw_text_with_stroke(draw, top_text, font, meme.width, 10)
        if bottom_text:
            draw_text_with_stroke(draw, bottom_text, font, meme.width, meme.height - font_size - 10)

        st.image(meme, caption="Generated Meme", use_container_width=True)

        buffer = io.BytesIO()
        meme.save(buffer, format="PNG")
        buffer.seek(0)

        class UploadedMeme:
            def __init__(self, name, buffer):
                self.name = name
                self._buffer = buffer
            def getbuffer(self):
                return self._buffer.getbuffer()

        fake_file = UploadedMeme(f"meme_{uploaded_file.name}", buffer)

        save_uploaded_meme(fake_file)
        st.success("✅ Meme saved to gallery!")

        # You must replace this with the real hosted URL after upload to your storage
        uploaded_url = f"https://your-storage.com/{fake_file.name}"

        api_response = create_record(
            title=f"Meme: {top_text} {bottom_text}",
            media_type="image",
            user_id=USER_ID,
            category_id=CATEGORY_ID,
            file_url=uploaded_url,
            file_name=fake_file.name,
            file_size=len(fake_file.getbuffer()),
            description="Generated Telugu meme"
        )
        if api_response:
            st.success("✅ Meme uploaded to API successfully!")
