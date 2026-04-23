import streamlit as st
import sqlite3
import pandas as pd
import os

st.markdown("""
<style>
/* Main app background */
.stApp {
    background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%);
    color: white;
}

/* Make all text white */
html, body, [class*="css"]  {
    color: white;
}

/* Cards / containers */
.card {
    background-color: rgba(255, 255, 255, 0.06);
    padding: 20px;
    border-radius: 16px;
    border: 1px solid rgba(255,255,255,0.12);
    box-shadow: 0 4px 14px rgba(0,0,0,0.25);
}

/* Headers */
h1, h2, h3 {
    color: #f8fafc;
}

/* Subtext */
[data-testid="stCaptionContainer"] {
    color: #cbd5e1;
}

/* Metrics (fix ugly dark text) */
[data-testid="stMetricValue"] {
    color: white;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background-color: #E5E7EB;
}

/* Buttons */
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

def build_db():
    conn = sqlite3.connect("nba.sqlite")

    team_stats = pd.read_csv("team_stats.csv")
    teams = pd.read_csv("teams.csv")
    player_stats = pd.read_csv("player_stats.csv")
    players = pd.read_csv("players.csv")

    team_stats.to_sql("team_stats", conn, if_exists="replace", index=False)
    teams.to_sql("teams", conn, if_exists="replace", index=False)
    player_stats.to_sql("player_stats", conn, if_exists="replace", index=False)
    players.to_sql("players", conn, if_exists="replace", index=False)

    conn.close()

if not os.path.exists("nba.sqlite"):
    build_db()

@st.cache_data
def load_player_editor_data():
    conn = sqlite3.connect("nba.sqlite")

    player_stats = pd.read_sql_query("SELECT * FROM player_stats", conn)
    players = pd.read_sql_query("SELECT * FROM players", conn)

    conn.close()

    player_stats["game_date"] = pd.to_datetime(player_stats["game_date"], errors="coerce")
    player_stats = player_stats[player_stats["game_date"].dt.year >= 2023]

    players["player_name"] = (
        players["first_name"].fillna("") + " " + players["last_name"].fillna("")
    ).str.strip()

    player_df = player_stats.merge(
        players[["player_id", "player_name"]],
        on="player_id",
        how="left"
    )

    cols = ["player_name"] + [col for col in player_df.columns if col != "player_name"]
    player_df = player_df[cols]

    return player_df

st.title("Data Editor")

df = load_player_editor_data()
st.dataframe(df, use_container_width=True)

st.subheader("Edit Existing Row")

selected_id = st.selectbox(
    "Select row ID to edit",
    df["ID"].tolist()
)

selected_row = df[df["ID"] == selected_id].iloc[0]

st.write("Selected row:")
st.write(selected_row)
