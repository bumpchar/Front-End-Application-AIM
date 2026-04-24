import streamlit as st
import sqlite3
import pandas as pd
import os

st.markdown("""
<style>
.stApp {
    background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%);
    color: white;
}

h1, h2, h3, h4, p, label,
[data-testid="stMarkdownContainer"],
[data-testid="stWidgetLabel"],
[data-testid="stMetricValue"] {
    color: white !important;
}

.card {
    background-color: rgba(255, 255, 255, 0.06);
    padding: 20px;
    border-radius: 16px;
    border: 1px solid rgba(255,255,255,0.12);
    box-shadow: 0 4px 14px rgba(0,0,0,0.25);
}

[data-testid="stCaptionContainer"] {
    color: #cbd5e1 !important;
}

input, textarea,
div[data-baseweb="input"],
div[data-baseweb="select"],
div[data-baseweb="select"] > div {
    background-color: #1e293b !important;
    color: white !important;
}

div[data-baseweb="select"] * {
    color: white !important;
}

ul[role="listbox"],
ul[role="listbox"] li {
    background-color: #1e293b !important;
    color: white !important;
}

ul[role="listbox"] li:hover {
    background-color: #334155 !important;
}

section[data-testid="stSidebar"] {
    background-color: #E5E7EB;
}

section[data-testid="stSidebar"] * {
    color: #0f172a !important;
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

div[data-baseweb="input"] input {
    color: white !important;
    -webkit-text-fill-color: white !important;
}

/* Fix placeholder text */
div[data-baseweb="input"] input::placeholder {
    color: #cbd5e1 !important;
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

st.subheader("Update Row")

with st.form("update_form"):
    new_points = st.number_input("Points", value=int(selected_row["points"]))
    new_assists = st.number_input("Assists", value=int(selected_row["assists"]))
    new_blocks = st.number_input("Blocks", value=int(selected_row["blocks"]))
    new_steals = st.number_input("Steals", value=int(selected_row["steals"]))

    submitted = st.form_submit_button("Update Row")

    if submitted:
        conn = sqlite3.connect("nba.sqlite")
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE player_stats
            SET points = ?, assists = ?, blocks = ?, steals = ?
            WHERE ID = ?
        """, (new_points, new_assists, new_blocks, new_steals, selected_id))

        conn.commit()
        conn.close()

        st.cache_data.clear()
        st.success(f"Row {selected_id} updated!")
        st.rerun()

st.subheader("Delete Row")

if st.button("Delete Selected Row"):
    conn = sqlite3.connect("nba.sqlite")
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM player_stats
        WHERE ID = ?
    """, (selected_id,))

    conn.commit()
    conn.close()

    st.cache_data.clear()
    st.success(f"Row {selected_id} deleted!")
    st.rerun()

st.subheader("Insert New Row")

st.subheader("Insert New Row")

with st.form("insert_form"):
    insert_player_id = st.number_input("Player ID", min_value=0)
    insert_game_id = st.number_input("Game ID", min_value=0)
    insert_team_id = st.number_input("Player Team ID", min_value=0)
    insert_opp_id = st.number_input("Opponent Team ID", min_value=0)

    insert_game_date = st.date_input("Game Date")
    insert_game_time = st.text_input("Game Time (HH:MM:SS)")
    insert_game_type = st.selectbox("Game Type", ["Regular Season", "Playoffs"])

    insert_win = st.selectbox("Win", [0, 1])
    insert_home = st.selectbox("Home Game", [0, 1])

    insert_minutes = st.number_input("Minutes", min_value=0.0)

    insert_points = st.number_input("Points", min_value=0)
    insert_assists = st.number_input("Assists", min_value=0)
    insert_blocks = st.number_input("Blocks", min_value=0)
    insert_steals = st.number_input("Steals", min_value=0)

    insert_fga = st.number_input("Field Goals Attempted", min_value=0)
    insert_fgm = st.number_input("Field Goals Made", min_value=0)

    insert_3pa = st.number_input("3PT Attempted", min_value=0)
    insert_3pm = st.number_input("3PT Made", min_value=0)

    insert_fta = st.number_input("Free Throws Attempted", min_value=0)
    insert_ftm = st.number_input("Free Throws Made", min_value=0)

    insert_dreb = st.number_input("Defensive Rebounds", min_value=0)
    insert_oreb = st.number_input("Offensive Rebounds", min_value=0)

    insert_pf = st.number_input("Personal Fouls", min_value=0)
    insert_turnovers = st.number_input("Turnovers", min_value=0)
    insert_plus_minus = st.number_input("Plus/Minus", value=0)

    submitted = st.form_submit_button("Insert Row")

    if submitted:
        conn = sqlite3.connect("nba.sqlite")
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO player_stats (
                player_id, game_id, player_team_id, player_opponent_id,
                game_date, game_time, game_type, win, home,
                num_minutes, points, assists, blocks, steals,
                field_goals_attempted, field_goals_made,
                three_points_attempted, three_points_made,
                free_throws_attempted, free_throws_made,
                defensive_rebounds, offensive_rebounds,
                personal_fouls, turnovers, plus_minus_points
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            insert_player_id,
            insert_game_id,
            insert_team_id,
            insert_opp_id,
            str(insert_game_date),
            insert_game_time,
            insert_game_type,
            insert_win,
            insert_home,
            insert_minutes,
            insert_points,
            insert_assists,
            insert_blocks,
            insert_steals,
            insert_fga,
            insert_fgm,
            insert_3pa,
            insert_3pm,
            insert_fta,
            insert_ftm,
            insert_dreb,
            insert_oreb,
            insert_pf,
            insert_turnovers,
            insert_plus_minus
        ))

        conn.commit()
        conn.close()

        st.cache_data.clear()
        st.success("New row inserted!")
        st.rerun()
