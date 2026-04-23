import streamlit as st

st.set_page_config(
    page_title="NBA Multi-Agent Assistant",
    page_icon="🏀",
    layout="wide"
)

st.markdown("""
<style>
/* Main app background */
.stApp {
    background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%);
    color: white;
}

/* Make normal text lighter */
html, body, [class*="css"]  {
    color: white;
}

/* Section cards */
.card {
    background-color: rgba(255, 255, 255, 0.06);
    padding: 20px;
    border-radius: 16px;
    border: 1px solid rgba(255,255,255,0.12);
    box-shadow: 0 4px 14px rgba(0,0,0,0.25);
}

/* Subheaders */
h2, h3 {
    color: #f8fafc;
}

/* Caption text */
[data-testid="stCaptionContainer"] {
    color: #cbd5e1;
}

/* Buttons */
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

col1, col2, col3 = st.columns(3)

with col1:
    st.image("assets/image.png")
    st.caption("Dashboard: Track team and player performance")

with col2:
    # st.image("assets/chatbot.png")
    st.caption("Chatbot: Ask stats or game recap questions")

with col3:
    # st.image("assets/editor.png")
    st.caption("Data Editor: Review and update data")

