import streamlit as st

st.set_page_config(
    page_title="NBA Multi-Agent Assistant",
    page_icon="🏀",
    layout="wide"
)

st.title("What's New in the Association? 🏀")

col1, col2, col3 = st.columns([1,2,1])

with col2:
    st.image("assets/Lebron_celly.gif", use_container_width=True)

st.markdown("""
Anything you need to know about the NBA all in one place.

- **Dashboard** → View team and player trends.
- **Chatbot** → Ask stats or recap questions.
- **Data Editor** → Review or Update Data
""")

st.subheader("Where would you like to go?")

col1, col2, col3 = st.columns(3)

with col1:
    st.info("**Dashboard**")
    if st.button("Open Dashboard"):
        st.switch_page("pages/2_Dashboard.py")

with col2:
    st.info("**Chatbot**")
    if st.button("Open Chatbot"):
        st.switch_page("pages/3_Chatbot.py")

with col3:
    st.info("**Data Editor**")
    if st.button("Open Data Editor"):
        st.switch_page("pages/4_Data_Editor.py")

st.subheader("What Our App Looks Like")

