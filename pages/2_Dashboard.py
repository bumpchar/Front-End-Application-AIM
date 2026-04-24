import streamlit as st
import pandas as pd
import plotly.express as px

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

.stButton > button:hover {
    background-color: #ea580c;
    color: white;
}

section[data-testid="stSidebar"] div[data-baseweb="select"],
section[data-testid="stSidebar"] div[data-baseweb="select"] > div,
section[data-testid="stSidebar"] div[data-baseweb="input"] {
    background-color: white !important;
    color: #0f172a !important;
}

section[data-testid="stSidebar"] div[data-baseweb="select"] * {
    color: #0f172a !important;
}

section[data-testid="stSidebar"] input {
    background-color: white !important;
    color: #0f172a !important;
}
</style>
""", unsafe_allow_html=True)

st.set_page_config(layout="wide")

st.title("NBA Dashboard")

@st.cache_data
def load_data():
    team_stats = pd.read_csv("team_stats.csv")
    teams = pd.read_csv("teams.csv")
    player_stats = pd.read_csv("player_stats.csv")
    players = pd.read_csv("players.csv")

    # dates
    team_stats["game_date"] = pd.to_datetime(team_stats["game_date"], errors="coerce")
    player_stats["game_date"] = pd.to_datetime(player_stats["game_date"], errors="coerce")

    # clean team data
    team_stats = team_stats[team_stats["team_id"] != 0]
    team_stats = team_stats[team_stats["team_score"].notna()]
    team_stats = team_stats[team_stats["win"].notna()]

    # keep recent player data only so dropdown is not insane
    player_stats = player_stats[player_stats["game_date"].dt.year >= 2023]

    # names
    teams["team_name"] = teams["city"].fillna("") + " " + teams["nickname"].fillna("")
    teams["team_name"] = teams["team_name"].str.strip()

    players["player_name"] = players["first_name"].fillna("") + " " + players["last_name"].fillna("")
    players["player_name"] = players["player_name"].str.strip()

    # merge team names
    team_df = team_stats.merge(
        teams[["team_id", "team_name"]],
        on="team_id",
        how="left"
    )

    # merge player names
    player_df = player_stats.merge(
        players[["player_id", "player_name"]],
        on="player_id",
        how="left"
    )

    return team_df, player_df


team_df, player_df = load_data()

# SIDEBAR 
st.sidebar.header("Filters")

team_names = sorted(team_df["team_name"].dropna().unique().tolist())
selected_team = st.sidebar.selectbox("Select Team", team_names)

location_filter = st.sidebar.selectbox("Location", ["All", "Home", "Away"])

filtered_team_df = team_df[team_df["team_name"] == selected_team].copy()

if location_filter == "Home":
    filtered_team_df = filtered_team_df[filtered_team_df["home"] == 1]
elif location_filter == "Away":
    filtered_team_df = filtered_team_df[filtered_team_df["home"] == 0]

# -TEAM OVERVIEW 
st.subheader(f"{selected_team} Team Overview")

col1, col2, col3 = st.columns(3)
col1.metric("Games", len(filtered_team_df))
col2.metric("Avg Team Score", round(filtered_team_df["team_score"].mean(), 1))
col3.metric("Win Rate", f"{round(filtered_team_df['win'].mean() * 100, 1)}%")

st.divider()

# - TEAM CHARTS 
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

# -PLAYER SECTION -
st.divider()
st.subheader("Player Analysis")

# show actual columns so you can see the right stat names
with st.expander("See player_stats column names"):
    st.write(player_df.columns.tolist())

# limit dropdown to players with recent games only
recent_players = (
    player_df.dropna(subset=["player_name"])
    .groupby("player_name")
    .size()
    .reset_index(name="games")
)

recent_players = recent_players[recent_players["games"] >= 10]
player_names = sorted(recent_players["player_name"].tolist())

selected_player = st.selectbox("Select Player", player_names)

player_only_df = player_df[player_df["player_name"] == selected_player].copy()

# try several likely stat column names
def pick_col(df, options):
    for col in options:
        if col in df.columns:
            return col
    return None

points_col = pick_col(player_only_df, ["pts", "points", "point"])
rebounds_col = pick_col(player_only_df, ["reb", "rebounds", "trb"])
assists_col = pick_col(player_only_df, ["ast", "assists"])

p1, p2, p3 = st.columns(3)

p1.metric("Avg Points", round(player_only_df[points_col].mean(), 1) if points_col else "N/A")
p2.metric("Avg Rebounds", round(player_only_df[rebounds_col].mean(), 1) if rebounds_col else "N/A")
p3.metric("Avg Assists", round(player_only_df[assists_col].mean(), 1) if assists_col else "N/A")

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

# -TABLES
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
