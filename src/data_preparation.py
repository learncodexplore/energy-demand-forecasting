"""
data_preparation.py

Functions for loading and preparing the Open Power System Data
electricity demand dataset.

The functions are written in a beginner-friendly style:
each function does one clear thing and is documented with a short
docstring.
"""

import pandas as pd


# Direct CSV URL for the Open Power System Data, Time Series package.
# We read from this URL so that the large raw CSV does not need to be
# committed to GitHub.
DATA_URL = (
    "https://data.open-power-system-data.org/time_series/"
    "2020-10-06/time_series_60min_singleindex.csv"
)

# The three columns we need from the original dataset.
ORIGINAL_COLUMNS = [
    "utc_timestamp",
    "DE_load_actual_entsoe_transparency",
    "DE_load_forecast_entsoe_transparency",
]

# The friendly names we want to use in our project.
RENAME_MAP = {
    "utc_timestamp": "timestamp",
    "DE_load_actual_entsoe_transparency": "actual_load_MW",
    "DE_load_forecast_entsoe_transparency": "official_forecast_MW",
}


def load_dataset(url: str = DATA_URL) -> pd.DataFrame:
    """
    Load the full Open Power System Data CSV from the given URL.

    Only the three columns we need are loaded, to save memory and time.
    """
    print("Loading dataset from the online URL ...")
    df = pd.read_csv(url, usecols=ORIGINAL_COLUMNS)
    print(f"Dataset loaded. Shape: {df.shape}")
    return df


def rename_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Rename the original column names to friendly project names."""
    return df.rename(columns=RENAME_MAP)


def convert_timestamp(df: pd.DataFrame) -> pd.DataFrame:
    """Convert the timestamp column to a real pandas datetime type."""
    df = df.copy()
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    return df


def filter_by_year(df: pd.DataFrame, year: int) -> pd.DataFrame:
    """Keep only the rows of the given year."""
    mask = df["timestamp"].dt.year == year
    filtered = df.loc[mask].copy()
    print(f"Filtered to year {year}. Rows kept: {len(filtered)}")
    return filtered


def handle_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    """
    Handle missing values in the two load columns.

    Strategy (simple, beginner-friendly):
    - forward-fill (carry the last known value forward)
    - then back-fill any remaining gaps at the very start of the series
    """
    df = df.copy()
    n_missing_before = df[["actual_load_MW", "official_forecast_MW"]].isna().sum().sum()

    df["actual_load_MW"] = df["actual_load_MW"].ffill().bfill()
    df["official_forecast_MW"] = df["official_forecast_MW"].ffill().bfill()

    n_missing_after = df[["actual_load_MW", "official_forecast_MW"]].isna().sum().sum()
    print(f"Missing values filled: {n_missing_before} -> {n_missing_after} remaining")
    return df


def create_time_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Create useful time features from the timestamp column.

    These features help us describe the data and make simple baseline
    forecasts (e.g. "the same hour yesterday").
    """
    df = df.copy()
    df["hour"] = df["timestamp"].dt.hour
    df["day_of_week"] = df["timestamp"].dt.dayofweek  # 0 = Monday
    df["day_name"] = df["timestamp"].dt.day_name()
    df["month"] = df["timestamp"].dt.month
    df["date"] = df["timestamp"].dt.date
    return df


def prepare_dataset(year: int = 2019) -> pd.DataFrame:
    """
    Full data preparation pipeline:
    load -> rename -> convert timestamp -> filter year ->
    handle missing -> create time features.
    """
    df = load_dataset()
    df = rename_columns(df)
    df = convert_timestamp(df)
    df = filter_by_year(df, year)
    df = handle_missing_values(df)
    df = create_time_features(df)
    df = df.reset_index(drop=True)
    return df
