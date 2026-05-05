"""
Patent Pipeline — FastAPI Backend
Run: uvicorn api:app --reload --port 8000
"""

import sqlite3
import json
import numpy as np
from pathlib import Path
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures

# ── Config ────────────────────────────────────────────────────────────────────
DB_PATH = Path(__file__).parent / "data" / "patents.db"

app = FastAPI(
    title="Patent Pipeline API",
    description="REST API over patents.db for the patent analytics dashboard",
    version="1.0.0",
)

# Allow the frontend (any localhost port) to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # tighten to ["http://localhost:5173"] in prod
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# ── DB helper ─────────────────────────────────────────────────────────────────
def get_conn():
    if not DB_PATH.exists():
        raise HTTPException(status_code=503, detail=f"Database not found at {DB_PATH}")
    # Increase timeout for large dataset operations
    conn = sqlite3.connect(DB_PATH, timeout=60, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    
    # ── Performance Optimizations ──
    # WAL mode is already enabled on the DB file
    conn.execute("PRAGMA cache_size = -200000")  # 200MB cache
    conn.execute("PRAGMA temp_store = MEMORY")
    return conn


def query(sql: str, params: tuple = ()) -> list[dict]:
    conn = get_conn()
    try:
        cur = conn.execute(sql, params)
        return [dict(row) for row in cur.fetchall()]
    finally:
        conn.close()


# ── Models ────────────────────────────────────────────────────────────────────
class SQLRequest(BaseModel):
    sql: str


# ── Routes ────────────────────────────────────────────────────────────────────

@app.get("/")
def root():
    return {"status": "ok", "db": str(DB_PATH)}


# ── Stats ─────────────────────────────────────────────────────────────────────
@app.get("/api/stats")
def stats():
    """High-level database statistics shown in the overview cards."""
    total     = query("SELECT COUNT(*) AS n FROM patents")[0]["n"]
    inventors = query("SELECT COUNT(DISTINCT inventor_id) AS n FROM inventors")[0]["n"]
    companies = query("SELECT COUNT(DISTINCT company_id) AS n FROM companies")[0]["n"]
    countries = query("SELECT COUNT(DISTINCT country) AS n FROM inventors WHERE country IS NOT NULL")[0]["n"]
    return {
        "total_patents": total,
        "unique_inventors": inventors,
        "companies": companies,
        "countries": countries,
    }


# ── Inventors ─────────────────────────────────────────────────────────────────
@app.get("/api/inventors/top")
def top_inventors(limit: int = Query(10, ge=1, le=100)):
    """Top N inventors by patent count. Uses summary table if available."""
    try:
        # Try summary table first for speed
        rows = query("SELECT name, patents FROM summary_top_inventors LIMIT ?", (limit,))
        if rows: return rows
    except:
        pass
        
    return query("""
        SELECT name, COUNT(patent_id) AS patents
        FROM inventors
        WHERE name != ''
        GROUP BY inventor_id
        ORDER BY patents DESC
        LIMIT ?
    """, (limit,))


@app.get("/api/inventors/cte")
def inventors_cte(min_patents: int = Query(50, ge=1), limit: int = Query(10, ge=1, le=100)):
    """Inventors with more than N patents using a CTE (Q6)."""
    rows = query("""
        WITH inventor_counts AS (
            SELECT inventor_id, name, COUNT(DISTINCT patent_id) AS patent_count
            FROM inventors
            GROUP BY inventor_id
        )
        SELECT name, patent_count
        FROM inventor_counts
        WHERE patent_count > ?
        ORDER BY patent_count DESC
        LIMIT ?
    """, (min_patents, limit))
    return rows


@app.get("/api/inventors/ranked")
def inventors_ranked(limit: int = Query(10, ge=1, le=100)):
    """Inventors ranked by patent count using a window function (Q7)."""
    rows = query("""
        SELECT name, patent_count,
               RANK() OVER (ORDER BY patent_count DESC) AS rank
        FROM (
            SELECT inventor_id, name, COUNT(DISTINCT patent_id) AS patent_count
            FROM inventors
            GROUP BY inventor_id
        )
        LIMIT ?
    """, (limit,))
    return rows


# ── Companies ─────────────────────────────────────────────────────────────────
@app.get("/api/companies/top")
def top_companies(limit: int = Query(10, ge=1, le=100)):
    """Top N companies by patent count. Uses summary table if available."""
    try:
        # Try summary table first for speed
        rows = query("SELECT name, patents FROM summary_top_companies LIMIT ?", (limit,))
        if rows: return rows
    except:
        pass

    return query("""
        SELECT name, COUNT(patent_id) AS patents
        FROM companies
        WHERE name IS NOT NULL
        GROUP BY company_id
        ORDER BY patents DESC
        LIMIT ?
    """, (limit,))


# ── Countries ─────────────────────────────────────────────────────────────────
@app.get("/api/countries/top")
def top_countries(limit: int = Query(10, ge=1, le=100)):
    """Top N countries by distinct patent count (Q3)."""
    rows = query("""
        SELECT country, COUNT(DISTINCT patent_id) AS patents
        FROM inventors
        WHERE country IS NOT NULL
        GROUP BY country
        ORDER BY patents DESC
        LIMIT ?
    """, (limit,))
    return rows


# ── Patents per year ──────────────────────────────────────────────────────────
@app.get("/api/patents/per-year")
def patents_per_year(
    start: Optional[int] = None,
    end: Optional[int] = None,
    limit: int = Query(50, ge=1, le=200),
):
    """Annual patent counts, optionally filtered by year range (Q4)."""
    filters = ["year IS NOT NULL"]
    params: list = []
    if start:
        filters.append("year >= ?")
        params.append(start)
    if end:
        filters.append("year <= ?")
        params.append(end)
    where = " AND ".join(filters)
    params.append(limit)
    rows = query(f"""
        SELECT year, COUNT(*) AS patents
        FROM patents
        WHERE {where}
        GROUP BY year
        ORDER BY year ASC
        LIMIT ?
    """, tuple(params))
    return rows


# ── Join query ────────────────────────────────────────────────────────────────
@app.get("/api/patents/with-inventors")
def patents_with_inventors(limit: int = Query(10, ge=1, le=200)):
    """Patents joined with inventors and companies (Q5)."""
    rows = query("""
        SELECT p.patent_id, p.title, i.name AS inventor, c.name AS company
        FROM patents p
        JOIN inventors i ON p.patent_id = i.patent_id
        LEFT JOIN companies c ON p.patent_id = c.patent_id
        LIMIT ?
    """, (limit,))
    return rows


# ── Full report export ────────────────────────────────────────────────────────
@app.get("/api/report")
def full_report():
    """Combined JSON report matching the original script's report.json output."""
    return {
        "total_patents": query("SELECT COUNT(*) AS n FROM patents")[0]["n"],
        "top_inventors": query("""
            SELECT name, COUNT(DISTINCT patent_id) AS patent_count
            FROM inventors WHERE name != ''
            GROUP BY inventor_id ORDER BY patent_count DESC LIMIT 5
        """),
        "top_companies": query("""
            SELECT name, COUNT(DISTINCT patent_id) AS patent_count
            FROM companies WHERE name IS NOT NULL
            GROUP BY company_id ORDER BY patent_count DESC LIMIT 5
        """),
        "patents_per_year": query("""
            SELECT year, COUNT(*) AS patent_count
            FROM patents WHERE year IS NOT NULL
            GROUP BY year ORDER BY year DESC LIMIT 5
        """),
    }


# ── Safe ad-hoc SQL runner ────────────────────────────────────────────────────
BLOCKED = {"drop", "delete", "insert", "update", "alter", "create", "attach"}

@app.post("/api/query")
def run_query(body: SQLRequest):
    """
    Execute a read-only SELECT query from the SQL Runner panel.
    Blocks any destructive statement keywords.
    """
    sql_lower = body.sql.lower()
    for keyword in BLOCKED:
        if keyword in sql_lower:
            raise HTTPException(
                status_code=400,
                detail=f"Keyword '{keyword}' is not allowed in ad-hoc queries.",
            )
    if not sql_lower.strip().startswith("select") and "with" not in sql_lower[:10]:
        raise HTTPException(status_code=400, detail="Only SELECT / CTE queries are allowed.")

    try:
        rows = query(body.sql)
        return {"rows": rows, "count": len(rows)}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ── ML Forecast ───────────────────────────────────────────────────────────────
@app.get("/api/ml/forecast")
def get_forecast(years: int = Query(5, ge=1, le=10)):
    """
    Predict future patent trends using Polynomial Regression.
    Returns historical data combined with predicted values.
    """
    # 1. Get historical data (filtered for performance)
    historical_sql = """
        SELECT year, COUNT(*) AS patents
        FROM patents 
        WHERE year IS NOT NULL AND year >= 1976 AND year <= 2024
        GROUP BY year 
        ORDER BY year ASC
    """
    data = query(historical_sql)
    if not data:
        return {"historical": [], "forecast": []}
    
    df = pd.DataFrame(data)
    
    # 2. Train Model
    X = df[['year']].values
    y = df['patents'].values
    
    poly = PolynomialFeatures(degree=3)
    X_poly = poly.fit_transform(X)
    
    model = LinearRegression()
    model.fit(X_poly, y)
    
    # 3. Predict Future
    last_year = int(df['year'].max())
    future_years = np.array([[last_year + i] for i in range(1, years + 1)])
    future_years_poly = poly.transform(future_years)
    predictions = model.predict(future_years_poly)
    
    forecast = []
    for i, year in enumerate(future_years.flatten()):
        forecast.append({
            "year": int(year),
            "patents": int(max(0, predictions[i])),
            "is_prediction": True
        })
    
    # Format for chart consumption
    return {
        "historical": data,
        "forecast": forecast
    }

import pandas as pd
