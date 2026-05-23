import pandas as pd
import sqlite3
import os
import zipfile

DB_NAME = "ipl.db"
MATCHES_CSV = "matches.csv"
DELIVERIES_CSV = "deliveries.csv"

def run_query(conn, title, sql):
    print(f"\n{'='*55}")
    print(f"📊 {title}")
    print('='*55)
    df = pd.read_sql_query(sql, conn)
    print(df.to_string(index=False))
    return df

def unzip_if_needed():
    if os.path.exists(DELIVERIES_CSV):
        print("deliveries.csv already extracted.")
        return True
    for zname in ["deliveries.csv.zip", "deliveries.zip", "archive.zip"]:
        if os.path.exists(zname):
            print(f"Extracting {zname}...")
            with zipfile.ZipFile(zname, 'r') as z:
                z.extractall(".")
            print("Extracted successfully.")
            return True
    print("ERROR: deliveries CSV or zip not found.")
    return False

def main():
    if not unzip_if_needed():
        return

    print("\nLoading CSVs...")
    matches = pd.read_csv(MATCHES_CSV)
    deliveries = pd.read_csv(DELIVERIES_CSV)

    print(f"  matches.csv    -> {len(matches)} rows")
    print(f"  deliveries.csv -> {len(deliveries)} rows")
    print(f"  deliveries columns: {deliveries.columns.tolist()}")

    conn = sqlite3.connect(DB_NAME)
    matches.to_sql("matches", conn, if_exists="replace", index=False)
    deliveries.to_sql("deliveries", conn, if_exists="replace", index=False)

    # ── Queries using correct column names ────────────────
    run_query(conn, "Most Match Wins by Team", """
        SELECT winner AS team, COUNT(*) AS wins
        FROM matches WHERE winner IS NOT NULL
        GROUP BY winner ORDER BY wins DESC LIMIT 8
    """)

    run_query(conn, "Top 10 Batsmen by Total Runs", """
        SELECT batter, SUM(batsman_runs) AS total_runs
        FROM deliveries
        GROUP BY batter ORDER BY total_runs DESC LIMIT 10
    """)

    run_query(conn, "Top 10 Bowlers by Wickets", """
        SELECT bowler, COUNT(*) AS wickets
        FROM deliveries
        WHERE dismissal_kind NOT IN ('run out','retired hurt','obstructing the field')
          AND dismissal_kind IS NOT NULL
        GROUP BY bowler ORDER BY wickets DESC LIMIT 10
    """)

    run_query(conn, "Toss Decision: Field vs Bat", """
        SELECT toss_decision, COUNT(*) AS times,
               ROUND(COUNT(*)*100.0/(SELECT COUNT(*) FROM matches),1) AS pct
        FROM matches GROUP BY toss_decision
    """)

    run_query(conn, "Player of the Match Top 10", """
        SELECT player_of_match, COUNT(*) AS awards
        FROM matches WHERE player_of_match IS NOT NULL
        GROUP BY player_of_match ORDER BY awards DESC LIMIT 10
    """)

    run_query(conn, "Most Sixes - Top 10", """
        SELECT batter, COUNT(*) AS sixes
        FROM deliveries WHERE batsman_runs = 6
        GROUP BY batter ORDER BY sixes DESC LIMIT 10
    """)

    conn.close()
    print("\n✅ All done! Now run: python visualise.py")

if __name__ == "__main__":
    main()