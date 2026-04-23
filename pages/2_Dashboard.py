import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide")

st.title("NBA Dashboard")

@st.cache_data
def load_data():
    team_stats = pd.read_csv("team_stats.csv")
    teams = pd.read_csv("teams.csv")

    team_stats["game_date"] = pd.to_datetime(team_stats["game_date"], errors="coerce")

    # clean data
    team_stats = team_stats[team_stats["team_id"] != 0]
    team_stats = team_stats[team_stats["team_score"].notna()]
    team_stats = team_stats[team_stats["win"].notna()]

    teams["team_name"] = teams["city"] + " " + teams["nickname"]

    df = team_stats.merge(
        teams[["team_id", "team_name"]],
        on="team_id",
        how="left"
    )

    return df

df = load_data()

# ---------- Sidebar ----------
st.sidebar.header("Filters")

team_names = sorted(df["team_name"].dropna().unique().tolist())
selected_team = st.sidebar.selectbox("Select Team", team_names)

location_filter = st.sidebar.selectbox("Location", ["All", "Home", "Away"])

filtered_df = df[df["team_name"] == selected_team].copy()

if location_filter == "Home":
    filtered_df = filtered_df[filtered_df["home"] == 1]
elif location_filter == "Away":
    filtered_df = filtered_df[filtered_df["home"] == 0]

# ---------- KPIs ----------
col1, col2, col3 = st.columns(3)
col1.metric("Games", len(filtered_df))
col2.metric("Avg Team Score", round(filtered_df["team_score"].mean(), 1))
col3.metric("Win Rate", f"{round(filtered_df['win'].mean() * 100, 1)}%")

st.divider()

# ---------- Aggregate charts ----------
monthly_df = filtered_df.copy()
monthly_df["month"] = monthly_df["game_date"].dt.to_period("M").dt.to_timestamp()

score_monthly = (
    monthly_df.groupby("month", as_index=False)["team_score"]
    .mean()
    .sort_values("month")
)

win_monthly = (
    monthly_df.groupby("month", as_index=False)["win"]
    .mean()
    .sort_values("month")
)

col_a, col_b = st.columns(2)

with col_a:
    fig1 = px.line(
        score_monthly,
        x="month",
        y="team_score",
        title="Average Team Score by Month"
    )
    st.plotly_chart(fig1, use_container_width=True)

with col_b:
    fig2 = px.bar(
        win_monthly,
        x="month",
        y="win",
        title="Monthly Win Rate"
    )
    fig2.update_yaxes(tickformat=".0%")
    st.plotly_chart(fig2, use_container_width=True)

# ---------- Cleaner recent games table ----------
st.subheader("Recent Games")

display_df = filtered_df.sort_values("game_date", ascending=False)[
    ["game_date", "game_time", "team_name", "team_score", "win", "home"]
].copy()

display_df["win"] = display_df["win"].map({1: "Win", 0: "Loss"})
display_df["home"] = display_df["home"].map({1: "Home", 0: "Away"})
display_df["game_date"] = display_df["game_date"].dt.strftime("%Y-%m-%d")

st.dataframe(display_df, use_container_width=True, hide_index=True)
