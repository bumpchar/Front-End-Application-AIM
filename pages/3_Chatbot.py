import streamlit as st

st.title("Welcome to our Chatbot!")
st.write("This our ChatBot.")

import os
import warnings
import streamlit as st

from intro_to_agents.rag.embedders import SentenceTransformerEmbedder
from intro_to_agents.rag.vector_databases import ChromaDBVectorDB
from intro_to_agents.agents.llms import OpenAILLM
from intro_to_agents.agents.agents import MultiAgent, ChromaAgent, SQLiteAgent

warnings.filterwarnings("ignore")

# ── Page config ───────────────────────────────────────────────────────────────
st.title("Welcome to our Chatbot!")
st.write("This is our NBA ChatBot.")

# ── Agent setup — cached so it only runs once, not on every message ───────────
@st.cache_resource
def build_multi_agent():
    # FIX 1: use Streamlit secrets instead of .env (works for all users)
    api_key = st.secrets["OPENAI_API_KEY"]

    # FIX 2: corrected model name (gpt-5-mini does not exist)
    llm = OpenAILLM(api_key=api_key, model="gpt-4o-mini")

    # FIX 3: relative path so it works on any machine, not just your laptop
    dbpath = os.path.join(os.path.dirname(__file__), "..", "data", "chroma_db")

    embedder = SentenceTransformerEmbedder()
    vdb = ChromaDBVectorDB(dbpath=dbpath, embedder=embedder, distance_measure="cosine")
    vdb.initialize_db()
    vdb.initialize_collection("NBA_Data_CharLen")

    rag_agent = ChromaAgent(llm=llm, vectordb=vdb)
    rag_desc = "what happened during NBA games in the month of March 2026 based on individual game recaps"
    rag_kwargs = {"k": 5, "max_distance": 0.75, "show_citations": True}

    db_url = os.path.join(os.path.dirname(__file__), "..", "data", "NBA_DB.db")
    db_desc = """
    The database contains NBA statistics from 2020 to present. Tables: player_stats,
    players, team_stats, teams. Key views: v_master_player (player stats + names),
    v_master_teams (team stats + names), v_avg_stats (per-player season averages).
    Query the views — joins are already handled for you.
    """.strip()

    sql_agent = SQLiteAgent(llm=llm, database_url=db_url, db_desc=db_desc, include_detail=True)
    sql_desc = "the stats for individual NBA players and teams, per game or averaged"
    sql_kwargs = {"view_sql": True}

    return MultiAgent(
        llm=llm,
        agent_names=["Rag Agent", "SQL Agent"],
        agents=[rag_agent, sql_agent],
        agent_descriptions=[rag_desc, sql_desc],
        agent_query_kwargs=[rag_kwargs, sql_kwargs],
    )

# ── Load agent ────────────────────────────────────────────────────────────────
multi_agent = build_multi_agent()

# ── Chat history ──────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ── FIX 4: replace print() with actual Streamlit chat UI ─────────────────────
if prompt := st.chat_input("Ask me about NBA stats or game recaps..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = multi_agent.query(prompt, show_logic=True)
        st.markdown(response)

    st.session_state.messages.append({"role": "assistant", "content": response})
