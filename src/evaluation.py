"""
evaluation.py

Functions to evaluate forecast quality using simple error metrics.

Metrics:
- MAE   : Mean Absolute Error
- RMSE  : Root Mean Squared Error
- MAPE  : Mean Absolute Percentage Error
"""

import numpy as np
import pandas as pd


def mae(actual: pd.Series, forecast: pd.Series) -> float:
    """Mean Absolute Error."""
    diff = (actual - forecast).abs()
    return float(diff.mean())


def rmse(actual: pd.Series, forecast: pd.Series) -> float:
    """Root Mean Squared Error."""
    diff = (actual - forecast) ** 2
    return float(np.sqrt(diff.mean()))


def mape(actual: pd.Series, forecast: pd.Series) -> float:
    """
    Mean Absolute Percentage Error, expressed as a percentage.

    We protect against division by zero by ignoring rows where the
    actual value is 0.
    """
    actual = pd.Series(actual)
    forecast = pd.Series(forecast)

    mask = actual != 0
    safe_actual = actual[mask]
    safe_forecast = forecast[mask]

    percentage_errors = ((safe_actual - safe_forecast) / safe_actual).abs()
    return float(percentage_errors.mean() * 100.0)


def evaluate_forecast(
    actual: pd.Series, forecast: pd.Series, name: str
) -> dict:
    """
    Return a dictionary with the MAE, RMSE and MAPE of a single forecast.

    Rows with missing values are dropped before computing the metrics so
    that the baselines (which start with NaNs) can be evaluated fairly.
    """
    df = pd.DataFrame({"actual": actual, "forecast": forecast}).dropna()

    return {
        "method": name,
        "MAE_MW": round(mae(df["actual"], df["forecast"]), 2),
        "RMSE_MW": round(rmse(df["actual"], df["forecast"]), 2),
        "MAPE_%": round(mape(df["actual"], df["forecast"]), 2),
        "n_observations": len(df),
    }


def comparison_table(df: pd.DataFrame) -> pd.DataFrame:
    """
    Build a comparison table for all forecasts in the dataframe.

    The dataframe must contain:
    - actual_load_MW
    - official_forecast_MW
    - forecast_yesterday_MW
    - forecast_last_week_MW
    - forecast_rolling24_MW
    """
    actual = df["actual_load_MW"]

    rows = [
        evaluate_forecast(actual, df["official_forecast_MW"], "Official day-ahead"),
        evaluate_forecast(actual, df["forecast_yesterday_MW"], "Yesterday-same-hour"),
        evaluate_forecast(actual, df["forecast_last_week_MW"], "Last-week-same-hour"),
        evaluate_forecast(actual, df["forecast_rolling24_MW"], "Rolling 24h average"),
    ]

    return pd.DataFrame(rows)
