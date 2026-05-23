import streamlit as st
import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.gridspec as gridspec

# ── Page Config ───────────────────────────────────────────
st.set_page_config(
    page_title="IPL Data Analysis",
    page_icon="🏏",
    layout="wide"
)

# ── Load Data ─────────────────────────────────────────────
@st.cache_data
def load_data():
    conn = sqlite3.connect("ipl.db")
    matches = pd.read_sql_query("SELECT * FROM matches", conn)
    deliveries = pd.read_sql_query("SELECT * FROM deliveries", conn)
    conn.close()
    return matches, deliveries

matches, deliveries = load_data()

# ── Header ────────────────────────────────────────────────
st.title("🏏 IPL Data Analysis (2008–2020)")
st.markdown("Analysing **260,000+ ball-by-ball records** using Python and SQL")
st.markdown("---")

# ── KPI Cards ─────────────────────────────────────────────
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Matches", len(matches))
col2.metric("Total Balls", len(deliveries))
col3.metric("Total Seasons", matches["season"].nunique())
col4.metric("Total Teams", matches["team1"].nunique())

st.markdown("---")

# ── Sidebar Filters ───────────────────────────────────────
st.sidebar.header("🔎 Filters")
seasons = sorted(matches["season"].unique())
selected_season = st.sidebar.selectbox("Select Season", ["All"] + list(seasons))

if selected_season != "All":
    filtered_matches = matches[matches["season"] == selected_season]
    match_ids = filtered_matches["id"].tolist()
    filtered_deliveries = deliveries[deliveries["match_id"].isin(match_ids)]
else:
    filtered_matches = matches
    filtered_deliveries = deliveries

st.sidebar.markdown(f"**{len(filtered_matches)} matches** in selection")

# ── Row 1: Team Wins + Top Batsmen ────────────────────────
col1, col2 = st.columns(2)

with col1:
    st.subheader("🏆 Most Wins by Team")
    wins = filtered_matches[filtered_matches["winner"].notna()] \
        .groupby("winner").size().reset_index(name="wins") \
        .sort_values("wins", ascending=False).head(8)
    fig, ax = plt.subplots(figsize=(7, 4))
    bars = ax.barh(wins["winner"], wins["wins"], color=sns.color_palette("Set2", len(wins)))
    ax.invert_yaxis()
    ax.set_xlabel("Wins")
    for bar, val in zip(bars, wins["wins"]):
        ax.text(bar.get_width() + 0.3, bar.get_y() + bar.get_height()/2,
                str(val), va="center", fontsize=9)
    st.pyplot(fig)
    plt.close()

with col2:
    st.subheader("🏏 Top 10 Batsmen by Runs")
    top_batsmen = filtered_deliveries.groupby("batter")["batsman_runs"] \
        .sum().reset_index(name="total_runs") \
        .sort_values("total_runs", ascending=False).head(10)
    fig, ax = plt.subplots(figsize=(7, 4))
    bars = ax.barh(top_batsmen["batter"], top_batsmen["total_runs"],
                   color=sns.color_palette("Blues_r", len(top_batsmen)))
    ax.invert_yaxis()
    ax.set_xlabel("Total Runs")
    for bar, val in zip(bars, top_batsmen["total_runs"]):
        ax.text(bar.get_width() + 10, bar.get_y() + bar.get_height()/2,
                str(val), va="center", fontsize=9)
    st.pyplot(fig)
    plt.close()

# ── Row 2: Top Bowlers + Toss Decision ───────────────────
col3, col4 = st.columns(2)

with col3:
    st.subheader("🎳 Top 10 Bowlers by Wickets")
    wickets = filtered_deliveries[
        filtered_deliveries["dismissal_kind"].notna() &
        ~filtered_deliveries["dismissal_kind"].isin(["run out", "retired hurt", "obstructing the field"])
    ].groupby("bowler").size().reset_index(name="wickets") \
     .sort_values("wickets", ascending=False).head(10)
    fig, ax = plt.subplots(figsize=(7, 4))
    bars = ax.barh(wickets["bowler"], wickets["wickets"],
                   color=sns.color_palette("Oranges_r", len(wickets)))
    ax.invert_yaxis()
    ax.set_xlabel("Wickets")
    for bar, val in zip(bars, wickets["wickets"]):
        ax.text(bar.get_width() + 0.3, bar.get_y() + bar.get_height()/2,
                str(val), va="center", fontsize=9)
    st.pyplot(fig)
    plt.close()

with col4:
    st.subheader("🪙 Toss Decision")
    toss = filtered_matches.groupby("toss_decision").size().reset_index(name="count")
    fig, ax = plt.subplots(figsize=(5, 4))
    ax.pie(toss["count"], labels=toss["toss_decision"],
           autopct="%1.1f%%", colors=["#3498db", "#e74c3c"],
           startangle=140, textprops={"fontsize": 12})
    st.pyplot(fig)
    plt.close()

# ── Row 3: Season Trend ───────────────────────────────────
st.markdown("---")
st.subheader("📈 Season-wise Average Runs per Ball")
season_avg = filtered_deliveries.merge(
    filtered_matches[["id", "season"]], left_on="match_id", right_on="id"
).groupby("season")["batsman_runs"].mean().reset_index()
season_avg.columns = ["season", "avg_runs"]
season_avg = season_avg.sort_values("season")

fig, ax = plt.subplots(figsize=(14, 4))
ax.plot(season_avg["season"].astype(str), season_avg["avg_runs"],
        marker="o", color="#2ecc71", linewidth=2.5, markersize=7)
ax.fill_between(season_avg["season"].astype(str), season_avg["avg_runs"],
                alpha=0.15, color="#2ecc71")
ax.set_xlabel("Season")
ax.set_ylabel("Avg Runs per Ball")
ax.tick_params(axis="x", rotation=45)
st.pyplot(fig)
plt.close()

# ── Row 4: Raw Data Table ─────────────────────────────────
st.markdown("---")
st.subheader("📋 Player of the Match Leaderboard")
potm = filtered_matches[filtered_matches["player_of_match"].notna()] \
    .groupby("player_of_match").size().reset_index(name="awards") \
    .sort_values("awards", ascending=False).head(10) \
    .reset_index(drop=True)
potm.index += 1
st.dataframe(potm, use_container_width=True)

st.markdown("---")
st.caption("Built with Python, SQL, SQLite, Pandas, Matplotlib & Streamlit | Data: Kaggle IPL Dataset")