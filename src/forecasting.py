"""
forecasting.py

Simple baseline forecasting methods for electricity demand.

These are NOT machine learning models. They are simple rules
that often work surprisingly well for short-term demand forecasting:

1. Yesterday-same-hour:
   The forecast for time t is the actual load 24 hours earlier.

2. Last-week-same-hour:
   The forecast for time t is the actual load 7 days (168 hours) earlier.

3. Rolling-average (optional):
   The forecast for time t is the average of the previous N hours.
"""

import pandas as pd


def yesterday_same_hour_forecast(df: pd.DataFrame) -> pd.Series:
    """
    Return a forecast based on the actual load 24 hours earlier.

    For the first 24 hours we cannot make a forecast, so those values
    will be NaN.
    """
    return df["actual_load_MW"].shift(24)


def last_week_same_hour_forecast(df: pd.DataFrame) -> pd.Series:
    """
    Return a forecast based on the actual load 7 days earlier (168 hours).

    For the first 168 hours we cannot make a forecast, so those values
    will be NaN.
    """
    return df["actual_load_MW"].shift(24 * 7)


def rolling_average_forecast(df: pd.DataFrame, window_hours: int = 24) -> pd.Series:
    """
    Return a forecast based on the rolling average of the previous N hours.

    We use shift(1) so that the forecast for time t only uses data
    strictly before time t (no look-ahead).
    """
    return (
        df["actual_load_MW"]
        .shift(1)
        .rolling(window=window_hours, min_periods=1)
        .mean()
    )


def add_baseline_forecasts(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add all baseline forecast columns to the dataframe.

    New columns:
    - forecast_yesterday_MW
    - forecast_last_week_MW
    - forecast_rolling24_MW
    """
    df = df.copy()
    df["forecast_yesterday_MW"] = yesterday_same_hour_forecast(df)
    df["forecast_last_week_MW"] = last_week_same_hour_forecast(df)
    df["forecast_rolling24_MW"] = rolling_average_forecast(df, window_hours=24)
    return df
