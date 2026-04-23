import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide")

st.title("NBA Dashboard")

@st.cache_data
def load_data():
    team_stats = pd.read_csv("team_stats.csv")
    teams = pd.read_csv("teams.csv")
    player_stats = pd.read_csv("player_stats.csv")
    players = pd.read_csv("players.csv")

    # Dates
    team_stats["game_date"] = pd.to_datetime(team_stats["game_date"], errors="coerce")
    player_stats["game_date"] = pd.to_datetime(player_stats["game_date"], errors="coerce")

    # Clean team data
    team_stats = team_stats[team_stats["team_id"] != 0]
    team_stats = team_stats[team_stats["team_score"].notna()]
    team_stats = team_stats[team_stats["win"].notna()]

    # Team names
    teams["team_name"] = teams["city"].fillna("") + " " + teams["nickname"].fillna("")
    teams["team_name"] = teams["team_name"].str.strip()

    # Player names
    players["player_name"] = players["first_name"].fillna("") + " " + players["last_name"].fillna("")
    players["player_name"] = players["player_name"].str.strip()

    # Merge team names into team stats
    team_df = team_stats.merge(
        teams[["team_id", "team_name"]],
        on="team_id",
        how="left"
    )

    # Merge player names into player stats
    player_df = player_stats.merge(
        players[["player_id", "player_name"]],
        on="player_id",
        how="left"
    )

    return team_df, player_df


team_df, player_df = load_data()

# ---------- SIDEBAR ----------
st.sidebar.header("Filters")

team_names = sorted(team_df["team_name"].dropna().unique().tolist())
selected_team = st.sidebar.selectbox("Select Team", team_names)

location_filter = st.sidebar.selectbox("Location", ["All", "Home", "Away"])

filtered_team_df = team_df[team_df["team_name"] == selected_team].copy()

if location_filter == "Home":
    filtered_team_df = filtered_team_df[filtered_team_df["home"] == 1]
elif location_filter == "Away":
    filtered_team_df = filtered_team_df[filtered_team_df["home"] == 0]

# ---------- TEAM OVERVIEW ----------
st.subheader(f"{selected_team} Team Overview")

col1, col2, col3 = st.columns(3)
col1.metric("Games", len(filtered_team_df))
col2.metric("Avg Team Score", round(filtered_team_df["team_score"].mean(), 1))
col3.metric("Win Rate", f"{round(filtered_team_df['win'].mean() * 100, 1)}%")

st.divider()

# ---------- TEAM CHARTS ----------
monthly_df = filtered_team_df.copy()
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

# ---------- PLAYER SECTION ----------
st.divider()
st.subheader("Player Analysis")

player_names = sorted(player_df["player_name"].dropna().unique().tolist())
selected_player = st.selectbox("Select Player", player_names)

player_only_df = player_df[player_df["player_name"] == selected_player].copy()

# Use the actual likely column names in your file
points_col = "pts" if "pts" in player_only_df.columns else None
rebounds_col = "reb" if "reb" in player_only_df.columns else None
assists_col = "ast" if "ast" in player_only_df.columns else None

p1, p2, p3 = st.columns(3)

if points_col:
    p1.metric("Avg Points", round(player_only_df[points_col].mean(), 1))
else:
    p1.metric("Avg Points", "N/A")

if rebounds_col:
    p2.metric("Avg Rebounds", round(player_only_df[rebounds_col].mean(), 1))
else:
    p2.metric("Avg Rebounds", "N/A")

if assists_col:
    p3.metric("Avg Assists", round(player_only_df[assists_col].mean(), 1))
else:
    p3.metric("Avg Assists", "N/A")

col_c, col_d = st.columns(2)

with col_c:
    if points_col:
        player_monthly = player_only_df.copy()
        player_monthly["month"] = player_monthly["game_date"].dt.to_period("M").dt.to_timestamp()

        points_by_month = (
            player_monthly.groupby("month", as_index=False)[points_col]
            .mean()
            .sort_values("month")
        )

        fig3 = px.line(
            points_by_month,
            x="month",
            y=points_col,
            title=f"{selected_player} Average Points by Month"
        )
        st.plotly_chart(fig3, use_container_width=True)

with col_d:
    if points_col:
        recent_points = (
            player_only_df.sort_values("game_date", ascending=False)
            .head(10)[["game_date", points_col]]
            .sort_values("game_date")
        )

        fig4 = px.bar(
            recent_points,
            x="game_date",
            y=points_col,
            title=f"{selected_player} Recent Points"
        )
        st.plotly_chart(fig4, use_container_width=True)

# ---------- TABLES ----------
st.divider()

st.subheader("Recent Team Games")
display_team_df = filtered_team_df.sort_values("game_date", ascending=False)[
    ["game_date", "game_time", "team_name", "team_score", "win", "home"]
].copy()

display_team_df["win"] = display_team_df["win"].map({1: "Win", 0: "Loss"})
display_team_df["home"] = display_team_df["home"].map({1: "Home", 0: "Away"})
display_team_df["game_date"] = display_team_df["game_date"].dt.strftime("%Y-%m-%d")

st.dataframe(display_team_df.head(10), use_container_width=True, hide_index=True)

st.subheader("Recent Player Games")

player_table_cols = ["game_date", "player_name"]
if points_col:
    player_table_cols.append(points_col)
if rebounds_col:
    player_table_cols.append(rebounds_col)
if assists_col:
    player_table_cols.append(assists_col)

display_player_df = player_only_df.sort_values("game_date", ascending=False)[player_table_cols].copy()
display_player_df["game_date"] = display_player_df["game_date"].dt.strftime("%Y-%m-%d")

st.dataframe(display_player_df.head(10), use_container_width=True, hide_index=True)
