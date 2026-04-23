import streamlit as st
import pandas as pd
import plotly.express as px

st.title("NBA Dashboard")

@st.cache_data
def load_data():
    df = pd.read_csv("team_stats.csv")
    df["game_date"] = pd.to_datetime(df["game_date"], errors="coerce")
    return df

df = load_data()

st.write("Rows:", len(df))

team_ids = sorted(df["team_id"].dropna().unique().tolist())
selected_team = st.sidebar.selectbox("Select Team ID", team_ids)

filtered_df = df[df["team_id"] == selected_team]

col1, col2, col3 = st.columns(3)
col1.metric("Games", len(filtered_df))
col2.metric("Avg Team Score", round(filtered_df["team_score"].mean(), 2))
col3.metric("Win Rate", round(filtered_df["win"].mean() * 100, 1))

wins_by_date = (
    filtered_df.groupby("game_date", as_index=False)["win"]
    .mean()
    .sort_values("game_date")
)

score_by_date = (
    filtered_df.groupby("game_date", as_index=False)["team_score"]
    .mean()
    .sort_values("game_date")
)

fig1 = px.line(
    score_by_date,
    x="game_date",
    y="team_score",
    title="Average Team Score Over Time"
)
st.plotly_chart(fig1, use_container_width=True)

fig2 = px.line(
    wins_by_date,
    x="game_date",
    y="win",
    title="Win Rate Over Time"
)
st.plotly_chart(fig2, use_container_width=True)

st.subheader("Filtered Team Data")
st.dataframe(filtered_df, use_container_width=True)
