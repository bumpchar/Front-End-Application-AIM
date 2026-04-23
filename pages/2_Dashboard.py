import streamlit as st
import pandas as pd
import plotly.express as px

st.title("NBA Dashboard")

@st.cache_data
def load_data():
    team_stats = pd.read_csv("team_stats.csv")
    teams = pd.read_csv("teams.csv")

    team_stats["game_date"] = pd.to_datetime(team_stats["game_date"], errors="coerce")

    # remove bad rows
    team_stats = team_stats[team_stats["team_id"] != 0]
    team_stats = team_stats[team_stats["team_score"].notna()]
    team_stats = team_stats[team_stats["win"].notna()]

    # make team names
    teams["team_name"] = teams["city"] + " " + teams["nickname"]

    # merge team names into stats
    df = team_stats.merge(
        teams[["team_id", "team_name"]],
        on="team_id",
        how="left"
    )

    return df

df = load_data()

st.write("Rows:", len(df))

team_names = sorted(df["team_name"].dropna().unique().tolist())
selected_team = st.sidebar.selectbox("Select Team", team_names)

filtered_df = df[df["team_name"] == selected_team]

col1, col2, col3 = st.columns(3)
col1.metric("Games", len(filtered_df))
col2.metric("Avg Team Score", round(filtered_df["team_score"].mean(), 2))
col3.metric("Win Rate", f"{round(filtered_df['win'].mean() * 100, 1)}%")

score_by_date = (
    filtered_df.groupby("game_date", as_index=False)["team_score"]
    .mean()
    .sort_values("game_date")
)

wins_by_date = (
    filtered_df.groupby("game_date", as_index=False)["win"]
    .mean()
    .sort_values("game_date")
)

fig1 = px.line(
    score_by_date,
    x="game_date",
    y="team_score",
    title="Average Team Score Over Time",
    markers=True
)
st.plotly_chart(fig1, use_container_width=True)

fig2 = px.line(
    wins_by_date,
    x="game_date",
    y="win",
    title="Win Rate Over Time",
    markers=True
)
st.plotly_chart(fig2, use_container_width=True)

st.subheader("Filtered Team Data")
st.dataframe(filtered_df, use_container_width=True)
