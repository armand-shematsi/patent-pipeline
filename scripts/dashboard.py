import streamlit as st
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

DB_PATH = "data/patents.db"

st.set_page_config(page_title="Patent Intelligence Dashboard", layout="wide")
st.title("Global Patent Intelligence Dashboard")
st.markdown("Analysis of 9,454,161 US Patents from 1976 to 2025")

conn = sqlite3.connect(DB_PATH)

# ── Metrics Row ────────────────────────────────────
col1, col2, col3 = st.columns(3)
col1.metric("Total Patents", "9,454,161")
col2.metric("Top Inventor", "Shunpei Yamazaki")
col3.metric("Top Company", "Samsung Display")

st.divider()

# ── Top Inventors ──────────────────────────────────
st.subheader("Top 10 Inventors")
top_inventors = pd.read_sql("""
    SELECT name, COUNT(DISTINCT patent_id) AS patents
    FROM inventors WHERE name != ''
    GROUP BY inventor_id
    ORDER BY patents DESC LIMIT 10
""", conn)

fig1, ax1 = plt.subplots(figsize=(10, 5))
ax1.barh(top_inventors["name"][::-1], top_inventors["patents"][::-1], color="steelblue")
ax1.set_xlabel("Number of Patents")
ax1.set_title("Top 10 Inventors")
plt.tight_layout()
st.pyplot(fig1)

st.divider()

# ── Top Companies ──────────────────────────────────
st.subheader("Top 10 Companies")
top_companies = pd.read_sql("""
    SELECT name, COUNT(DISTINCT patent_id) AS patents
    FROM companies WHERE name IS NOT NULL
    GROUP BY company_id
    ORDER BY patents DESC LIMIT 10
""", conn)

fig2, ax2 = plt.subplots(figsize=(10, 5))
ax2.barh(top_companies["name"][::-1], top_companies["patents"][::-1], color="darkorange")
ax2.set_xlabel("Number of Patents")
ax2.set_title("Top 10 Companies")
plt.tight_layout()
st.pyplot(fig2)

st.divider()

# ── Patents Per Year ───────────────────────────────
st.subheader("Patents Granted Per Year (1976-2025)")
patents_per_year = pd.read_sql("""
    SELECT year, COUNT(*) AS patents
    FROM patents WHERE year IS NOT NULL
    GROUP BY year ORDER BY year ASC
""", conn)

fig3, ax3 = plt.subplots(figsize=(12, 5))
ax3.plot(patents_per_year["year"], patents_per_year["patents"], color="green", linewidth=2)
ax3.fill_between(patents_per_year["year"], patents_per_year["patents"], alpha=0.2, color="green")
ax3.set_xlabel("Year")
ax3.set_ylabel("Patents")
ax3.set_title("US Patents Per Year")
plt.tight_layout()
st.pyplot(fig3)

st.divider()

# ── Raw Data Tables ────────────────────────────────
st.subheader("Top Inventors Data")
st.dataframe(top_inventors, use_container_width=True)

st.subheader("Top Companies Data")
st.dataframe(top_companies, use_container_width=True)

conn.close()
