import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import os

DB_PATH = "data/patents.db"
REPORTS = "reports"
os.makedirs(REPORTS, exist_ok=True)

conn = sqlite3.connect(DB_PATH)

# ── Data ───────────────────────────────────────────
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
    GROUP BY year ORDER BY year ASC
""", conn)

conn.close()

# ── Chart 1: Top 10 Inventors ──────────────────────
plt.figure(figsize=(12, 6))
plt.barh(top_inventors["name"][::-1], top_inventors["patents"][::-1], color="steelblue")
plt.xlabel("Number of Patents")
plt.title("Top 10 Inventors by Patent Count")
plt.tight_layout()
plt.savefig(f"{REPORTS}/top_inventors.png")
plt.close()
print("Saved top_inventors.png")

# ── Chart 2: Top 10 Companies ─────────────────────
plt.figure(figsize=(12, 6))
plt.barh(top_companies["name"][::-1], top_companies["patents"][::-1], color="darkorange")
plt.xlabel("Number of Patents")
plt.title("Top 10 Companies by Patent Count")
plt.tight_layout()
plt.savefig(f"{REPORTS}/top_companies.png")
plt.close()
print("Saved top_companies.png")

# ── Chart 3: Patents Per Year ──────────────────────
plt.figure(figsize=(14, 6))
plt.plot(patents_per_year["year"], patents_per_year["patents"], color="green", linewidth=2)
plt.fill_between(patents_per_year["year"], patents_per_year["patents"], alpha=0.2, color="green")
plt.xlabel("Year")
plt.ylabel("Number of Patents")
plt.title("US Patents Granted Per Year (1976-2025)")
plt.tight_layout()
plt.savefig(f"{REPORTS}/patents_per_year.png")
plt.close()
print("Saved patents_per_year.png")

print("\nAll charts saved to reports/")
