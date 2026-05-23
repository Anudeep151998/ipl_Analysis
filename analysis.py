import sqlite3
import pandas as pd

DB_NAME = "ipl.db"

def run_query(conn, title, sql):
    print(f"\n{'='*55}")
    print(f"📊 {title}")
    print('='*55)
    df = pd.read_sql_query(sql, conn)
    print(df.to_string(index=False))
    return df


def main():
    conn = sqlite3.connect(DB_NAME)

    # Print actual column names so we can verify
    print("🔍 deliveries columns:", pd.read_sql_query("SELECT * FROM deliveries LIMIT 1", conn).columns.tolist())
    print("🔍 matches columns:", pd.read_sql_query("SELECT * FROM matches LIMIT 1", conn).columns.tolist())

    # ── Q1: Most wins by team ─────────────────────────────
    run_query(conn, "Most Match Wins by Team (All Time)", """
        SELECT winner AS team, COUNT(*) AS wins
        FROM matches
        WHERE winner IS NOT NULL
        GROUP BY winner
        ORDER BY wins DESC
        LIMIT 8
    """)

    # ── Q2: Top 10 batsmen by total runs ──────────────────
    run_query(conn, "Top 10 Batsmen by Total Runs", """
        SELECT batter, SUM(batsman_runs) AS total_runs
        FROM deliveries
        GROUP BY batter
        ORDER BY total_runs DESC
        LIMIT 10
    """)

    # ── Q3: Top 10 bowlers by wickets ─────────────────────
    run_query(conn, "Top 10 Bowlers by Wickets", """
        SELECT bowler, COUNT(*) AS wickets
        FROM deliveries
        WHERE dismissal_kind NOT IN ('run out', 'retired hurt', 'obstructing the field')
          AND dismissal_kind IS NOT NULL
        GROUP BY bowler
        ORDER BY wickets DESC
        LIMIT 10
    """)

    # ── Q4: Win % batting first vs chasing ────────────────
    run_query(conn, "Win % — Batting First vs Chasing", """
        SELECT
            CASE WHEN winner = team1 THEN 'Batting First'
                 WHEN winner = team2 THEN 'Chasing'
                 ELSE 'No Result' END AS result_type,
            COUNT(*) AS matches,
            ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM matches WHERE winner IS NOT NULL), 1) AS percentage
        FROM matches
        WHERE winner IS NOT NULL
        GROUP BY result_type
    """)

    # ── Q5: Season with highest average total score ───────
    run_query(conn, "Season-wise Average Runs per Match", """
        SELECT m.season,
               ROUND(AVG(d.total_runs), 2) AS avg_runs_per_ball
        FROM deliveries d
        JOIN matches m ON d.match_id = m.id
        GROUP BY m.season
        ORDER BY m.season
    """)

    # ── Q6: Player of the match leaderboard ───────────────
    run_query(conn, "Player of the Match — Top 10", """
        SELECT player_of_match, COUNT(*) AS awards
        FROM matches
        WHERE player_of_match IS NOT NULL
        GROUP BY player_of_match
        ORDER BY awards DESC
        LIMIT 10
    """)

    # ── Q7: Toss decision analysis ────────────────────────
    run_query(conn, "Toss Decision: Field vs Bat", """
        SELECT toss_decision, COUNT(*) AS times_chosen,
               ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM matches), 1) AS percentage
        FROM matches
        GROUP BY toss_decision
    """)

    # ── Q8: Most sixes by batsman ─────────────────────────
    run_query(conn, "Most Sixes — Top 10 Batsmen", """
        SELECT batter, COUNT(*) AS sixes
        FROM deliveries
        WHERE batsman_runs = 6
        GROUP BY batter
        ORDER BY sixes DESC
        LIMIT 10
    """)

    conn.close()
    print("\n\n✅ All queries done! Now run: python visualise.py")


if __name__ == "__main__":
    main()