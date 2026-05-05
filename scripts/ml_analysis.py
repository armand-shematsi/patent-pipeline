import sqlite3
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from pathlib import Path

# Paths
DB_PATH = Path(__file__).parent.parent / "data" / "patents.db"

def get_patent_trends():
    conn = sqlite3.connect(DB_PATH)
    query = """
        SELECT year, COUNT(*) AS patents
        FROM patents 
        WHERE year IS NOT NULL AND year >= 1976 AND year <= 2024
        GROUP BY year 
        ORDER BY year ASC
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df

def predict_future_trends(df, forecast_years=5):
    # Prepare data
    X = df[['year']].values
    y = df['patents'].values
    
    # Use Polynomial Regression for better fit
    poly = PolynomialFeatures(degree=3)
    X_poly = poly.fit_transform(X)
    
    model = LinearRegression()
    model.fit(X_poly, y)
    
    # Predict future
    last_year = df['year'].max()
    future_years = np.array([[last_year + i] for i in range(1, forecast_years + 1)])
    future_years_poly = poly.transform(future_years)
    predictions = model.predict(future_years_poly)
    
    forecast_df = pd.DataFrame({
        'year': future_years.flatten(),
        'patents': predictions.astype(int),
        'is_prediction': True
    })
    
    return forecast_df

if __name__ == "__main__":
    df = get_patent_trends()
    if not df.empty:
        forecast = predict_future_trends(df)
        print("Historical Data Head:")
        print(df.tail())
        print("\nForecasted Data:")
        print(forecast)
    else:
        print("No data found in database.")
