# styles.py

import streamlit as st

def load_css():
    st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%);
        color: white;
    }

    html, body, [class*="css"]  {
        color: white;
    }

    .card {
        background-color: rgba(255, 255, 255, 0.06);
        padding: 20px;
        border-radius: 16px;
        border: 1px solid rgba(255,255,255,0.12);
        box-shadow: 0 4px 14px rgba(0,0,0,0.25);
    }

    h2, h3 {
        color: #f8fafc;
    }

    [data-testid="stCaptionContainer"] {
        color: #cbd5e1;
    }

    .stButton > button {
        width: 100%;
        border-radius: 10px;
        background-color: #f97316;
        color: white;
        border: none;
        font-weight: 600;
    }

    .stButton > button:hover {
        background-color: #ea580c;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)
