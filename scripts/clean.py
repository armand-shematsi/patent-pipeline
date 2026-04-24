import pandas as pd
import os

# ── Paths ──────────────────────────────────────────
RAW = "data/raw"
CLEAN = "data/clean"
os.makedirs(CLEAN, exist_ok=True)

# ── 1. PATENTS ──────────────────────────────────────
print("Cleaning patents...")
patents = pd.read_csv(f"{RAW}/g_patent.tsv", sep="\t", low_memory=False)

patents = patents[["patent_id", "patent_title", "patent_date"]].copy()
patents.columns = ["patent_id", "title", "filing_date"]

# Drop rows missing key fields
patents.dropna(subset=["patent_id", "title", "filing_date"], inplace=True)

# Extract year from date
patents["filing_date"] = pd.to_datetime(patents["filing_date"], errors="coerce")
patents["year"] = patents["filing_date"].dt.year
patents["abstract"] = None  # not available in this file

patents.drop_duplicates(subset="patent_id", inplace=True)
patents.to_csv(f"{CLEAN}/clean_patents.csv", index=False)
print(f"  Patents saved: {len(patents)} rows")

# ── 2. INVENTORS ────────────────────────────────────
print("Cleaning inventors...")
inventors = pd.read_csv(f"{RAW}/g_inventor_disambiguated.tsv", sep="\t", low_memory=False)

inventors = inventors[["inventor_id", "disambig_inventor_name_first", 
                        "disambig_inventor_name_last", "patent_id"]].copy()

# Combine first and last name
inventors["name"] = (
    inventors["disambig_inventor_name_first"].fillna("") + " " +
    inventors["disambig_inventor_name_last"].fillna("")
).str.strip()

inventors["country"] = None  # location_id needs separate lookup

inventors = inventors[["inventor_id", "name", "country", "patent_id"]]
inventors.dropna(subset=["inventor_id", "name"], inplace=True)
inventors.drop_duplicates(inplace=True)
inventors.to_csv(f"{CLEAN}/clean_inventors.csv", index=False)
print(f"  Inventors saved: {len(inventors)} rows")

# ── 3. COMPANIES ────────────────────────────────────
print("Cleaning companies...")
assignees = pd.read_csv(f"{RAW}/g_assignee_disambiguated.tsv", sep="\t", low_memory=False)

assignees = assignees[["assignee_id", "disambig_assignee_organization", "patent_id"]].copy()
assignees.columns = ["company_id", "name", "patent_id"]

assignees.dropna(subset=["company_id", "name"], inplace=True)
assignees.drop_duplicates(inplace=True)
assignees.to_csv(f"{CLEAN}/clean_companies.csv", index=False)
print(f"  Companies saved: {len(assignees)} rows")

print("\nAll files cleaned and saved to data/clean/")
