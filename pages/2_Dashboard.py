import streamlit as st
import pandas as pd
import sqlite3
import os

st.title("NBA Dashboard")

DB_PATH = "data/nba_news.db"

st.write("File exists:", os.path.exists(DB_PATH))

if os.path.exists(DB_PATH):
    st.write("File size:", os.path.getsize(DB_PATH))

try:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    st.write("Tables in database:", tables)
    conn.close()
except Exception as e:
    st.error(f"Database connection failed: {e}")
