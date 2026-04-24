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

from intro_to_agents.rag.embedders import SentenceTransformerEmbedder
from intro_to_agents.rag.vector_databases import ChromaDBVectorDB

from intro_to_agents.agents.llms import OpenAILLM
from intro_to_agents.agents.agents import MultiAgent, ChromaAgent, SQLiteAgent, ExcelAgent

# ignore warnings
import warnings
warnings.filterwarnings('ignore')

# Make sure you have a .env file with your OpenAI API key
    # ex: OPENAI_API_KEY = "abcdefg12345"
    # a .env file is a text file that contains environment variables
    # it is used to store sensitive information (like API keys) in a secure way
    # it is NOT included in the repository (you don't want to share your API key with others), so you will need to create it yourself
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

# Instantiate the LLM
model = "gpt-5-mini" # you can change the model to whatever you want (see from intro_to_agents.agents.llms import OPENAI_TOKEN_LIMITS)
llm = OpenAILLM(api_key=api_key, model=model)

# Load to vector database
# @ You: Identify the path where your vector database that you previously loaded is located
dbpath = r"C:\Users\eoinr\Downloads"

# Instantiate the same embedder you used to load the vector database
embedder = SentenceTransformerEmbedder()

# Instantiate the vector database
vdb = ChromaDBVectorDB(dbpath = dbpath, 
                       embedder = embedder, 
                       distance_measure = "cosine")

# Connect to vector database
vdb.initialize_db()

# Attach to a collection
vdb.initialize_collection("NBA_Data_CharLen")

# Instantiate the RAG Agent
rag_agent = ChromaAgent(llm = llm, 
                        vectordb = vdb)

# Build the Agent "Card"
    # Provide a description of the Agent as to what types of questions it can answer
        # So "This agent can answer questions about..." Your description
rag_desc = "what happened during NBA games in the month of March 2026 based on individual game recaps"

    # Provide the kwargs for how you want the  Agent to perform
rag_kwargs = {"k": 5, 
              "max_distance": 0.75, 
              "show_citations": True}
# @You: Locate your SQLite database file
db_url = "../data/NBA_DB.db"

# Provide context about the database to the LLM
db_desc = """
The database contains data related to NBA statistics from 2020 to present. There are four tables: player_stats, players, team_stats, teams. The player stats table 
shows individual player's stats for each player for each game using a player id number. The players table is the master-file for players where players and thier corresponding
player_id are listed. The team_stats table shows stats for every team for every game using a team id number. Team ID numbers are stored in the teams table along with the team location
nick names and some others.

There are three views in this data base which you will be mostly querying from. They are v_master_player, v_master_team, and v_avg_stats. v_master_player joins the player table and the 
player_stats table to create a view with the stats of each player and their player name for each game. Similarly, the v_master_teams view joins the teams and team table and the team_stats
table to create a view with every teams stats for each game and the team names. These views are usefull as you do not need to do any joins to search by player or team name. v_avg_stats has
all players average stats grouped by year. Again, you will almost exlusively be querying on these views.
""".rstrip()

# Instantiate the SQLiteAgent
sql_agent = SQLiteAgent(llm = llm, 
                        database_url = db_url, 
                        db_desc = db_desc, 
                        include_detail = True)

# Build the Agent "Card"
    # Provide a description of the Agent as to what types of questions it can answer
        # So "This agent can answer questions about..." Your description
sql_desc = "the stats for individual NBA players and teams. Stats can be pulled on a per game basis or averaged out"

    # Provide the kwargs for how you want the Agent to perform
sql_kwargs = {"view_sql": True}
# Build the MultiAgent
    # Provide the names of the Agents
agent_names = ["Rag Agent", "SQL Agent"]

    # Provide the Agents themselves
agents = [rag_agent, sql_agent]

    # Provide the descriptions of the Agents
agent_descriptions = [rag_desc, sql_desc]

    # Provide the kwargs for how you want the MultiAgent to perform
agent_query_kwargs = [rag_kwargs, sql_kwargs]

# Instantiate the MultiAgent
multi_agent = MultiAgent(llm = llm, 
                         agent_names = agent_names, 
                         agents = agents, 
                         agent_descriptions = agent_descriptions, 
                         agent_query_kwargs = agent_query_kwargs)
# Query MultiAgent
print(multi_agent.query("Which Heat player had a career-high game on March 12, 2026?", 
                        show_logic = True))
