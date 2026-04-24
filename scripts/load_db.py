import sqlite3
import pandas as pd
import os

# ── Configuration ─────────────────────────────────────
DB_PATH = "data/patents.db"
CLEAN_DIR = "data/clean"
CHUNK_SIZE = 100000  # Adjust based on memory

def load_to_db():
    print(f"Connecting to database: {DB_PATH}...")
    conn = sqlite3.connect(DB_PATH)
    
    # ── 1. PATENTS ─────────────────────────────────────
    load_csv_to_table(
        conn, 
        f"{CLEAN_DIR}/clean_patents.csv", 
        "patents", 
        ["patent_id"], 
        "patent_id"
    )

    # ── 2. INVENTORS ───────────────────────────────────
    load_csv_to_table(
        conn, 
        f"{CLEAN_DIR}/clean_inventors.csv", 
        "inventors", 
        ["patent_id", "inventor_id"]
    )

    # ── 3. COMPANIES ───────────────────────────────────
    load_csv_to_table(
        conn, 
        f"{CLEAN_DIR}/clean_companies.csv", 
        "companies", 
        ["patent_id", "company_id"]
    )

    print("\nDatabase loading complete.")
    conn.close()

def load_csv_to_table(conn, csv_path, table_name, index_cols=None, primary_key=None):
    if not os.path.exists(csv_path):
        print(f"Warning: {csv_path} not found. Skipping...")
        return

    print(f"Loading {csv_path} into table '{table_name}'...")
    
    # Drop table if exists to ensure fresh load
    conn.execute(f"DROP TABLE IF EXISTS {table_name}")
    
    first_chunk = True
    for chunk in pd.read_csv(csv_path, chunksize=CHUNK_SIZE):
        chunk.to_sql(table_name, conn, if_exists="append", index=False)
        
        if first_chunk:
            print(f"  First chunk loaded. Schema initialized.")
            first_chunk = False

    # Create indices for better performance
    if index_cols:
        for col in index_cols:
            print(f"  Creating index on {table_name}.{col}...")
            conn.execute(f"CREATE INDEX idx_{table_name}_{col} ON {table_name} ({col})")
            
    conn.commit()

if __name__ == "__main__":
    load_to_db()
