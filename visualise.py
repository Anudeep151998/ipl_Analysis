import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import seaborn as sns

DB_NAME = "ipl.db"

sns.set_theme(style="darkgrid")

def main():
    conn = sqlite3.connect(DB_NAME)

    fig = plt.figure(figsize=(18, 14))
    fig.suptitle("🏏 IPL Data Analysis (2008–2020)", fontsize=20, fontweight="bold", y=0.98)
    gs = gridspec.GridSpec(2, 2, figure=fig, hspace=0.45, wspace=0.35)

    # ── Chart 1: Top 8 teams by wins ──────────────────────
    ax1 = fig.add_subplot(gs[0, 0])
    df1 = pd.read_sql_query("""
        SELECT winner AS team, COUNT(*) AS wins
        FROM matches WHERE winner IS NOT NULL
        GROUP BY winner ORDER BY wins DESC LIMIT 8
    """, conn)
    bars = ax1.barh(df1["team"], df1["wins"], color=sns.color_palette("Set2", len(df1)))
    ax1.set_title("Most Wins by Team (All Time)", fontweight="bold")
    ax1.set_xlabel("Number of Wins")
    ax1.invert_yaxis()
    for bar, val in zip(bars, df1["wins"]):
        ax1.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height()/2,
                 str(val), va="center", fontsize=9)

    # ── Chart 2: Top 10 batsmen ───────────────────────────
    ax2 = fig.add_subplot(gs[0, 1])
    df2 = pd.read_sql_query("""
        SELECT batter, SUM(batsman_runs) AS total_runs
        FROM deliveries GROUP BY batter
        ORDER BY total_runs DESC LIMIT 10
    """, conn)
    bars2 = ax2.barh(df2["batter"], df2["total_runs"], color=sns.color_palette("Blues_r", len(df2)))
    ax2.set_title("Top 10 Batsmen by Total Runs", fontweight="bold")
    ax2.set_xlabel("Total Runs")
    ax2.invert_yaxis()
    for bar, val in zip(bars2, df2["total_runs"]):
        ax2.text(bar.get_width() + 10, bar.get_y() + bar.get_height()/2,
                 str(val), va="center", fontsize=9)

    # ── Chart 3: Season-wise avg score ───────────────────
    ax3 = fig.add_subplot(gs[1, 0])
    df3 = pd.read_sql_query("""
        SELECT m.season, ROUND(AVG(d.batsman_runs), 3) AS avg_runs
        FROM deliveries d JOIN matches m ON d.match_id = m.id
        GROUP BY m.season ORDER BY m.season
    """, conn)
    ax3.plot(df3["season"].astype(str), df3["avg_runs"], marker="o",
             color="#2ecc71", linewidth=2.5, markersize=7)
    ax3.fill_between(df3["season"].astype(str), df3["avg_runs"], alpha=0.15, color="#2ecc71")
    ax3.set_title("Season-wise Average Runs per Ball", fontweight="bold")
    ax3.set_xlabel("Season")
    ax3.set_ylabel("Avg Runs")
    ax3.tick_params(axis="x", rotation=45)

    # ── Chart 4: Toss decision pie ────────────────────────
    ax4 = fig.add_subplot(gs[1, 1])
    df4 = pd.read_sql_query("""
        SELECT toss_decision, COUNT(*) AS count
        FROM matches GROUP BY toss_decision
    """, conn)
    ax4.pie(df4["count"], labels=df4["toss_decision"],
            autopct="%1.1f%%", colors=["#3498db", "#e74c3c"],
            startangle=140, textprops={"fontsize": 12})
    ax4.set_title("Toss Decision: Field vs Bat", fontweight="bold")

    conn.close()

    plt.savefig("ipl_analysis_dashboard.png", dpi=150, bbox_inches="tight")
    print("✅ Dashboard saved as 'ipl_analysis_dashboard.png'")
    plt.show()


if __name__ == "__main__":
    main()