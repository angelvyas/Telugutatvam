import streamlit as st

# Simple FAQ knowledge base (replace these with your app's real FAQs)
FAQS = {
    "what is this app": "This app is a Telugu Corpus Collection Engine that allows users to contribute text and image data, including memes, to support building a Telugu Large Language Model.",
    "how can i contribute": "You can contribute by uploading text or images directly through the app. Images are auto-captioned with BLIP and can be used for meme generation.",
    "what is meme generator": "The meme generator allows you to create Telugu memes using uploaded images and text captions in Telugu font.",
    "how does leaderboard work": "The leaderboard ranks memes by the number of likes they receive from users.",
    "is this app offline": "Some features work offline, like the chatbot here, but others require internet (such as deployment on Hugging Face Spaces).",
    "what categories can i choose": "Categories include cultural topics, movies, historical events, literature, and more."
}

def get_response(user_input: str) -> str:
    user_input_lower = user_input.lower()
    for question, answer in FAQS.items():
        if question in user_input_lower:
            return answer
    return "I'm not sure about that. Please try asking in a different way or check the documentation."

def run():
    st.title("Offline FAQ Chatbot")

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    user_input = st.text_input("Ask me something about the app:")
    if st.button("Ask") and user_input.strip():
        answer = get_response(user_input)
        st.session_state.chat_history.append(("You", user_input))
        st.session_state.chat_history.append(("Bot", answer))

    for sender, message in st.session_state.chat_history:
        st.markdown(f"**{sender}:** {message}")
