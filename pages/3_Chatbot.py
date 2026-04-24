import streamlit as st
from openai import OpenAI

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
