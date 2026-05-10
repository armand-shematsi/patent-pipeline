# 🤖 Global Patent Intelligence Data Pipeline

A professional-grade data pipeline that cleans, enriches, and analyzes real US patent data from the **USPTO PatentsView (1976-2025)**. This project transforms over **10 million records** into actionable insights via an interactive dashboard and automated reports.

---

## 📊 Live Insights
*   **Total Patents Processed:** 9,454,161
*   **Unique Inventors:** 4,294,034
*   **Top Innovation Hubs:** US, Japan, Germany, South Korea, China.
*   **Top Company:** Samsung Display Co., Ltd. (174,536 patents)

---

## 🏗️ Architecture & Features

### 1. Data Pipeline (`/scripts`)
- **Cleaning & Enrichment**: Processes 5GB+ of raw TSV data using `pandas`.
- **Geographic Integration**: Joins patent records with `g_location_disambiguated.tsv` to provide city, state, and country-level granularity.
- **Incremental Loading**: Chunked loading into SQLite for memory efficiency.

### 2. Analytics & ML
- **Trend Forecasting**: Uses **Degree-3 Polynomial Regression** (`scikit-learn`) to predict patent filing trajectories for the next 10 years.
- **Geographic Mapping**: Visualizes innovation clusters on a global scale using `plotly` and `scatter_geo`.

### 3. Interactive Dashboard (`app.py`)
- **Overview**: High-level KPIs and trends.
- **Geography**: Interactive global maps and regional hub analysis.
- **Inventors & Companies**: Prolific contributor leaderboards.
- **SQL Runner**: A safe, read-only SQL playground to explore the database.

---

## 🛠️ Tech Stack
| Category | Tools |
| :--- | :--- |
| **Language** | ![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white) |
| **Data Processing** | ![Pandas](https://img.shields.io/badge/Pandas-150458?style=flat&logo=pandas&logoColor=white) ![NumPy](https://img.shields.io/badge/NumPy-013243?style=flat&logo=numpy&logoColor=white) |
| **Database** | ![SQLite](https://img.shields.io/badge/SQLite-003B57?style=flat&logo=sqlite&logoColor=white) |
| **Visualization** | ![Plotly](https://img.shields.io/badge/Plotly-3F4F75?style=flat&logo=plotly&logoColor=white) ![Matplotlib](https://img.shields.io/badge/Matplotlib-11557C?style=flat) |
| **Web Framework** | ![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=flat&logo=streamlit&logoColor=white) ![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat&logo=fastapi&logoColor=white) |
| **Machine Learning** | ![Scikit-Learn](https://img.shields.io/badge/Scikit--Learn-F7931E?style=flat&logo=scikit-learn&logoColor=white) |

---

## 📂 Project Structure
```bash
├── data/
│   ├── raw/         # Source TSV files from PatentsView
│   ├── clean/       # Processed CSV files
│   └── patents.db   # Final SQLite database
├── scripts/
│   ├── clean.py     # Data cleaning and enrichment logic
│   ├── load_db.py   # Database schema and loading
│   ├── visualize.py # Static chart generation
│   └── report.py    # Console/JSON report generator
├── sql/
│   ├── schema.sql   # Database structure
│   └── queries.sql  # Reference analysis queries
├── app.py           # Streamlit Dashboard
└── api.py           # FastAPI Backend (REST layer)
```

---

## 🚀 How to Run

### 1. Environment Setup
```bash
# Install dependencies
python3 -m pip install -r requirements.txt
```

### 2. Initialize Data
1.  Place raw TSV files (e.g., `g_patent.tsv`, `g_location_disambiguated.tsv`) in `data/raw/`.
2.  **Clean & Enrich**: `python3 scripts/clean.py`
3.  **Load DB**: `python3 scripts/load_db.py`

### 3. Launch Dashboard
- **Static Dashboard**: Open `main.html` in your browser (requires `api.py` to be running).
- **Streamlit App**: `python3 -m streamlit run app.py`

---

## 🌐 Data Source
Data provided by **USPTO PatentsView**, a data visualization and analysis platform that provides public access to intellectual property data. 
[https://patentsview.org](https://patentsview.org)
