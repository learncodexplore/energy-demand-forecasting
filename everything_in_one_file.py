"""
everything_in_one_file.py

==============================================================================
  !!  THIS IS A "BAD EXAMPLE" FILE  -  DO NOT STRUCTURE YOUR PROJECT LIKE THIS  !!
==============================================================================

This single file does EVERYTHING:
  - loads and cleans the data
  - creates time features
  - builds the baseline forecasts
  - evaluates them (MAE, RMSE, MAPE)
  - draws and saves every figure
  - prints the summary

It produces the SAME result as the properly structured project.
The point of the video is: it works, but it is painful to read, painful to
navigate, and painful for two people to edit at the same time.

Compare this with the structured version, where the same code is split into:
    src/data_preparation.py
    src/forecasting.py
    src/evaluation.py
    src/visualization.py
    main.py
"""

from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


# ----------------------------------------------------------------------------
# CONFIG (mixed in with everything else - hard to find later)
# ----------------------------------------------------------------------------
YEAR = 2019
DATA_URL = (
    "https://data.open-power-system-data.org/time_series/"
    "2020-10-06/time_series_60min_singleindex.csv"
)
ORIGINAL_COLUMNS = [
    "utc_timestamp",
    "DE_load_actual_entsoe_transparency",
    "DE_load_forecast_entsoe_transparency",
]
RENAME_MAP = {
    "utc_timestamp": "timestamp",
    "DE_load_actual_entsoe_transparency": "actual_load_MW",
    "DE_load_forecast_entsoe_transparency": "official_forecast_MW",
}
FIGURES_DIR = Path("reports") / "figures"
PROCESSED_DIR = Path("data") / "processed"
PROCESSED_FILE = PROCESSED_DIR / f"germany_load_{YEAR}_clean.csv"


# ----------------------------------------------------------------------------
# DATA PREPARATION  (this whole block should really be its own module)
# ----------------------------------------------------------------------------
print("Loading dataset from the online URL ...")
df = pd.read_csv(DATA_URL, usecols=ORIGINAL_COLUMNS)
print(f"Dataset loaded. Shape: {df.shape}")

# rename columns
df = df.rename(columns=RENAME_MAP)

# convert timestamp
df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)

# filter to one year
df = df.loc[df["timestamp"].dt.year == YEAR].copy()
print(f"Filtered to year {YEAR}. Rows kept: {len(df)}")

# handle missing values
n_missing_before = df[["actual_load_MW", "official_forecast_MW"]].isna().sum().sum()
df["actual_load_MW"] = df["actual_load_MW"].ffill().bfill()
df["official_forecast_MW"] = df["official_forecast_MW"].ffill().bfill()
n_missing_after = df[["actual_load_MW", "official_forecast_MW"]].isna().sum().sum()
print(f"Missing values filled: {n_missing_before} -> {n_missing_after} remaining")

# create time features
df["hour"] = df["timestamp"].dt.hour
df["day_of_week"] = df["timestamp"].dt.dayofweek
df["day_name"] = df["timestamp"].dt.day_name()
df["month"] = df["timestamp"].dt.month
df["date"] = df["timestamp"].dt.date
df = df.reset_index(drop=True)
print(f"Prepared dataset shape: {df.shape}")
print(f"Date range: {df['timestamp'].min()} -> {df['timestamp'].max()}")


# ----------------------------------------------------------------------------
# FORECASTING  (this whole block should really be its own module)
# ----------------------------------------------------------------------------
# baseline 1: yesterday same hour
df["forecast_yesterday_MW"] = df["actual_load_MW"].shift(24)

# baseline 2: last week same hour
df["forecast_last_week_MW"] = df["actual_load_MW"].shift(24 * 7)

# baseline 3: rolling 24h average (shift(1) to avoid look-ahead)
df["forecast_rolling24_MW"] = (
    df["actual_load_MW"].shift(1).rolling(window=24, min_periods=1).mean()
)
print("Baseline forecasts added.")


# ----------------------------------------------------------------------------
# EVALUATION  (this whole block should really be its own module)
# ----------------------------------------------------------------------------
print("\nEvaluating forecasts ...")

# the same three metric formulas, written out again and again below


def mae(actual, forecast):
    return float((actual - forecast).abs().mean())


def rmse(actual, forecast):
    return float(np.sqrt(((actual - forecast) ** 2).mean()))


def mape(actual, forecast):
    actual = pd.Series(actual)
    forecast = pd.Series(forecast)
    mask = actual != 0
    pe = ((actual[mask] - forecast[mask]) / actual[mask]).abs()
    return float(pe.mean() * 100.0)


# evaluate official forecast
tmp = pd.DataFrame(
    {"actual": df["actual_load_MW"], "forecast": df["official_forecast_MW"]}
).dropna()
row_official = {
    "method": "Official day-ahead",
    "MAE_MW": round(mae(tmp["actual"], tmp["forecast"]), 2),
    "RMSE_MW": round(rmse(tmp["actual"], tmp["forecast"]), 2),
    "MAPE_%": round(mape(tmp["actual"], tmp["forecast"]), 2),
    "n_observations": len(tmp),
}

# evaluate yesterday-same-hour (copy-pasted block - notice the repetition)
tmp = pd.DataFrame(
    {"actual": df["actual_load_MW"], "forecast": df["forecast_yesterday_MW"]}
).dropna()
row_yesterday = {
    "method": "Yesterday-same-hour",
    "MAE_MW": round(mae(tmp["actual"], tmp["forecast"]), 2),
    "RMSE_MW": round(rmse(tmp["actual"], tmp["forecast"]), 2),
    "MAPE_%": round(mape(tmp["actual"], tmp["forecast"]), 2),
    "n_observations": len(tmp),
}

# evaluate last-week-same-hour (copy-pasted block again)
tmp = pd.DataFrame(
    {"actual": df["actual_load_MW"], "forecast": df["forecast_last_week_MW"]}
).dropna()
row_last_week = {
    "method": "Last-week-same-hour",
    "MAE_MW": round(mae(tmp["actual"], tmp["forecast"]), 2),
    "RMSE_MW": round(rmse(tmp["actual"], tmp["forecast"]), 2),
    "MAPE_%": round(mape(tmp["actual"], tmp["forecast"]), 2),
    "n_observations": len(tmp),
}

# evaluate rolling-24h (copy-pasted block yet again)
tmp = pd.DataFrame(
    {"actual": df["actual_load_MW"], "forecast": df["forecast_rolling24_MW"]}
).dropna()
row_rolling = {
    "method": "Rolling 24h average",
    "MAE_MW": round(mae(tmp["actual"], tmp["forecast"]), 2),
    "RMSE_MW": round(rmse(tmp["actual"], tmp["forecast"]), 2),
    "MAPE_%": round(mape(tmp["actual"], tmp["forecast"]), 2),
    "n_observations": len(tmp),
}

results = pd.DataFrame(
    [row_official, row_yesterday, row_last_week, row_rolling]
)
print("\n--- Forecast comparison ---")
print(results.to_string(index=False))


# ----------------------------------------------------------------------------
# VISUALIZATION  (this whole block should really be its own module)
# ----------------------------------------------------------------------------
print("\nSaving figures ...")
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

# figure 1: one week of demand
start = pd.to_datetime(f"{YEAR}-01-07", utc=True)
end = start + pd.Timedelta(days=7)
week_df = df.loc[(df["timestamp"] >= start) & (df["timestamp"] < end)]
fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(week_df["timestamp"], week_df["actual_load_MW"], color="steelblue")
ax.set_xlabel("Time")
ax.set_ylabel("Electricity load (MW)")
ax.set_title("German electricity demand, week of 2019-01-07")
fig.autofmt_xdate()
fig.tight_layout()
fig.savefig(FIGURES_DIR / "one_week_demand.png", dpi=150)
plt.close(fig)
print(f"  saved: {FIGURES_DIR / 'one_week_demand.png'}")

# figure 2: average by hour
by_hour = df.groupby("hour")["actual_load_MW"].mean()
fig, ax = plt.subplots(figsize=(8, 5))
ax.bar(by_hour.index, by_hour.values, color="steelblue")
ax.set_xlabel("Hour of day (0-23)")
ax.set_ylabel("Average electricity load (MW)")
ax.set_title("Average electricity demand by hour of day")
ax.set_xticks(range(0, 24))
fig.tight_layout()
fig.savefig(FIGURES_DIR / "average_demand_by_hour.png", dpi=150)
plt.close(fig)
print(f"  saved: {FIGURES_DIR / 'average_demand_by_hour.png'}")

# figure 3: average by day of week
day_order = [
    "Monday", "Tuesday", "Wednesday", "Thursday",
    "Friday", "Saturday", "Sunday",
]
by_day = df.groupby("day_name")["actual_load_MW"].mean().reindex(day_order)
fig, ax = plt.subplots(figsize=(8, 5))
ax.bar(by_day.index, by_day.values, color="darkorange")
ax.set_xlabel("Day of week")
ax.set_ylabel("Average electricity load (MW)")
ax.set_title("Average electricity demand by day of week")
fig.tight_layout()
fig.savefig(FIGURES_DIR / "average_demand_by_day.png", dpi=150)
plt.close(fig)
print(f"  saved: {FIGURES_DIR / 'average_demand_by_day.png'}")

# figure 4: average by month
by_month = df.groupby("month")["actual_load_MW"].mean()
fig, ax = plt.subplots(figsize=(8, 5))
ax.bar(by_month.index, by_month.values, color="seagreen")
ax.set_xlabel("Month")
ax.set_ylabel("Average electricity load (MW)")
ax.set_title("Average electricity demand by month")
ax.set_xticks(range(1, 13))
fig.tight_layout()
fig.savefig(FIGURES_DIR / "average_demand_by_month.png", dpi=150)
plt.close(fig)
print(f"  saved: {FIGURES_DIR / 'average_demand_by_month.png'}")

# figure 5: forecast comparison
start = pd.to_datetime(f"{YEAR}-06-03", utc=True)
end = start + pd.Timedelta(days=7)
period = df.loc[(df["timestamp"] >= start) & (df["timestamp"] < end)]
fig, ax = plt.subplots(figsize=(12, 6))
ax.plot(period["timestamp"], period["actual_load_MW"],
        label="Actual", color="black", linewidth=2)
ax.plot(period["timestamp"], period["official_forecast_MW"],
        label="Official day-ahead", color="tab:blue", linestyle="--")
ax.plot(period["timestamp"], period["forecast_yesterday_MW"],
        label="Yesterday-same-hour", color="tab:orange")
ax.plot(period["timestamp"], period["forecast_last_week_MW"],
        label="Last-week-same-hour", color="tab:green")
ax.plot(period["timestamp"], period["forecast_rolling24_MW"],
        label="Rolling 24h average", color="tab:red")
ax.set_xlabel("Time")
ax.set_ylabel("Electricity load (MW)")
ax.set_title("Forecast comparison, 7 days from 2019-06-03")
ax.legend(loc="best")
fig.autofmt_xdate()
fig.tight_layout()
fig.savefig(FIGURES_DIR / "forecast_comparison.png", dpi=150)
plt.close(fig)
print(f"  saved: {FIGURES_DIR / 'forecast_comparison.png'}")


# ----------------------------------------------------------------------------
# SAVE PROCESSED DATA + SUMMARY  (still the same file ...)
# ----------------------------------------------------------------------------
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
df.to_csv(PROCESSED_FILE, index=False)
print(f"\nCleaned dataset saved to: {PROCESSED_FILE}")

best_row = results.sort_values("MAE_MW").iloc[0]
print("\n--- Summary ---")
print(f"Year analysed     : {YEAR}")
print(f"Number of hours   : {len(df)}")
print(f"Best baseline     : {best_row['method']}")
print(f"  MAE  = {best_row['MAE_MW']} MW")
print(f"  RMSE = {best_row['RMSE_MW']} MW")
print(f"  MAPE = {best_row['MAPE_%']} %")
print("Done.")

# ----------------------------------------------------------------------------
# End of everything_in_one_file.py
#
# Notice the problems with this single-file approach:
#   - You have to scroll through ~290 lines to find anything.
#   - Config, data, forecasting, evaluation and plotting are all tangled.
#   - The metric evaluation block is copy-pasted four times.
#   - If two people edit this file at once, Git conflicts are almost certain.
#   - You cannot reuse the plotting code without running the whole script.
#   - It cannot be tested or imported piece by piece.
#
# This is exactly why the real project splits the work into src/ modules.
# ----------------------------------------------------------------------------
