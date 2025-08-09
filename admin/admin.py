import streamlit as st
import sqlite3
import pandas as pd
import os
import hashlib
import plotly.express as px

DB_PATH = "responses.db"

# ---------- Authentication ----------
def check_login(username, password):
    # Hardcoded for simplicity (you can load from file or env later)
    stored_username = "admin"
    stored_password = "admin123"  # Plain text for now

    # Hash the password (optional enhancement)
    return username == stored_username and password == stored_password

# ---------- Load Data ----------
def load_data():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM responses", conn)
    conn.close()
    return df

# ---------- Get File Path ----------
def get_uploaded_file_path(response):
    if response["mode"] == "Text":
        return None
    hint = response["text_response"]
    if "File uploaded:" in hint:
        return hint.split("File uploaded:")[-1].strip()
    return None

# ---------- Run Admin Panel ----------
def run_admin_panel():
    st.title("🛠️ Admin Panel - Prompt Collector Responses")

    # ----------- Login ----------
    with st.sidebar:
        st.markdown("## 🔐 Admin Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

    if not check_login(username, password):
        st.warning("Please enter valid admin credentials to proceed.")
        st.stop()

    # ---------- Load Data ----------
    df = load_data()

    if df.empty:
        st.info("No responses submitted yet.")
        return

    # ---------- Summary Charts ----------
    st.subheader("📊 Submission Summary")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Responses", len(df))
    with col2:
        st.metric("Unique Users", df["swecha_username"].nunique())
    with col3:
        st.metric("Prompt Categories", df["category"].nunique())

    chart1 = px.histogram(df, x="category", title="Responses per Category", color="category")
    chart2 = px.histogram(df, x="mode", title="Responses by Mode", color="mode")
    chart3 = px.histogram(df, x="swecha_username", title="Responses per User", color="swecha_username")

    st.plotly_chart(chart1, use_container_width=True)
    st.plotly_chart(chart2, use_container_width=True)
    st.plotly_chart(chart3, use_container_width=True)

    # ---------- Filters ----------
    st.sidebar.header("🔍 Filter Responses")

    usernames = ["All"] + sorted(df["swecha_username"].unique().tolist())
    categories = ["All"] + sorted(df["category"].unique().tolist())
    modes = ["All"] + sorted(df["mode"].unique().tolist())

    selected_user = st.sidebar.selectbox("By Username", usernames)
    selected_category = st.sidebar.selectbox("By Category", categories)
    selected_mode = st.sidebar.selectbox("By Mode", modes)
    show_latest_only = st.sidebar.checkbox("🕒 Show only latest submission per user")

    filtered_df = df.copy()
    if selected_user != "All":
        filtered_df = filtered_df[filtered_df["swecha_username"] == selected_user]
    if selected_category != "All":
        filtered_df = filtered_df[filtered_df["category"] == selected_category]
    if selected_mode != "All":
        filtered_df = filtered_df[filtered_df["mode"] == selected_mode]

    if show_latest_only:
        filtered_df = filtered_df.sort_values("timestamp").groupby("swecha_username", as_index=False).last()

    st.write(f"📄 Showing **{len(filtered_df)}** response(s)")

    # ---------- Display Entries ----------
    for _, row in filtered_df.iterrows():
        with st.expander(f"🧾 {row['swecha_username']} | {row['category']} | {row['mode']}"):
            st.markdown(f"**Prompt:** {row['prompt']}")
            st.markdown(f"**Response Timestamp:** {row['timestamp']}")
            st.markdown(f"**Location:** {row['location']}")
            st.markdown(f"**Email:** {row['email']}")

            if row["mode"] == "Text":
                st.markdown("**Text Response:**")
                st.code(row["text_response"], language="text")
            else:
                file_path = get_uploaded_file_path(row)
                if file_path and os.path.exists(file_path):
                    ext = file_path.split('.')[-1].lower()
                    with open(file_path, "rb") as f:
                        file_bytes = f.read()
                        if ext in ["mp3", "wav", "m4a"]:
                            st.audio(file_bytes, format=f"audio/{ext}")
                        elif ext in ["mp4", "mkv", "webm"]:
                            st.video(file_bytes)
                        st.download_button("📥 Download File", file_bytes, file_name=os.path.basename(file_path))
                else:
                    st.warning("⚠️ Uploaded file not found.")

    # ---------- Download Button ----------
    st.sidebar.markdown("### 📦 Export Filtered Data")
    st.sidebar.download_button(
        label="Download CSV",
        data=filtered_df.to_csv(index=False),
        file_name="filtered_responses.csv",
        mime="text/csv"
    )

# ---------- Run App ----------
if __name__ == "__main__":
    run_admin_panel()
