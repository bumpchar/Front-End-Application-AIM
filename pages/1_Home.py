import streamlit as st

st.set_page_config(
    page_title="NBA Multi-Agent Assistant",
    page_icon="🏀",
    layout="wide"
)

st.title("What's New in the Association? 🏀")

st.markdown("""
Ask questions about **NBA stats** and **game recaps** in one place.

- **SQL agent** → player and team stats per game
- **RAG agent** → game recap summaries and narrative context
""")

st.subheader("Where would you like to go?")

col1, col2, col3 = st.columns(3)

with col1:
    st.info("**Dashboard**\n\nView team and player trends.")
    if st.button("Open Dashboard"):
        st.switch_page("pages/2_Dashboard.py")

with col2:
    st.info("**Chatbot**\n\nAsk stats or recap questions.")
    st.button("Open Chatbot")

with col3:
    st.info("**Data Editor**\n\nReview or update data.")
    st.button("Open Data Editor")

st.subheader("Example questions")

st.markdown("""
**Stats / SQL**
- How many points did Jayson Tatum score last game?
- Which team had the best 3-point percentage this week?

**Recaps / RAG**
- Summarize the Lakers vs Warriors game recap.
- What were the main reasons the Celtics won?
""")
