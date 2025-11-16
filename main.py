# ============================================================
#  Import–Export Data Analytics and Demand Forecasting
# Case Study: LED Lights Imported from China to India
# ============================================================

# Step 1 — Import Required Libraries
# ------------------------------------------------------------
# If you don't have these installed, uncomment the following line:
# !pip install pandas numpy matplotlib seaborn scikit-learn statsmodels

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from statsmodels.tsa.arima.model import ARIMA
from sklearn.metrics import mean_absolute_error, mean_squared_error
import warnings
warnings.filterwarnings("ignore")

# Step 2 — Load or Simulate Import–Export Data
# ------------------------------------------------------------
# You can replace this with real CSV data from data.gov.in or UN Comtrade
data = {
    "Year": np.arange(2013, 2025),
    "Import_Value_USD_Million": [120, 135, 160, 185, 210, 250, 290, 310, 355, 370, 400, 425]
}

df = pd.DataFrame(data)
df["Year"] = pd.to_datetime(df["Year"], format="%Y")
df.set_index("Year", inplace=True)

print("📊 Sample Import Data (2013–2024):")
print(df.head())

# Step 3 — Visualize Import Trends
# ------------------------------------------------------------
plt.figure(figsize=(10, 5))
sns.lineplot(data=df, x=df.index.year, y="Import_Value_USD_Million", marker="o")
plt.title("Yearly Import Value of LED Lights (India from China)")
plt.xlabel("Year")
plt.ylabel("Import Value (in Million USD)")
plt.grid(True)
plt.show()

# Step 4 — Build and Train Forecasting Model (ARIMA)
# ------------------------------------------------------------
# Split data into training (till 2022) and testing (2023–2024)
train = df[:-2]
test = df[-2:]

# Build ARIMA model
model = ARIMA(train["Import_Value_USD_Million"], order=(1,1,1))
model_fit = model.fit()

# Forecast for next 2 years (2023–2024)
forecast = model_fit.forecast(steps=2)
forecast.index = test.index

# Compare actual vs predicted
plt.figure(figsize=(10,5))
plt.plot(train.index, train["Import_Value_USD_Million"], label="Training Data")
plt.plot(test.index, test["Import_Value_USD_Million"], label="Actual Data")
plt.plot(forecast.index, forecast, label="Forecast", linestyle="--")
plt.title("Import Forecast of LED Lights (ARIMA Model)")
plt.xlabel("Year")
plt.ylabel("Import Value (in Million USD)")
plt.legend()
plt.grid(True)
plt.show()

# Evaluate model performance
mae = mean_absolute_error(test, forecast)
rmse = np.sqrt(mean_squared_error(test, forecast))
print(f"\n📈 Model Evaluation:")
print(f"Mean Absolute Error (MAE): {mae:.2f}")
print(f"Root Mean Square Error (RMSE): {rmse:.2f}")

# Step 5 — Predict Imports for Next 3 Years (2025–2027)
# ------------------------------------------------------------
future_forecast = model_fit.forecast(steps=3)
future_years = pd.date_range("2025", periods=3, freq="Y")
future_df = pd.DataFrame({"Forecasted_Import_Value": future_forecast.values}, index=future_years)

plt.figure(figsize=(10,5))
plt.plot(df.index, df["Import_Value_USD_Million"], label="Historical Data", marker="o")
plt.plot(future_df.index, future_df["Forecasted_Import_Value"], label="Future Forecast", marker="x", linestyle="--")
plt.title("Forecasted Import Value of LED Lights (2025–2027)")
plt.xlabel("Year")
plt.ylabel("Import Value (in Million USD)")
plt.legend()
plt.grid(True)
plt.show()

print("\n🔮 Forecasted Import Values (2025–2027):")
print(future_df)

# Step 6 — Insights Summary
# ------------------------------------------------------------
latest = df["Import_Value_USD_Million"].iloc[-1]
growth_rate = (forecast.iloc[-1] - df["Import_Value_USD_Million"].iloc[-3]) / df["Import_Value_USD_Million"].iloc[-3] * 100

print("\n🔍 Insights Summary:")
print(f"- The latest import value (2024) was approximately {latest} million USD.")
print(f"- The forecast suggests an average annual growth rate of {growth_rate:.2f}% in imports.")
print("- The model indicates increasing demand for LED light imports, driven by India's expanding infrastructure and smart-city projects.")
print("- Importers can use this insight to plan bulk orders, negotiate supplier contracts, and optimize inventory levels.")
print("- This demonstrates how AI-driven analytics can support small and medium import–export enterprises in decision-making.")

# ============================================================
# ✅ End of Project Code
# ============================================================
