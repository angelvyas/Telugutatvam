import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import os
import io
from meme_gallery import save_uploaded_meme  # Import save function

# Path to Telugu font file
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

    # Take text first
    top_text = st.text_input("Top Text (Telugu supported)")
    bottom_text = st.text_input("Bottom Text (Telugu supported)")

    # Then upload image
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

        # Save the meme image to bytes buffer with a generated filename
        buffer = io.BytesIO()
        meme.save(buffer, format="PNG")
        buffer.seek(0)

        # Create a fake file-like object with a name attribute
        class UploadedMeme:
            def __init__(self, name, buffer):
                self.name = name
                self._buffer = buffer
            def getbuffer(self):
                return self._buffer.getbuffer()

        fake_file = UploadedMeme(f"meme_{uploaded_file.name}", buffer)

        save_uploaded_meme(fake_file)
        st.success("✅ Meme saved to gallery!")
