import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import make_pipeline
import numpy as np
from datetime import datetime

# Load data
df = pd.read_csv("gas_prices.csv")
df.columns = df.columns.str.strip()  # Remove extra spaces in headers

# Convert 'Date' column to datetime
df['Date'] = pd.to_datetime(df['Date'])

# Sort the data by date
df = df.sort_values('Date')

# Calculate days since the start date
start_date = df['Date'].min()
df['Days_Since_Start'] = (df['Date'] - start_date).dt.days

# Prepare training data
X = df[['Days_Since_Start']]
y = df['Prices']

# Train polynomial regression model (degree 2)
poly_model = make_pipeline(PolynomialFeatures(degree=2), LinearRegression())
poly_model.fit(X, y)

# Predict for next 12 months (Oct 2024 to Sep 2025)
future_dates = pd.date_range(start=df['Date'].max() + pd.DateOffset(months=1), periods=12, freq='M')
future_days = (future_dates - start_date).days.values.reshape(-1, 1)
future_preds = poly_model.predict(future_days)

# Clip predictions to avoid unrealistic values
future_preds = np.clip(future_preds, 10, 13)

# Plot historical + future prices
plt.figure(figsize=(10, 6))
plt.plot(df['Date'], df['Prices'], label="Historical Prices", marker='o', color='blue')
plt.plot(future_dates, future_preds, label="Predicted Prices", marker='x', color='green', linestyle='--')
plt.title("Natural Gas Price Forecast (JPMorgan Task)")
plt.xlabel("Date")
plt.ylabel("Price (₹)")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()

# Plot monthly seasonality trend
df['Month'] = df['Date'].dt.month
plt.figure(figsize=(8, 5))
df.boxplot(column='Prices', by='Month')
plt.title("Monthly Seasonality in Gas Prices")
plt.suptitle("")
plt.xlabel("Month")
plt.ylabel("Price (₹)")
plt.grid(True)
plt.tight_layout()
plt.show()

# Function to predict price for any date
def predict_price(date_string):
    try:
        input_date = pd.to_datetime(date_string)
        days_since = (input_date - start_date).days
        if days_since < 0:
            return "Date is before data starts. Cannot predict."
        price = poly_model.predict([[days_since]])[0]
        return round(np.clip(price, 10, 13), 2)
    except Exception as e:
        return f"Invalid date or error: {e}"

# Example usage
print("Predicted price on 2025-03-31:", predict_price("2025-03-31"))
