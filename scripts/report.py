import sqlite3
import pandas as pd
import json
import os

DB_PATH = "data/patents.db"
REPORTS = "reports"
os.makedirs(REPORTS, exist_ok=True)

conn = sqlite3.connect(DB_PATH)

# ── Fetch data ─────────────────────────────────────
top_inventors = pd.read_sql("""
    SELECT name, COUNT(DISTINCT patent_id) AS patents
    FROM inventors WHERE name != ''
    GROUP BY inventor_id
    ORDER BY patents DESC LIMIT 10
""", conn)

top_companies = pd.read_sql("""
    SELECT name, COUNT(DISTINCT patent_id) AS patents
    FROM companies WHERE name IS NOT NULL
    GROUP BY company_id
    ORDER BY patents DESC LIMIT 10
""", conn)

patents_per_year = pd.read_sql("""
    SELECT year, COUNT(*) AS patents
    FROM patents WHERE year IS NOT NULL
    GROUP BY year ORDER BY year DESC LIMIT 10
""", conn)

total = pd.read_sql("SELECT COUNT(*) AS total FROM patents", conn)
total_patents = int(total["total"][0])

conn.close()

# ── Console Report ─────────────────────────────────
print("=" * 52)
print("         GLOBAL PATENT INTELLIGENCE REPORT")
print("=" * 52)
print(f"\nTotal Patents: {total_patents:,}")

print("\nTop 10 Inventors:")
for i, row in top_inventors.iterrows():
    print(f"  {i+1}. {row['name']} - {row['patents']:,} patents")

print("\nTop 10 Companies:")
for i, row in top_companies.iterrows():
    print(f"  {i+1}. {row['name']} - {row['patents']:,} patents")

print("\nPatents Per Year (Recent):")
for i, row in patents_per_year.iterrows():
    print(f"  {int(row['year'])}: {row['patents']:,} patents")

print("=" * 52)

# ── Export CSVs ────────────────────────────────────
top_inventors.to_csv(f"{REPORTS}/top_inventors.csv", index=False)
top_companies.to_csv(f"{REPORTS}/top_companies.csv", index=False)
patents_per_year.to_csv(f"{REPORTS}/country_trends.csv", index=False)
print("\nCSV reports saved to reports/")

# ── Export JSON ────────────────────────────────────
report = {
    "total_patents": total_patents,
    "top_inventors": top_inventors.to_dict(orient="records"),
    "top_companies": top_companies.to_dict(orient="records"),
    "patents_per_year": patents_per_year.to_dict(orient="records")
}
with open(f"{REPORTS}/report.json", "w") as f:
    json.dump(report, f, indent=2)
print("JSON report saved to reports/report.json")
