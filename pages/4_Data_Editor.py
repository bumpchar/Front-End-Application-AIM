import streamlit as st
import sqlite3
import pandas as pd
import os

def build_db():
    st.write("Working directory files:", os.listdir())

    for file in ["team_stats.csv", "teams.csv", "player_stats.csv", "players.csv"]:
        st.write(file, "exists:", os.path.exists(file))
        if os.path.exists(file):
            st.write(file, "size:", os.path.getsize(file))

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
