"""
visualization.py

Plotting functions for the electricity demand project.

All plots use the matplotlib object-oriented style
(fig, ax = plt.subplots()) and save figures to reports/figures/.
"""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


# Default folder where all figures are saved.
FIGURES_DIR = Path("reports") / "figures"


def _ensure_figures_dir() -> Path:
    """Make sure the figures folder exists, then return its path."""
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    return FIGURES_DIR


def plot_one_week(df: pd.DataFrame, start_date: str = "2019-01-07") -> Path:
    """
    Plot actual electricity load for one week starting at start_date.

    start_date is given as a string like '2019-01-07' (a Monday is nice
    for readability).
    """
    figures_dir = _ensure_figures_dir()

    start = pd.to_datetime(start_date, utc=True)
    end = start + pd.Timedelta(days=7)
    mask = (df["timestamp"] >= start) & (df["timestamp"] < end)
    week_df = df.loc[mask]

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(week_df["timestamp"], week_df["actual_load_MW"], color="steelblue")
    ax.set_xlabel("Time")
    ax.set_ylabel("Electricity load (MW)")
    ax.set_title(f"German electricity demand, week of {start_date}")
    fig.autofmt_xdate()
    fig.tight_layout()

    out_path = figures_dir / "one_week_demand.png"
    fig.savefig(out_path, dpi=150)
    plt.close(fig)
    return out_path


def plot_average_by_hour(df: pd.DataFrame) -> Path:
    """Plot the average electricity demand by hour of day."""
    figures_dir = _ensure_figures_dir()

    by_hour = df.groupby("hour")["actual_load_MW"].mean()

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(by_hour.index, by_hour.values, color="steelblue")
    ax.set_xlabel("Hour of day (0-23)")
    ax.set_ylabel("Average electricity load (MW)")
    ax.set_title("Average electricity demand by hour of day")
    ax.set_xticks(range(0, 24))
    fig.tight_layout()

    out_path = figures_dir / "average_demand_by_hour.png"
    fig.savefig(out_path, dpi=150)
    plt.close(fig)
    return out_path


def plot_average_by_day(df: pd.DataFrame) -> Path:
    """Plot the average electricity demand by day of week."""
    figures_dir = _ensure_figures_dir()

    day_order = [
        "Monday", "Tuesday", "Wednesday", "Thursday",
        "Friday", "Saturday", "Sunday",
    ]
    by_day = (
        df.groupby("day_name")["actual_load_MW"]
        .mean()
        .reindex(day_order)
    )

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(by_day.index, by_day.values, color="darkorange")
    ax.set_xlabel("Day of week")
    ax.set_ylabel("Average electricity load (MW)")
    ax.set_title("Average electricity demand by day of week")
    fig.tight_layout()

    out_path = figures_dir / "average_demand_by_day.png"
    fig.savefig(out_path, dpi=150)
    plt.close(fig)
    return out_path


def plot_average_by_month(df: pd.DataFrame) -> Path:
    """Plot the average electricity demand by month."""
    figures_dir = _ensure_figures_dir()

    by_month = df.groupby("month")["actual_load_MW"].mean()

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(by_month.index, by_month.values, color="seagreen")
    ax.set_xlabel("Month")
    ax.set_ylabel("Average electricity load (MW)")
    ax.set_title("Average electricity demand by month")
    ax.set_xticks(range(1, 13))
    fig.tight_layout()

    out_path = figures_dir / "average_demand_by_month.png"
    fig.savefig(out_path, dpi=150)
    plt.close(fig)
    return out_path


def plot_forecast_comparison(
    df: pd.DataFrame,
    start_date: str = "2019-06-03",
    days: int = 7,
) -> Path:
    """
    Plot the actual demand together with the different forecasts for a
    selected period of length 'days'.
    """
    figures_dir = _ensure_figures_dir()

    start = pd.to_datetime(start_date, utc=True)
    end = start + pd.Timedelta(days=days)
    mask = (df["timestamp"] >= start) & (df["timestamp"] < end)
    period = df.loc[mask]

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
    ax.set_title(f"Forecast comparison, {days} days from {start_date}")
    ax.legend(loc="best")
    fig.autofmt_xdate()
    fig.tight_layout()

    out_path = figures_dir / "forecast_comparison.png"
    fig.savefig(out_path, dpi=150)
    plt.close(fig)
    return out_path
