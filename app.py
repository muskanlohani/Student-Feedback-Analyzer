# app.py
import os
import re
import json
from dotenv import load_dotenv
load_dotenv()

import streamlit as st
import pandas as pd
import mysql.connector
import matplotlib.pyplot as plt
from wordcloud import WordCloud

# Google Gen AI SDK
from google import genai
from google.genai import types

# # -------------------------
# # Config (from env)
# # -------------------------
# GEMINI_KEY = os.getenv("GEMINI_API_KEY")
# DB_HOST = os.getenv("DB_HOST", "localhost")
# DB_USER = os.getenv("DB_USER", "root")
# DB_PASSWORD = os.getenv("DB_PASSWORD", "")
# DB_NAME = os.getenv("DB_NAME", "feedback_db")

# -------------------------
# Config (from Streamlit secrets)
# -------------------------
GEMINI_KEY = st.secrets["GEMINI_API_KEY"]
DB_HOST = st.secrets["database"]["DB_HOST"]
DB_PORT = int(st.secrets["database"]["DB_PORT"])
DB_USER = st.secrets["database"]["DB_USER"]
DB_PASSWORD = st.secrets["database"]["DB_PASSWORD"]
DB_NAME = st.secrets["database"]["DB_NAME"]

# -------------------------
# Initialize Gemini client
# -------------------------
# client picks up GEMINI_API_KEY from env var by default (per docs)
client = genai.Client()  # uses env var GEMINI_API_KEY
# Optionally you could initialize with explicit key (not recommended for production)

# -------------------------
# DB helpers
# -------------------------
def get_db_connection():
    conn = mysql.connector.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        autocommit=True
    )
    return conn

def insert_feedback(student_name, subject, rating, comments):
    conn = get_db_connection()
    cursor = conn.cursor()
    sql = "INSERT INTO feedback (student_name, subject, rating, comments) VALUES (%s,%s,%s,%s)"
    cursor.execute(sql, (student_name, subject, rating, comments))
    cursor.close()
    conn.close()

def fetch_all_feedback():
    conn = get_db_connection()
    df = pd.read_sql("SELECT * FROM feedback ORDER BY date_submitted DESC", conn)
    conn.close()
    return df

# -------------------------
# Helper: safe JSON extraction
# -------------------------
def extract_json(text):
    # try to find the first JSON array/object in the text
    m = re.search(r'(\{.*\}|\[.*\])', text, re.S)
    if m:
        return m.group(1)
    return text

# -------------------------
# AI: batch sentiment classification
# -------------------------
def classify_sentiments_bulk(comments):
    if not comments:
        return []

    prompt = (
        "Classify sentiment for each student feedback. "
        "Return ONLY a JSON array of objects with keys: id (1-based) and sentiment. "
        "Sentiment must be one of: Positive, Negative, Neutral. "
        "DO NOT include any extra text.\n\nComments:\n"
    )
    for i, c in enumerate(comments, start=1):
        # keep it short to avoid huge prompt sizes
        prompt += f"{i}. {c}\n"

    # set thinking_budget=0 to reduce extra 'reasoning' overhead (faster + cheaper)
    config = types.GenerateContentConfig(
        thinking_config=types.ThinkingConfig(thinking_budget=0)
    )

    resp = client.models.generate_content(
        model="gemini-2.5-flash",   # production/flash model in quickstart
        contents=prompt,
        config=config
    )
    text = resp.text

    json_text = extract_json(text)
    try:
        parsed = json.loads(json_text)
        return parsed
    except Exception:
        # fallback: return simple neutral labels if parsing fails
        return [{"id": i+1, "sentiment": "Neutral"} for i in range(len(comments))]

# -------------------------
# AI: summarize feedback
# -------------------------
def summarize_feedback(comments):
    if not comments:
        return "No comments to summarize."
    prompt = (
        "Summarize the following student feedback into up to 5 concise bullet points. "
        "Be neutral, short and include main themes only.\n\nComments:\n"
        + "\n".join([f"- {c}" for c in comments])
    )
    config = types.GenerateContentConfig(
        thinking_config=types.ThinkingConfig(thinking_budget=0)
    )
    resp = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=config
    )
    return resp.text.strip()

# -------------------------
# Streamlit UI
# -------------------------
st.set_page_config(page_title="Student Feedback Analyzer", layout="wide")
st.title("📚 Student Feedback Analyzer")

menu = st.sidebar.radio("Navigate", ["Submit Feedback", "Dashboard"])

if menu == "Submit Feedback":
    st.header("Submit Feedback")
    name = st.text_input("Student name")
    subject = st.selectbox("Subject", ["Physics", "Chemistry", "Mathematics", "Computer Science", "English"])
    rating = st.slider("Rating (1=poor, 5=excellent)", 1, 5, 4)
    comments = st.text_area("Comments")

    if st.button("Submit"):
        if not subject or not comments:
            st.error("Please fill subject and comments.")
        else:
            insert_feedback(name, subject, rating, comments)
            st.success("Feedback submitted ✅")
            # Optionally clear inputs - Streamlit doesn't clear by default.

else:
    st.header("Feedback Dashboard")
    df = fetch_all_feedback()
    st.subheader("All feedback")
    st.dataframe(df)

    if not df.empty:
        # Average rating per subject
        st.subheader("Average Rating per Subject")
        avg = df.groupby("subject")["rating"].mean().sort_values(ascending=False)
        st.bar_chart(avg)

        # ---------- Subject-wise analysis ----------
        st.subheader("Subject-wise Analysis")
        subjects = df["subject"].unique()
        selected_subject = st.selectbox("Choose a subject to analyze", subjects)

        if selected_subject:
            st.markdown(f"### 📘 {selected_subject}")
            subj_df = df[df["subject"] == selected_subject]

            # Word cloud
            st.write("**Word Cloud**")
            text = " ".join(subj_df["comments"].dropna().tolist())
            if text.strip():
                wc = WordCloud(width=800, height=300, background_color="white").generate(text)
                fig, ax = plt.subplots(figsize=(10,3))
                ax.imshow(wc, interpolation="bilinear")
                ax.axis("off")
                st.pyplot(fig)
            else:
                st.write("No comments to generate word cloud.")

            # Sentiment analysis
            st.write("**Sentiment Analysis (AI)**")
            comments_list = subj_df["comments"].dropna().tolist()
            if comments_list:
                with st.spinner("Analyzing sentiments via Gemini..."):
                    labels = classify_sentiments_bulk(comments_list)
                counts = {"Positive":0, "Negative":0, "Neutral":0}
                for item in labels:
                    lab = item.get("sentiment", "Neutral")
                    counts[lab] = counts.get(lab,0) + 1
                st.write(counts)
            else:
                st.write("No comments to analyze.")

            # AI summary
            st.write("**AI Summary**")
            if comments_list:
                with st.spinner("Summarizing feedback via Gemini..."):
                    summary = summarize_feedback(comments_list)
                st.write(summary)
            else:
                st.write("No comments to summarize.")
