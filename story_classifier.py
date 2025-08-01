# story_classifier.py
import streamlit as st
from transformers import pipeline

@st.cache_resource
def load_classifier():
    return pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

def run():
    classifier = load_classifier()
    values = ["Honesty", "Kindness", "Respect", "Responsibility", "Courage", "Empathy", "Forgiveness", "Perseverance", "Gratitude"]

    st.title("🧠 Values Vault – Personality Development Story Collector")
    story = st.text_area("✏️ Share a short story that taught you a life lesson:", height=150)

    if st.button("Submit Story"):
        if story.strip():
            with st.spinner("Classifying story..."):
                result = classifier(story, values)
                predicted_value = result['labels'][0]

            st.success("✅ Story Submitted!")
            st.markdown(f"📖 **Your Story:** {story}")
            selected_value = st.selectbox("💡 Suggested Value (you can change if needed):", values, index=values.index(predicted_value))
            if st.button("✅ Confirm Value"):
                st.success(f"📝 Story tagged with **{selected_value}**")
                # Save to CSV, DB etc. (optional)
        else:
            st.warning("Please write a story before submitting.")
