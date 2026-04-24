# Global Patent Intelligence Data Pipeline

A full data pipeline that collects, cleans, stores, and analyzes
real US patent data from USPTO PatentsView (1976-2025).

## Results
- Total Patents: 9,454,161
- Top Inventor: Shunpei Yamazaki (6,787 patents)
- Top Company: Samsung Display Co., Ltd. (174,536 patents)
- Data Range: 1976 - 2025

## How to Run

1. Install dependencies
   pip install -r requirements.txt

2. Place raw TSV files in data/raw/ from patentsview.org

3. Clean the data
   python scripts/clean.py

4. Load into database
   python scripts/load_db.py

5. Run queries
   python scripts/queries.py

6. Generate reports
   python scripts/report.py

## Tools Used
- Python, pandas, SQLite, matplotlib

## Data Source
USPTO PatentsView - https://patentsview.org
