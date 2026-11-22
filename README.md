# 🗄️ Natural-Language-to-SQL AI Data Analyst

🔗 **Live App:** [nl-to-sql-analyst-jhlwhisygb2mpcsidc3gnu.streamlit.app](https://nl-to-sql-analyst-jhlwhisygb2mpcsidc3gnu.streamlit.app/)

An interactive AI-powered data analysis web application built with **Python**, **SQLite**, **Pandas**, **Streamlit**, and the **Google Gemini API**. Users can ask business questions in plain English against either a built-in multi-table relational database or any custom uploaded CSV file—and get validated SQL queries, result tables, and automatic visualizations.

---

## ✨ Key Features

- **Natural Language to SQL Translation:** Converts plain-English analytical questions into valid SQLite `SELECT` queries using the Google Gemini API (`gemini-3.5-flash-lite` with automatic fallback to `gemini-3.6-flash`).
- **Schema-Grounded Prompting:** Extracts live `CREATE TABLE` DDL schemas and sample rows directly from SQLite to prevent column or table hallucinations.
- **Dual Data Source Support:**
  - **Built-in E-Commerce Database:** Pre-populated 3-table relational schema (`customers`, `products`, `orders`) supporting multi-table `JOIN`, `GROUP BY`, and aggregation queries out of the box.
  - **Custom CSV Upload:** Automatically sanitizes column names and loads any uploaded `.csv` file into an in-memory SQLite table (`uploaded_data`) for instant querying.
- **Read-Only SQL Safety Guardrails:** Validates every generated query using regex checks before execution—blocking stacked statements and destructive keywords (`DROP`, `DELETE`, `UPDATE`, `INSERT`, `ALTER`, `TRUNCATE`, `ATTACH`, `DETACH`, `PRAGMA`).
- **Automated Results & Charts:** Executes validated queries via Pandas (`pd.read_sql_query`) and automatically renders interactive Streamlit bar charts whenever categorical and numeric columns are returned.

---

## 🛠️ Tech Stack

- **Language:** Python 3.13
- **Frontend & Deployment:** Streamlit, Streamlit Community Cloud
- **Database & Data Processing:** SQLite (`sqlite3`), Pandas
- **AI / LLM Integration:** Google GenAI SDK (`google-genai`), Structured JSON Output Mode
- **Configuration:** `python-dotenv`

---

## 📂 Project Structure

```text
nl-to-sql-analyst/
├── app.py              # Main Streamlit UI, Gemini NL-to-SQL pipeline, SQL guardrails & charting
├── database.py         # SQLite relational schema setup, CSV ingestion & DDL schema inspector
├── requirements.txt    # Python dependencies
├── .gitignore          # Excludes virtual environments, local DBs, and .env secrets
└── README.md           # Project documentation
