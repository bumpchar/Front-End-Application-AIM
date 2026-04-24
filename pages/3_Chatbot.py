import streamlit as st
from openai import OpenAI

st.markdown("""
<style>
.stApp {
    background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%);
    color: white;
}

h1, h2, h3, h4, p, label,
[data-testid="stMarkdownContainer"],
[data-testid="stWidgetLabel"],
[data-testid="stMetricValue"] {
    color: white !important;
}

.card {
    background-color: rgba(255, 255, 255, 0.06);
    padding: 20px;
    border-radius: 16px;
    border: 1px solid rgba(255,255,255,0.12);
    box-shadow: 0 4px 14px rgba(0,0,0,0.25);
}

[data-testid="stCaptionContainer"] {
    color: #cbd5e1 !important;
}

input, textarea,
div[data-baseweb="input"],
div[data-baseweb="select"],
div[data-baseweb="select"] > div {
    background-color: #1e293b !important;
    color: white !important;
}

div[data-baseweb="select"] * {
    color: white !important;
}

ul[role="listbox"],
ul[role="listbox"] li {
    background-color: #1e293b !important;
    color: white !important;
}

ul[role="listbox"] li:hover {
    background-color: #334155 !important;
}

section[data-testid="stSidebar"] {
    background-color: #E5E7EB;
}

section[data-testid="stSidebar"] * {
    color: #0f172a !important;
}

.stButton > button {
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

div[data-baseweb="input"] input {
    color: white !important;
    -webkit-text-fill-color: white !important;
}

/* Fix placeholder text */
div[data-baseweb="input"] input::placeholder {
    color: #cbd5e1 !important;
}

</style>
""", unsafe_allow_html=True)

st.title("NBA Chatbot 🏀")
st.write("Ask questions about NBA teams, players, stats, or game recaps.")

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

question = st.text_input("Ask a question:")

if st.button("Ask") and question:
    with st.spinner("Thinking..."):
        response = client.chat.completions.create(
            model="gpt-5-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful NBA assistant. Answer questions about NBA teams, players, stats, and game recaps clearly and simply."
                },
                {
                    "role": "user",
                    "content": question
                }
            ]
        )

        st.subheader("Answer")
        st.write(response.choices[0].message.content)
