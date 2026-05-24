"""
main.py

Main entry point for the Energy Demand Forecasting project.

Run from the project root with:

    python main.py

Workflow:
1. Load the dataset from the online URL.
2. Select and rename the required columns.
3. Convert the timestamp column to datetime.
4. Filter one year of data (default: 2019).
5. Handle missing values.
6. Create time features (hour, day of week, month, ...).
7. Compute baseline forecasts.
8. Evaluate the forecasts (MAE, RMSE, MAPE).
9. Save figures to reports/figures/.
10. Save the cleaned dataset to data/processed/.
11. Print a results summary to the terminal.
"""

from pathlib import Path

import pandas as pd

from src.data_preparation import prepare_dataset
from src.forecasting import add_baseline_forecasts
from src.evaluation import comparison_table
from src.visualization import (
    plot_one_week,
    plot_average_by_hour,
    plot_average_by_day,
    plot_average_by_month,
    plot_forecast_comparison,
)


# Configuration
YEAR = 2019
PROCESSED_DIR = Path("data") / "processed"
PROCESSED_FILE = PROCESSED_DIR / f"germany_load_{YEAR}_clean.csv"


def main() -> None:
    print("=" * 60)
    print("  Energy Demand Forecasting - Baseline Project")
    print("=" * 60)

    # Step 1-6: data preparation pipeline
    df = prepare_dataset(year=YEAR)
    print(f"Prepared dataset shape: {df.shape}")
    print(f"Date range: {df['timestamp'].min()} -> {df['timestamp'].max()}")

    # Step 7: baseline forecasts
    df = add_baseline_forecasts(df)
    print("Baseline forecasts added.")

    # Step 8: evaluation
    print("\nEvaluating forecasts ...")
    results = comparison_table(df)
    print("\n--- Forecast comparison ---")
    print(results.to_string(index=False))

    # Step 9: figures
    print("\nSaving figures ...")
    saved_paths = [
        plot_one_week(df, start_date=f"{YEAR}-01-07"),
        plot_average_by_hour(df),
        plot_average_by_day(df),
        plot_average_by_month(df),
        plot_forecast_comparison(df, start_date=f"{YEAR}-06-03", days=7),
    ]
    for p in saved_paths:
        print(f"  saved: {p}")

    # Step 10: save processed dataset
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(PROCESSED_FILE, index=False)
    print(f"\nCleaned dataset saved to: {PROCESSED_FILE}")

    # Step 11: summary
    best_row = results.sort_values("MAE_MW").iloc[0]
    print("\n--- Summary ---")
    print(f"Year analysed     : {YEAR}")
    print(f"Number of hours   : {len(df)}")
    print(f"Best baseline     : {best_row['method']}")
    print(f"  MAE  = {best_row['MAE_MW']} MW")
    print(f"  RMSE = {best_row['RMSE_MW']} MW")
    print(f"  MAPE = {best_row['MAPE_%']} %")
    print("Done.")


if __name__ == "__main__":
    main()
