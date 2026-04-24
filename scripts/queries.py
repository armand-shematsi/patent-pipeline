import sqlite3
import pandas as pd
import json
import os

DB_PATH = "data/patents.db"
REPORTS = "reports"
os.makedirs(REPORTS, exist_ok=True)

conn = sqlite3.connect(DB_PATH)

# ── Q1: Top Inventors ──────────────────────────────
print("\nQ1: Top Inventors")
q1 = pd.read_sql("""
    SELECT name, COUNT(DISTINCT patent_id) AS patent_count
    FROM inventors
    WHERE name != ''
    GROUP BY inventor_id
    ORDER BY patent_count DESC
    LIMIT 10
""", conn)
print(q1.to_string(index=False))

# ── Q2: Top Companies ──────────────────────────────
print("\nQ2: Top Companies")
q2 = pd.read_sql("""
    SELECT name, COUNT(DISTINCT patent_id) AS patent_count
    FROM companies
    WHERE name IS NOT NULL
    GROUP BY company_id
    ORDER BY patent_count DESC
    LIMIT 10
""", conn)
print(q2.to_string(index=False))

# ── Q3: Top Countries ──────────────────────────────
print("\nQ3: Top Countries")
q3 = pd.read_sql("""
    SELECT country, COUNT(DISTINCT patent_id) AS patent_count
    FROM inventors
    WHERE country IS NOT NULL
    GROUP BY country
    ORDER BY patent_count DESC
    LIMIT 10
""", conn)
print(q3.to_string(index=False))

# ── Q4: Patents Per Year ───────────────────────────
print("\nQ4: Patents Per Year")
q4 = pd.read_sql("""
    SELECT year, COUNT(*) AS patent_count
    FROM patents
    WHERE year IS NOT NULL
    GROUP BY year
    ORDER BY year DESC
    LIMIT 20
""", conn)
print(q4.to_string(index=False))

# ── Q5: JOIN Query ─────────────────────────────────
print("\nQ5: Patents with Inventors and Companies")
q5 = pd.read_sql("""
    SELECT p.patent_id, p.title, i.name AS inventor, c.name AS company
    FROM patents p
    JOIN inventors i ON p.patent_id = i.patent_id
    LEFT JOIN companies c ON p.patent_id = c.patent_id
    LIMIT 10
""", conn)
print(q5.to_string(index=False))

# ── Q6: CTE Query ──────────────────────────────────
print("\nQ6: CTE - Top 10 inventors with more than 50 patents")
q6 = pd.read_sql("""
    WITH inventor_counts AS (
        SELECT inventor_id, name, COUNT(DISTINCT patent_id) AS patent_count
        FROM inventors
        GROUP BY inventor_id
    )
    SELECT name, patent_count
    FROM inventor_counts
    WHERE patent_count > 50
    ORDER BY patent_count DESC
    LIMIT 10
""", conn)
print(q6.to_string(index=False))

# ── Q7: Ranking Query ──────────────────────────────
print("\nQ7: Ranking Inventors using Window Function")
q7 = pd.read_sql("""
    SELECT name, patent_count,
           RANK() OVER (ORDER BY patent_count DESC) AS rank
    FROM (
        SELECT inventor_id, name, COUNT(DISTINCT patent_id) AS patent_count
        FROM inventors
        GROUP BY inventor_id
    )
    LIMIT 10
""", conn)
print(q7.to_string(index=False))

# ── Export CSVs ────────────────────────────────────
print("\nExporting CSV reports...")
q1.to_csv(f"{REPORTS}/top_inventors.csv", index=False)
q2.to_csv(f"{REPORTS}/top_companies.csv", index=False)
q4.to_csv(f"{REPORTS}/country_trends.csv", index=False)
print("  CSVs saved to reports/")

# ── Export JSON ────────────────────────────────────
print("Exporting JSON report...")
report = {
    "total_patents": 9454161,
    "top_inventors": q1.head(5).to_dict(orient="records"),
    "top_companies": q2.head(5).to_dict(orient="records"),
    "patents_per_year": q4.head(5).to_dict(orient="records")
}
with open(f"{REPORTS}/report.json", "w") as f:
    json.dump(report, f, indent=2)
print("  JSON saved to reports/report.json")

conn.close()
print("\nAll queries done!")
