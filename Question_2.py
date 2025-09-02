"""
Outputs three text files in the current directory.

Requirements: pandas (as of now, need to be looked further)
  pip install pandas ?? yes required

This Python code is for reading the directory, reading as well as loading
the CSV Files from the targeted directory. (Multi-year, multi-station temperature analytics)

After that, the next step will be to add months and their respective seasons. 
so that it reads all CSVs from ./temperatures/, computes:
 1) Seasonal average temperatures (AU seasons)
 2) Station(s) with largest overall temperature range (max - min)
 3) Temperature stability: stations with min/max std dev

We will also choose our destination target names for: Average Temperature, Largest Temperature
Range as well as Temperature Stability Stations. For now the output will  directly be on the root.

CODEEEEEEEEEE
Option 1:
The best and first way to read, extract and load the data files in order to get the
information would be to use a function with a For Loop and expect where the problems might arise beoforehand.
Aiming to make it intp multiple py files that will be called by the main "main" but couldn't make it right.

Option 2:
#i need coffee
althoug clutterd and a very long string of code, it was much more prefferd to make the code in one python file.
no need to call it to main so, only one to call everything and run. removes the undefined error. makes the console graceful.
Optimization won't be easy as well as debugging depending on how the code handles the variables.
I'll use the datetime package to make the output much more robust. the comments must be absolute to understand each section for other participants.
Null data variable needs more work, but not the priority as it is handling the files as expected.
Have not checked if this works for other files.
Upgrade the warning system if a corrupted/ unknown files gets into the data files.
"""

import os
import glob
from datetime import datetime
from typing import List
import pandas as pd

DATA_DIR = "temperatures"   # folder containing stations_group_YYYY.csv
OUTPUTS_ROOT = "outputs"    # root folder for all runs

MONTHS: List[str] = [
    "January","February","March","April","May","June",
    "July","August","September","October","November","December"
]

# Southern Hemisphere seasons
SEASON_MAP = {
    "December": "Summer", "January": "Summer", "February": "Summer",
    "March": "Autumn", "April": "Autumn", "May": "Autumn",
    "June": "Winter", "July": "Winter", "August": "Winter",
    "September": "Spring", "October": "Spring", "November": "Spring",
}
SEASON_ORDER = ["Summer", "Autumn", "Winter", "Spring"]  # fixed output order

ID_COLS = ["STATION_NAME", "STN_ID", "LAT", "LON"]

def _fmt_stn_id(x) -> str:
    """Format station ID robustly for text output."""
    if pd.isna(x):
        return "NA"
    try:
        return str(int(float(x)))  # 23090.0 -> "23090"
    except Exception:
        return str(x)

def _make_run_dir() -> str:
    """Create a timestamped run directory (e.g., outputs/2025-09-02_23-14-07/)."""
    stamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    run_dir = os.path.join(OUTPUTS_ROOT, stamp)
    os.makedirs(run_dir, exist_ok=True)
    return run_dir

def load_all_csvs(data_dir: str) -> pd.DataFrame:
    """Load all station CSVs and return a long-format dataframe."""
    pattern = os.path.join(data_dir, "stations_group_*.csv")
    files = sorted(glob.glob(pattern))
    if not files:
        raise FileNotFoundError(f"No files found matching {pattern}")

    long_rows = []
    for f in files:
        # infer year from filename (not needed for outputs, but useful)
        try:
            year = int(os.path.basename(f).split("_")[-1].split(".")[0])
        except Exception:
            year = None

        df = pd.read_csv(f)

        # Keep expected columns that actually exist
        keep = [c for c in ID_COLS + MONTHS if c in df.columns]
        if not keep:
            continue  # no useful columns in this file
        df = df[keep].copy()

        # Melt months to rows (only for months present)
        present_months = [m for m in MONTHS if m in df.columns]
        melt = df.melt(
            id_vars=[c for c in ID_COLS if c in df.columns],
            value_vars=present_months,
            var_name="Month",
            value_name="Temperature_C"
        )

        # Coerce to numeric, drop NaNs
        melt["Temperature_C"] = pd.to_numeric(melt["Temperature_C"], errors="coerce")
        melt = melt.dropna(subset=["Temperature_C"])

        # Attach year, month order, and season
        melt["Year"] = year
        melt["Month"] = pd.Categorical(melt["Month"], categories=MONTHS, ordered=True)
        melt["Season"] = melt["Month"].map(SEASON_MAP)

        # Drop any rows that couldn't map to a season (shouldn't happen if months are standard)
        melt = melt.dropna(subset=["Season"])

        long_rows.append(melt)

    if not long_rows:
        raise ValueError("No usable temperature rows found after loading CSVs.")
    return pd.concat(long_rows, ignore_index=True)

def write_seasonal_averages(df: pd.DataFrame, out_path: str) -> None:
    """Compute overall seasonal averages (across all stations & years)."""
    seasonal = df.groupby("Season", as_index=False)["Temperature_C"].mean()
    # Write in fixed season order
    with open(out_path, "w", encoding="utf-8") as f:
        for season in SEASON_ORDER:
            row = seasonal[seasonal["Season"] == season]
            if not row.empty:
                val = float(row["Temperature_C"].iloc[0])
                f.write(f"{season}: {val:.2f}°C\n")

def write_largest_range(df: pd.DataFrame, out_path: str) -> None:
    """Find station(s) with largest temperature range across all months/years."""
    agg = df.groupby(["STATION_NAME","STN_ID"], as_index=False).agg(
        MaxTemp=("Temperature_C","max"),
        MinTemp=("Temperature_C","min")
    )
    agg["Range"] = agg["MaxTemp"] - agg["MinTemp"]
    max_range = agg["Range"].max()
    winners = agg[agg["Range"] == max_range].sort_values(["STATION_NAME","STN_ID"])

    with open(out_path, "w", encoding="utf-8") as f:
        for _, r in winners.iterrows():
            f.write(
                f"Station {r['STATION_NAME']} (ID: {_fmt_stn_id(r['STN_ID'])}): "
                f"Range {r['Range']:.2f}°C (Max: {r['MaxTemp']:.2f}°C, Min: {r['MinTemp']:.2f}°C)\n"
            )

def write_stability(df: pd.DataFrame, out_path: str) -> None:
    """Compute per-station std dev (population, ddof=0). List most stable & most variable (ties allowed)."""
    stds = (
        df.groupby(["STATION_NAME","STN_ID"])["Temperature_C"]
          .std(ddof=0)                 # population std dev
          .reset_index(name="StdDev")
          .dropna(subset=["StdDev"])   # drop stations with <2 data points
    )

    min_std = stds["StdDev"].min()
    max_std = stds["StdDev"].max()
    most_stable = stds[stds["StdDev"] == min_std].sort_values(["STATION_NAME","STN_ID"])
    most_variable = stds[stds["StdDev"] == max_std].sort_values(["STATION_NAME","STN_ID"])

    with open(out_path, "w", encoding="utf-8") as f:
        f.write("Most Stable Station(s):\n")
        for _, r in most_stable.iterrows():
            f.write(f"- {r['STATION_NAME']} (ID: {_fmt_stn_id(r['STN_ID'])}): Std Dev {r['StdDev']:.2f}°C\n")
        f.write("\nMost Variable Station(s):\n")
        for _, r in most_variable.iterrows():
            f.write(f"- {r['STATION_NAME']} (ID: {_fmt_stn_id(r['STN_ID'])}): Std Dev {r['StdDev']:.2f}°C\n")

def main() -> None:
    # Prepare unique run folder
    run_dir = _make_run_dir()

    # Full output paths inside this run folder
    path_avg  = os.path.join(run_dir, "average_temp.txt")
    path_rng  = os.path.join(run_dir, "largest_temp_range_station.txt")
    path_std  = os.path.join(run_dir, "temperature_stability_stations.txt")

    # Load and compute
    df = load_all_csvs(DATA_DIR)
    write_seasonal_averages(df, path_avg)
    write_largest_range(df, path_rng)
    write_stability(df, path_std)

    # Console summary
    print(f"Files processed from: {DATA_DIR}")
    print(f"Unique stations: {df['STATION_NAME'].nunique()}")
    print(f"Data points: {len(df)}")
    print(f"Outputs written to: {run_dir}")
    print("Generated files:")
    print(f" - {os.path.basename(path_avg)}")
    print(f" - {os.path.basename(path_rng)}")
    print(f" - {os.path.basename(path_std)}")

if __name__ == "__main__":
    main()
