import streamlit as st
import sqlite3
import pandas as pd
import os

import streamlit as st
import sqlite3
import pandas as pd
import os

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

build_db()

def load_player_editor_data():
    conn = sqlite3.connect("nba.sqlite")

    player_stats = pd.read_sql_query("SELECT * FROM player_stats", conn)
    players = pd.read_sql_query("SELECT * FROM players", conn)

    conn.close()

    # dates
    player_stats["game_date"] = pd.to_datetime(player_stats["game_date"], errors="coerce")

    # keep recent rows only
    player_stats = player_stats[player_stats["game_date"].dt.year >= 2023]

    # create player name
    players["player_name"] = (
        players["first_name"].fillna("") + " " + players["last_name"].fillna("")
    ).str.strip()

    # merge player name into stats
    player_df = player_stats.merge(
        players[["player_id", "player_name"]],
        on="player_id",
        how="left"
    )

    return player_df

st.title("Data Editor")
df = df = load_player_editor_data()
st.dataframe(df)
