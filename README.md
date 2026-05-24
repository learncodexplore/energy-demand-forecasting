# Energy Demand Forecasting

A small, company-style data project for Environmental Engineering students.
The project shows how to structure a real Python data project using
VS Code, Git, GitHub, pandas and matplotlib, and how to compare simple
baseline forecasts of electricity demand against the official
day-ahead forecast.

---

## 1. Project summary

A small energy analytics team wants to understand electricity demand
patterns in Germany and compare simple baseline forecasting methods
against the official day-ahead forecast published by the ENTSO-E
transparency platform. The goal is to build a clean, reproducible
Python workflow that can later be extended with machine learning
models.

The project produces:

- A cleaned hourly electricity demand dataset for one year.
- Baseline forecasts using simple, transparent rules.
- A table of error metrics (MAE, RMSE, MAPE).
- A set of figures saved to `reports/figures/`.
- A short results summary printed in the terminal.

---

## 2. Environmental engineering motivation

Electricity demand forecasting is one of the most important data
problems in modern energy systems. Good forecasts directly support
sustainability and environmental goals:

- **Grid planning** – operators must balance supply and demand in
  real time. Better forecasts reduce the risk of blackouts and the
  need for spinning reserves.
- **Renewable integration** – wind and solar generation is variable.
  Understanding demand patterns helps integrate larger shares of
  renewables.
- **Energy efficiency** – knowing daily and seasonal demand patterns
  helps identify peaks that can be reduced through demand-side
  management.
- **Reducing fossil backup power** – accurate forecasts reduce the
  need to keep fossil-fuelled plants running "just in case".
- **Consumption patterns** – studying hourly, weekly and monthly
  variation reveals how human activity drives energy use.
- **Sustainable energy systems** – data-driven forecasting is a
  building block for smart grids, electric mobility and
  sector coupling.

---

## 3. Business / company-style problem statement

> **Context.** A small German energy analytics team wants to assess
> whether *simple, transparent* forecasting rules can compete with the
> official day-ahead forecast that the transmission system operators
> publish on the ENTSO-E transparency platform.
>
> **Question.** Can simple baseline forecasting methods provide useful
> short-term electricity demand forecasts?
>
> **Deliverable.** A reproducible Python project that loads one year
> of hourly demand data, computes three baseline forecasts, compares
> them with the official forecast, and reports the results in a clean
> way that a future machine-learning project can build on.

---

## 4. Dataset

The project uses the **Open Power System Data** *Time Series* package,
release **2020-10-06**.

- Project page: <https://data.open-power-system-data.org/time_series/>
- Direct CSV (hourly):
  <https://data.open-power-system-data.org/time_series/2020-10-06/time_series_60min_singleindex.csv>

The CSV is **not committed** to the repository. The project reads it
directly from the URL using `pandas.read_csv`. A smaller cleaned CSV
for one year is saved into `data/processed/`.

### 4.1 Selected columns

| Original column                          | Renamed to              | Meaning                                       |
|------------------------------------------|-------------------------|-----------------------------------------------|
| `utc_timestamp`                          | `timestamp`             | UTC timestamp at hourly resolution            |
| `DE_load_actual_entsoe_transparency`     | `actual_load_MW`        | Actual electricity load in Germany, in MW     |
| `DE_load_forecast_entsoe_transparency`   | `official_forecast_MW`  | Day-ahead forecast published by ENTSO-E, MW   |

### 4.2 Citation

> Open Power System Data. 2020. Data Package Time series.
> Version 2020-10-06. <https://data.open-power-system-data.org/time_series/2020-10-06/>.
> (Primary data from various sources, see project page.)

---

## 5. Project structure

```
energy-demand-forecasting/
│
├── data/
│   ├── raw/                  # large raw files (not committed)
│   └── processed/            # cleaned dataset for one year
│
├── notebooks/
│   └── 00_data_verification.ipynb   # quick checks only
│
├── reports/
│   ├── figures/              # all generated PNG figures
│   └── report_outline.md     # writing guide for the ~20-page report
│
├── src/
│   ├── __init__.py
│   ├── data_preparation.py   # load, clean, time features
│   ├── forecasting.py        # baseline forecast methods
│   ├── evaluation.py         # MAE, RMSE, MAPE, comparison table
│   └── visualization.py      # plotting functions
│
├── .gitignore
├── README.md                 # <-- main documentation
├── requirements.txt
└── main.py                   # main entry point
```

---

## 6. Setup instructions (Windows, Command Prompt)

Open **Command Prompt** (`cmd.exe`), not PowerShell, and run:

```bat
mkdir energy-demand-forecasting
cd energy-demand-forecasting
code .
python -m venv venv
venv\Scripts\activate
pip install pandas numpy matplotlib scikit-learn jupyter
pip freeze > requirements.txt
git init
git add .
git commit -m "Initial project structure"
```

Connect the local project to GitHub (replace `USERNAME`):

```bat
git remote add origin https://github.com/USERNAME/energy-demand-forecasting.git
git branch -M main
git push -u origin main
```

> If you re-open the project later, simply run
> `venv\Scripts\activate` from the project folder to re-activate the
> virtual environment.

---

## 7. How to run the project in VS Code

1. Open the project folder in VS Code (`code .` from Command Prompt).
2. Open a **new terminal** inside VS Code (`Terminal -> New Terminal`).
   Make sure the terminal type is **Command Prompt** (the small drop-down
   next to the `+` icon).
3. Activate the virtual environment in that terminal:
   ```bat
   venv\Scripts\activate
   ```
4. (Optional) Open `notebooks/00_data_verification.ipynb` and run the
   cells to verify the environment and the dataset.
5. Run the main script:
   ```bat
   python main.py
   ```
6. Check the generated figures in `reports/figures/` and the cleaned
   dataset in `data/processed/`.

---

## 8. Workflow

```
Online CSV  ─►  data_preparation  ─►  cleaned dataframe
                                       │
                                       ▼
                                  forecasting  ─►  baseline forecasts added
                                       │
                                       ▼
                                  evaluation   ─►  MAE / RMSE / MAPE table
                                       │
                                       ▼
                                  visualization ─►  PNG figures
                                       │
                                       ▼
                                  data/processed/germany_load_2019_clean.csv
```

`main.py` is the orchestrator. It calls the functions from the `src/`
package in the order above.

---

## 9. Baseline forecasting methods

This project uses **only simple, transparent baselines** – no machine
learning. The methods are:

1. **Yesterday-same-hour.**
   The forecast for hour *t* equals the actual load at hour *t − 24h*.
   *Idea:* electricity demand has a strong daily pattern.

2. **Last-week-same-hour.**
   The forecast for hour *t* equals the actual load at hour *t − 168h*
   (7 days). *Idea:* demand also has a weekly pattern (workdays
   vs. weekends).

3. **Rolling 24-hour average.**
   The forecast for hour *t* equals the average of the previous 24
   actual values. *Idea:* a smoothed recent level.

All three are compared against the **official day-ahead forecast**
already provided in the dataset.

---

## 10. Results produced by the project

After running `python main.py` you will see:

- A terminal printout with the comparison table:
  ```
  method               MAE_MW  RMSE_MW  MAPE_%  n_observations
  Official day-ahead   ...     ...      ...     ...
  Yesterday-same-hour  ...     ...      ...     ...
  Last-week-same-hour  ...     ...      ...     ...
  Rolling 24h average  ...     ...      ...     ...
  ```
- A short summary highlighting the best baseline method.
- A cleaned CSV at `data/processed/germany_load_2019_clean.csv`.

---

## 11. How figures are saved

All figures are produced with matplotlib in the object-oriented style:

```python
fig, ax = plt.subplots()
ax.plot(...)
ax.set_xlabel(...)
ax.set_ylabel(...)
ax.set_title(...)
fig.savefig("reports/figures/<name>.png", dpi=150)
```

The following figures are saved in `reports/figures/`:

| Filename                       | Content                                   |
|--------------------------------|-------------------------------------------|
| `one_week_demand.png`          | One week of hourly actual demand          |
| `average_demand_by_hour.png`   | Average demand by hour of day             |
| `average_demand_by_day.png`    | Average demand by day of week             |
| `average_demand_by_month.png`  | Average demand by month                   |
| `forecast_comparison.png`      | Actual demand vs. all forecasts, 7 days   |

These figures can be inserted directly into the project report.

---

## 12. Report writing guidance

The coding project is **only one half** of the deliverable. The other
half is a written report of about **20 pages**. A detailed outline is
provided in [`reports/report_outline.md`](reports/report_outline.md),
including a recommended page distribution.

The report should clearly present:

- Project topic and motivation (environmental engineering view).
- Dataset, methodology and implementation choices.
- Results (use the figures saved by the project).
- Discussion, conclusions and ideas for future work.
- A proper list of references in a consistent citation style.

---

## 13. Future machine-learning extension

The project is intentionally simple, but it is structured so that an
ML extension can be added later without rewriting everything:

- `src/data_preparation.py` already produces useful features
  (`hour`, `day_of_week`, `month`, …).
- `src/forecasting.py` could be extended with, for example:
  - Linear regression on the time features.
  - A regression tree or random forest.
  - A gradient boosting model.
  - A small recurrent neural network.
- `src/evaluation.py` and the comparison table can stay the same –
  any new model is just one more row in the table.

This makes the project a natural starting point for a follow-up
course on data-driven energy analytics.

---

## 14. References

- Open Power System Data. *Time series* package, version 2020-10-06.
  <https://data.open-power-system-data.org/time_series/>
- ENTSO-E Transparency Platform.
  <https://transparency.entsoe.eu/>
- pandas documentation. <https://pandas.pydata.org/docs/>
- matplotlib documentation. <https://matplotlib.org/stable/>
- Hyndman, R. J., & Athanasopoulos, G. (2021).
  *Forecasting: Principles and Practice* (3rd ed.). OTexts.
  <https://otexts.com/fpp3/>
