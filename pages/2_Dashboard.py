import streamlit as st
import pandas as pd
import plotly.express as px

st.title("NBA News Dashboard")
st.write("Explore recent NBA news with filters and interactive charts.")

@st.cache_data
def load_data():
    df = pd.read_csv("data/nba_news.csv")
    df["published"] = pd.to_datetime(df["published"], errors="coerce")
    return df

df = load_data()

st.sidebar.header("Filters")

teams = ["All"] + sorted(df["team"].dropna().unique().tolist())
selected_team = st.sidebar.selectbox("Choose a team", teams)

sources = sorted(df["source"].dropna().unique().tolist())
selected_sources = st.sidebar.multiselect(
    "Choose source(s)",
    sources,
    default=sources
)

min_sentiment = float(df["sentiment"].min())
max_sentiment = float(df["sentiment"].max())

selected_sentiment = st.sidebar.slider(
    "Sentiment range",
    min_value=min_sentiment,
    max_value=max_sentiment,
    value=(min_sentiment, max_sentiment)
)

filtered_df = df.copy()

if selected_team != "All":
    filtered_df = filtered_df[filtered_df["team"] == selected_team]

filtered_df = filtered_df[filtered_df["source"].isin(selected_sources)]

filtered_df = filtered_df[
    (filtered_df["sentiment"] >= selected_sentiment[0]) &
    (filtered_df["sentiment"] <= selected_sentiment[1])
]

col1, col2, col3 = st.columns(3)
col1.metric("Articles", len(filtered_df))
col2.metric("Sources", filtered_df["source"].nunique())
col3.metric("Teams Mentioned", filtered_df["team"].nunique())

st.divider()

col_a, col_b = st.columns(2)

with col_a:
    team_counts = filtered_df["team"].value_counts().reset_index()
    team_counts.columns = ["team", "count"]

    fig_team = px.bar(team_counts, x="team", y="count", title="Articles by Team")
    st.plotly_chart(fig_team, use_container_width=True)

with col_b:
    source_counts = filtered_df["source"].value_counts().reset_index()
    source_counts.columns = ["source", "count"]

    fig_source = px.pie(source_counts, names="source", values="count", title="Source Share")
    st.plotly_chart(fig_source, use_container_width=True)

trend_df = filtered_df.dropna(subset=["published"]).copy()
trend_df["date"] = trend_df["published"].dt.date
daily_counts = trend_df.groupby("date").size().reset_index(name="count")

fig_trend = px.line(daily_counts, x="date", y="count", title="Article Volume Over Time")
st.plotly_chart(fig_trend, use_container_width=True)

st.subheader("Filtered Data")
st.dataframe(filtered_df, use_container_width=True)
