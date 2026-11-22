import sqlite3
import pandas as pd


def create_sample_db() -> sqlite3.Connection:
    """Creates an in-memory SQLite database with 3 related tables for realistic JOIN queries."""
    conn = sqlite3.connect(":memory:", check_same_thread=False)
    cursor = conn.cursor()

    cursor.executescript("""
        CREATE TABLE customers (
            customer_id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            city TEXT NOT NULL,
            signup_date TEXT NOT NULL
        );

        CREATE TABLE products (
            product_id INTEGER PRIMARY KEY,
            product_name TEXT NOT NULL,
            category TEXT NOT NULL,
            unit_price REAL NOT NULL
        );

        CREATE TABLE orders (
            order_id INTEGER PRIMARY KEY,
            customer_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            order_date TEXT NOT NULL,
            status TEXT NOT NULL,
            FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
            FOREIGN KEY (product_id) REFERENCES products(product_id)
        );

        INSERT INTO customers VALUES
            (1, 'Aarav Sharma', 'Mumbai', '2026-01-12'),
            (2, 'Priya Nair', 'Pune', '2026-02-05'),
            (3, 'Rohan Verma', 'Bengaluru', '2026-02-19'),
            (4, 'Sneha Kulkarni', 'Mumbai', '2026-03-03'),
            (5, 'Vikram Desai', 'Delhi', '2026-03-18'),
            (6, 'Ananya Joshi', 'Mumbai', '2026-04-02');

        INSERT INTO products VALUES
            (101, 'Mechanical Keyboard', 'Electronics', 4500.0),
            (102, 'Wireless Mouse', 'Electronics', 1800.0),
            (103, 'USB-C Hub', 'Accessories', 2200.0),
            (104, 'Laptop Stand', 'Accessories', 1500.0),
            (105, '27-inch Monitor', 'Electronics', 18500.0);

        INSERT INTO orders VALUES
            (1001, 1, 101, 1, '2026-05-01', 'Delivered'),
            (1002, 1, 102, 2, '2026-05-04', 'Delivered'),
            (1003, 2, 105, 1, '2026-05-08', 'Delivered'),
            (1004, 3, 103, 3, '2026-05-12', 'Delivered'),
            (1005, 4, 101, 2, '2026-05-15', 'Delivered'),
            (1006, 5, 104, 2, '2026-05-18', 'Cancelled'),
            (1007, 6, 105, 1, '2026-05-20', 'Delivered'),
            (1008, 2, 102, 1, '2026-05-22', 'Delivered'),
            (1009, 4, 103, 2, '2026-05-25', 'Delivered');
    """)
    conn.commit()
    return conn


def load_csv_to_db(uploaded_file) -> sqlite3.Connection:
    """Loads a user-uploaded CSV into an in-memory SQLite table named 'uploaded_data'."""
    conn = sqlite3.connect(":memory:", check_same_thread=False)
    df = pd.read_csv(uploaded_file)
    # Clean column names so SQL queries never break on spaces
    df.columns = [c.strip().replace(" ", "_").lower() for c in df.columns]
    df.to_sql("uploaded_data", conn, index=False, if_exists="replace")
    return conn


def get_schema_description(conn: sqlite3.Connection) -> str:
    """Extracts table schemas and 2 sample rows per table to ground Gemini's SQL generation."""
    cursor = conn.cursor()
    tables = cursor.execute(
        "SELECT name, sql FROM sqlite_master WHERE type='table';"
    ).fetchall()

    schema_parts = []
    for table_name, create_sql in tables:
        sample_df = pd.read_sql_query(f"SELECT * FROM {table_name} LIMIT 2;", conn)
        schema_parts.append(
            f"Table: {table_name}\nSchema:\n{create_sql}\nSample rows:\n{sample_df.to_string(index=False)}"
        )
    return "\n\n".join(schema_parts)