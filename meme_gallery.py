import os
import json
import streamlit as st

MEME_FOLDER = "memes"
LIKES_FILE = os.path.join(MEME_FOLDER, "likes.json")
os.makedirs(MEME_FOLDER, exist_ok=True)

def load_likes():
    if os.path.exists(LIKES_FILE):
        with open(LIKES_FILE, "r") as f:
            return json.load(f)
    else:
        return {}

def save_likes(likes):
    with open(LIKES_FILE, "w") as f:
        json.dump(likes, f)

def save_uploaded_meme(uploaded_file):
    file_path = os.path.join(MEME_FOLDER, uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return file_path

def run():
    st.title("📸 Meme Gallery")

    meme_files = [f for f in os.listdir(MEME_FOLDER) if f.lower().endswith((".png", ".jpg", ".jpeg"))]

    # Load likes from disk or init empty dict
    likes = load_likes()

    if not meme_files:
        st.info("No memes in gallery yet.")
    else:
        for meme_file in meme_files:
            meme_path = os.path.join(MEME_FOLDER, meme_file)
            st.image(meme_path, caption=meme_file, use_container_width=True)

            # Initialize likes count if missing
            if meme_file not in likes:
                likes[meme_file] = 0

            col1, col2 = st.columns([1, 5])
            with col1:
                if st.button(f"👍 {likes[meme_file]}", key=meme_file):
                    likes[meme_file] += 1
                    save_likes(likes)
                    st.rerun()  # refresh UI to update count immediately
            with col2:
                st.write(f"Likes: {likes[meme_file]}")
