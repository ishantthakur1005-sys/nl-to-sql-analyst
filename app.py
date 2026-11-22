import os
import json
import re
import sqlite3
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from google import genai
from google.genai import types
from database import create_sample_db, load_csv_to_db, get_schema_description

load_dotenv()

st.set_page_config(page_title="NL-to-SQL AI Data Analyst", page_icon="🗄️", layout="wide")
st.title("🗄️ Natural-Language-to-SQL AI Data Analyst")
st.caption("Ask questions in plain English—Gemini translates them into SQL, runs them on SQLite, and visualizes the results.")

api_key = os.getenv("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY", None)
if not api_key:
    st.error("Missing GEMINI_API_KEY. Add it to your .env file or Streamlit Secrets.")
    st.stop()

client = genai.Client(api_key=api_key)

# Sidebar: choose built-in multi-table DB or upload CSV
with st.sidebar:
    st.header("1. Choose Data Source")
    data_mode = st.radio("Database:", ["Built-in E-Commerce DB (3 Tables)", "Upload Custom CSV"])

    if data_mode == "Upload Custom CSV":
        csv_file = st.file_uploader("Upload a CSV file", type=["csv"])
        if csv_file is not None:
            conn = load_csv_to_db(csv_file)
        else:
            st.info("Upload a CSV to query it with SQL.")
            st.stop()
    else:
        conn = create_sample_db()

    st.subheader("Database Schema")
    schema_text = get_schema_description(conn)
    st.code(schema_text, language="sql")


def is_safe_select_query(sql: str) -> bool:
    """Allows only read-only SELECT / WITH queries and blocks destructive SQL keywords."""
    cleaned = sql.strip().rstrip(";").strip()
    if ";" in cleaned:  # Block stacked multi-statements
        return False
    if not re.match(r"^(SELECT|WITH)\b", cleaned, re.IGNORECASE):
        return False
    forbidden = r"\b(DROP|DELETE|UPDATE|INSERT|ALTER|TRUNCATE|ATTACH|DETACH|PRAGMA)\b"
    return not re.search(forbidden, cleaned, re.IGNORECASE)


def generate_sql_with_fallback(question: str, schema: str) -> dict:
    prompt = f"""
You are an expert SQLite data analyst. Convert the user's question into a single valid, read-only SQLite SELECT query based ONLY on the schema below.

Database Schema:
{schema}

User Question:
{question}

Return valid JSON with exact keys:
- "sql_query": string (valid SQLite SELECT statement, no markdown backticks)
- "explanation": string (1-2 sentence explanation of how the query answers the question)
"""
    models = ["gemini-3.5-flash-lite", "gemini-3.6-flash"]
    last_err = None
    for model_name in models:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                ),
            )
            return json.loads(response.text)
        except Exception as e:
            last_err = e
    raise RuntimeError(f"All models failed: {last_err}")


st.subheader("2. Ask a Question in Plain English")
sample_questions = [
    "Show total revenue by city for delivered orders, sorted highest to lowest.",
    "Which top 3 customers spent the most money across all delivered orders?",
    "List total units sold and revenue per product category.",
]
selected_sample = st.selectbox("Try an example question (or type your own below):", ["Custom question..."] + sample_questions)
default_q = "" if selected_sample == "Custom question..." else selected_sample
user_question = st.text_input("Your question:", value=default_q, placeholder="e.g., What is the total revenue for each product?")

if st.button("Run AI SQL Query", type="primary") and user_question.strip():
    with st.spinner("Generating SQL and querying database..."):
        try:
            ai_result = generate_sql_with_fallback(user_question, schema_text)
            sql_query = ai_result["sql_query"].strip()
            explanation = ai_result["explanation"]

            st.markdown("### Generated SQL Query")
            st.code(sql_query, language="sql")
            st.info(explanation)

            if not is_safe_select_query(sql_query):
                st.error("Blocked unsafe SQL query. Only read-only SELECT statements are permitted.")
                st.stop()

            result_df = pd.read_sql_query(sql_query, conn)
            st.markdown("### Query Results")
            st.dataframe(result_df, use_container_width=True)

            # Auto-chart when result has 1 text/label column and at least 1 numeric column
            num_cols = result_df.select_dtypes(include="number").columns.tolist()
            cat_cols = result_df.select_dtypes(exclude="number").columns.tolist()
            if len(result_df) > 1 and len(num_cols) >= 1 and len(cat_cols) >= 1:
                st.markdown("### Visual Summary")
                st.bar_chart(result_df.set_index(cat_cols[0])[num_cols[0]])

        except Exception as e:
            st.error(f"Query failed: {e}")