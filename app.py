import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from pathlib import Path

# --- CONFIG ---
st.set_page_config(
    page_title="USPTO Patent Intelligence",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- THEME & CSS ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono&display=swap');
    
    .main { background-color: #0a0c10; }
    .stMetric { background-color: #111318; border: 1px solid rgba(255,255,255,0.07); padding: 15px; border-radius: 10px; }
    .stMetric:hover { border-color: #3b82f6; cursor: pointer; }
    .mono { font-family: 'IBM Plex Mono', monospace; }
    
    /* Hide Streamlit elements for a cleaner look */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Custom Sidebar styling */
    section[data-testid="stSidebar"] {
        background-color: #111318;
        border-right: 1px solid rgba(255,255,255,0.07);
    }
    </style>
""", unsafe_allow_html=True)

# --- DATA HELPERS ---
DB_PATH = Path("data/patents.db")

def query_db(sql, params=()):
    try:
        with sqlite3.connect(DB_PATH) as conn:
            return pd.read_sql_query(sql, conn, params=params)
    except Exception as e:
        st.error(f"Database error: {e}")
        return pd.DataFrame()

@st.cache_data
def get_stats():
    stats = {}
    stats['total_patents'] = query_db("SELECT COUNT(*) FROM patents").iloc[0,0]
    stats['unique_inventors'] = query_db("SELECT COUNT(DISTINCT inventor_id) FROM inventors").iloc[0,0]
    stats['companies'] = query_db("SELECT COUNT(DISTINCT company_id) FROM companies").iloc[0,0]
    stats['countries'] = query_db("SELECT COUNT(DISTINCT country) FROM inventors WHERE country != ''").iloc[0,0]
    return stats

# --- SIDEBAR NAVIGATION ---
st.sidebar.title("🤖 Patent Intel")
st.sidebar.markdown("---")
view = st.sidebar.radio("Navigate Views", 
    ["Overview", "Geography", "Inventors", "Companies", "Trend Forecast", "SQL Runner"]
)

# --- GLOBAL SEARCH ---
st.sidebar.markdown("---")
search_query = st.sidebar.text_input("🔍 Global Search", placeholder="e.g. 'Apple' or 'Quantum'")

if search_query:
    st.markdown(f"### 🔍 Search Results for '{search_query}'")
    cols = st.columns(3)
    
    # Search Patents
    df_p = query_db(f"SELECT patent_id, title FROM patents WHERE title LIKE ? LIMIT 5", (f"%{search_query}%",))
    with cols[0]:
        st.markdown("**Patents**")
        if not df_p.empty: st.dataframe(df_p, hide_index=True)
        else: st.caption("No patents found")
        
    # Search Companies
    df_c = query_db(f"SELECT DISTINCT name FROM companies WHERE name LIKE ? LIMIT 5", (f"%{search_query}%",))
    with cols[1]:
        st.markdown("**Companies**")
        if not df_c.empty: st.dataframe(df_c, hide_index=True)
        else: st.caption("No companies found")
        
    # Search Inventors
    df_i = query_db(f"SELECT DISTINCT name FROM inventors WHERE name LIKE ? LIMIT 5", (f"%{search_query}%",))
    with cols[2]:
        st.markdown("**Inventors**")
        if not df_i.empty: st.dataframe(df_i, hide_index=True)
        else: st.caption("No inventors found")
    st.markdown("---")

# --- VIEW: OVERVIEW ---
if view == "Overview":
    st.title("📊 Patent Pipeline Overview")
    stats = get_stats()
    
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Total Patents", f"{stats['total_patents']:,}")
        with st.expander("See Samples"):
            df_s = query_db("SELECT patent_id, title, filing_date FROM patents LIMIT 10")
            st.dataframe(df_s, hide_index=True)
            st.download_button("Download Samples", df_s.to_csv(index=False), "patents_sample.csv", "text/csv")
            
    with c2:
        st.metric("Unique Inventors", f"{stats['unique_inventors']:,}")
        with st.expander("See Samples"):
            df_s = query_db("SELECT DISTINCT name FROM inventors LIMIT 10")
            st.dataframe(df_s, hide_index=True)
            st.download_button("Download Samples", df_s.to_csv(index=False), "inventors_sample.csv", "text/csv")
            
    with c3:
        st.metric("Companies", f"{stats['companies']:,}")
        with st.expander("See Samples"):
            df_s = query_db("SELECT DISTINCT name FROM companies LIMIT 10")
            st.dataframe(df_s, hide_index=True)
            st.download_button("Download Samples", df_s.to_csv(index=False), "companies_sample.csv", "text/csv")
            
    with c4:
        st.metric("Countries", stats['countries'])
        with st.expander("See List"):
            df_s = query_db("SELECT DISTINCT country FROM inventors WHERE country != '' LIMIT 10")
            st.dataframe(df_s, hide_index=True)
            st.download_button("Download List", df_s.to_csv(index=False), "countries.csv", "text/csv")

    st.markdown("---")
    
    # Quick Trends with Filter
    st.subheader("Patent Filing Activity")
    y_start, y_end = st.select_slider("Select Year Range", options=sorted(query_db("SELECT DISTINCT year FROM patents")['year'].tolist()), value=(1976, 2025))
    df_year = query_db(f"SELECT year, COUNT(*) as count FROM patents WHERE year BETWEEN {y_start} AND {y_end} GROUP BY year ORDER BY year")
    
    fig = px.area(df_year, x='year', y='count', 
                  title=f"Annual Patent Grants ({y_start}-{y_end})",
                  template="plotly_dark",
                  color_discrete_sequence=['#3b82f6'])
    fig.update_traces(fillcolor='rgba(59,130,246,0.2)')
    st.plotly_chart(fig, use_container_width=True)

# --- VIEW: GEOGRAPHY ---
elif view == "Geography":
    st.title("🌍 Geographic Distribution")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Top Countries by Patent Count")
        limit = st.slider("Number of countries", 5, 50, 10)
        df_country = query_db(f"""
            SELECT country, COUNT(DISTINCT patent_id) as patents 
            FROM inventors 
            WHERE country != '' AND country IS NOT NULL
            GROUP BY country 
            ORDER BY patents DESC LIMIT {limit}
        """)
        fig = px.bar(df_country, x='patents', y='country', orientation='h',
                     template="plotly_dark", color='patents',
                     color_continuous_scale='Greens')
        fig.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Regional Hubs (City/State)")
        df_loc = query_db("""
            SELECT city, state, country, COUNT(DISTINCT patent_id) as patents
            FROM inventors
            WHERE city != '' AND country = 'US'
            GROUP BY city, state
            ORDER BY patents DESC LIMIT 10
        """)
        st.dataframe(df_loc, use_container_width=True, hide_index=True)

    st.markdown("---")
    st.subheader("Global Patent Map")
    # Sample some locations for the map to avoid performance issues
    df_map = query_db("""
        SELECT l.city, l.country, l.latitude, l.longitude, COUNT(DISTINCT i.patent_id) as patents
        FROM locations l
        JOIN inventors i ON l.city = i.city AND l.country = i.country
        WHERE l.latitude IS NOT NULL AND l.longitude IS NOT NULL
        GROUP BY l.location_id
        ORDER BY patents DESC LIMIT 1000
    """)
    if not df_map.empty:
        fig_map = px.scatter_geo(df_map, lat='latitude', lon='longitude', 
                                 hover_name='city', size='patents',
                                 projection="natural earth",
                                 template="plotly_dark",
                                 title="Top 1,000 Innovation Hubs")
        st.plotly_chart(fig_map, use_container_width=True)
    else:
        st.info("No coordinate data found for mapping.")

# --- VIEW: INVENTORS ---
elif view == "Inventors":
    st.title("👤 Top Inventors")
    limit = st.slider("Number of inventors to show", 5, 50, 10)
    df_inv = query_db(f"SELECT name, COUNT(DISTINCT patent_id) as patents FROM inventors GROUP BY inventor_id ORDER BY patents DESC LIMIT {limit}")
    
    fig = px.bar(df_inv, x='patents', y='name', orientation='h',
                 title=f"Top {limit} Prolific Inventors",
                 template="plotly_dark",
                 color='patents',
                 color_continuous_scale='Blues')
    fig.update_layout(yaxis={'categoryorder':'total ascending'})
    st.plotly_chart(fig, use_container_width=True)
    
    st.subheader("Detailed Dataset")
    st.dataframe(df_inv, use_container_width=True, hide_index=True)
    st.download_button("Download Inventor Data", df_inv.to_csv(index=False), "top_inventors.csv", "text/csv")

# --- VIEW: COMPANIES ---
elif view == "Companies":
    st.title("🏢 Top Companies (Assignees)")
    limit = st.slider("Number of companies to show", 5, 50, 10)
    df_co = query_db(f"SELECT name, COUNT(DISTINCT patent_id) as patents FROM companies GROUP BY company_id ORDER BY patents DESC LIMIT {limit}")
    
    fig = px.bar(df_co, x='patents', y='name', orientation='h',
                 title=f"Top {limit} Companies",
                 template="plotly_dark",
                 color='patents',
                 color_continuous_scale='Viridis')
    fig.update_layout(yaxis={'categoryorder':'total ascending'})
    st.plotly_chart(fig, use_container_width=True)
    
    st.subheader("Detailed Dataset")
    st.dataframe(df_co, use_container_width=True, hide_index=True)
    st.download_button("Download Company Data", df_co.to_csv(index=False), "top_companies.csv", "text/csv")

# --- VIEW: TREND FORECAST ---
elif view == "Trend Forecast":
    st.title("🤖 Machine Learning: Trend Forecast")
    forecast_years = st.slider("Years to forecast", 1, 10, 5)
    
    # Prep data
    df_year = query_db("SELECT year, COUNT(*) as count FROM patents WHERE year IS NOT NULL GROUP BY year ORDER BY year")
    X = df_year[['year']].values
    y = df_year['count'].values
    
    # Train model
    poly = PolynomialFeatures(degree=3)
    X_poly = poly.fit_transform(X)
    model = LinearRegression().fit(X_poly, y)
    
    # Forecast
    last_year = int(X.max())
    future_years = np.array([[last_year + i] for i in range(1, forecast_years + 1)])
    future_years_poly = poly.transform(future_years)
    preds = model.predict(future_years_poly)
    
    # Plot
    fig = go.Figure()
    # Historical
    fig.add_trace(go.Scatter(x=df_year['year'], y=df_year['count'], 
                             name='Historical', line=dict(color='#3b82f6', width=2)))
    # Forecast
    fig.add_trace(go.Scatter(x=future_years.flatten(), y=preds, 
                             name='Polynomial Forecast', line=dict(color='#f59e0b', width=2, dash='dot')))
    
    fig.update_layout(title="US Patent Trends: History vs. Forecast",
                      template="plotly_dark",
                      xaxis_title="Year",
                      yaxis_title="Patents",
                      hovermode="x unified")
    
    st.plotly_chart(fig, use_container_width=True)
    
    st.info(f"Model: Degree-3 Polynomial Regression. Accuracy is based on historical growth patterns.")

# --- VIEW: SQL RUNNER ---
elif view == "SQL Runner":
    st.title("🔍 SQL Playground (Read-Only)")
    st.markdown("Execute custom SQL queries against the USPTO dataset.")
    
    query = st.text_area("SQL Query", value="SELECT * FROM patents LIMIT 10;", height=150)
    
    if st.button("Run Query"):
        if query.lower().strip().startswith("select"):
            res = query_db(query)
            if not res.empty:
                st.success(f"Returned {len(res)} rows")
                st.dataframe(res, use_container_width=True)
            else:
                st.warning("No data found for this query.")
        else:
            st.error("Only SELECT queries are allowed for security.")

# --- FOOTER ---
st.sidebar.markdown("---")
st.sidebar.caption("Data source: USPTO (1976-2025)")
st.sidebar.caption("Built with ❤️ using Streamlit & Plotly")
