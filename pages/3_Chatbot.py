import streamlit as st
import os
import warnings

warnings.filterwarnings("ignore")

st.set_page_config(
    page_title="NBA Chatbot",
    page_icon="🏀",
    layout="wide"
)

st.markdown("""
<style>
.stApp {
    background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%);
    color: white;
}
html, body, [class*="css"] {
    color: white;
}
h1, h2, h3 {
    color: #f8fafc;
}
section[data-testid="stSidebar"] {
    background-color: #020617;
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
</style>
""", unsafe_allow_html=True)

st.title("NBA Chatbot 🏀")
st.write("Ask questions about NBA teams, players, stats, or game recaps.")

# Get API key from Streamlit Secrets
api_key = st.secrets.get("OPENAI_API_KEY", None)

if not api_key:
    st.error("OpenAI API key is missing. Add OPENAI_API_KEY in Streamlit Secrets.")
    st.stop()

# Imports for your class package
try:
    from intro_to_agents.rag.embedders import SentenceTransformerEmbedder
    from intro_to_agents.rag.vector_databases import ChromaDBVectorDB
    from intro_to_agents.agents.llms import OpenAILLM
    from intro_to_agents.agents.agents import MultiAgent, ChromaAgent, SQLiteAgent
except Exception as e:
    st.error("The intro_to_agents package could not be imported.")
    st.write("Error:", e)
    st.stop()

# Instantiate LLM
model = "gpt-5-mini"
llm = OpenAILLM(api_key=api_key, model=model)

# Paths that work on Streamlit Cloud
dbpath = "data"
db_url = "data/NBA_DB.db"

db_desc = """
The database contains NBA statistics from 2020 to present. 
There are four tables: player_stats, players, team_stats, and teams.

The player_stats table contains individual player stats for each game using player_id.
The players table lists player names and player_id values.
The team_stats table contains team stats for each game using team_id.
The teams table contains team names and team_id values.

Use the available data to answer questions about NBA players, teams, games, and trends.
""".strip()

@st.cache_resource
def build_agent():
    # RAG Agent
    embedder = SentenceTransformerEmbedder()

    vdb = ChromaDBVectorDB(
        dbpath=dbpath,
        embedder=embedder,
        distance_measure="cosine"
    )

    vdb.initialize_db()
    vdb.initialize_collection("NBA_Data_CharLen")

    rag_agent = ChromaAgent(
        llm=llm,
        vectordb=vdb
    )

    rag_desc = "Answers questions about NBA game recaps and recent NBA news."

    rag_kwargs = {
        "k": 5,
        "max_distance": 0.75,
        "show_citations": True
    }

    # SQL Agent
    sql_agent = SQLiteAgent(
        llm=llm,
        database_url=db_url,
        db_desc=db_desc,
        include_detail=True
    )

    sql_desc = "Answers questions about NBA player and team statistics."

    sql_kwargs = {
        "view_sql": True
    }

    # MultiAgent
    multi_agent = MultiAgent(
        llm=llm,
        agent_names=["RAG Agent", "SQL Agent"],
        agents=[rag_agent, sql_agent],
        agent_descriptions=[rag_desc, sql_desc],
        agent_query_kwargs=[rag_kwargs, sql_kwargs]
    )

    return multi_agent

try:
    multi_agent = build_agent()
except Exception as e:
    st.error("The chatbot agent could not be loaded.")
    st.write("Most likely issue: the vector database or SQLite database path is missing/wrong.")
    st.write("Error:", e)
    st.stop()

# Chat UI
col1, col2 = st.columns([2, 1])

with col1:
    user_question = st.text_input(
        "Ask the chatbot a question:",
        placeholder="Example: Which Heat player had a career-high game on March 12, 2026?"
    )

    ask_button = st.button("Ask Chatbot")

with col2:
    st.subheader("Traceability")
    st.write("This panel is for citations, SQL, or logic from the agent response.")

if ask_button and user_question:
    with st.spinner("Thinking..."):
        try:
            response = multi_agent.query(
                user_question,
                show_logic=True
            )

            st.subheader("Answer")
            st.write(response)

            with col2:
                st.write(response)

        except Exception as e:
            st.error("The chatbot could not answer the question.")
            st.write("Error:", e)
