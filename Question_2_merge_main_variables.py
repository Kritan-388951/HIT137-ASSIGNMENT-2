"""
Outputs three text files in the current directory.

Requirements: pandas (as of now, need to be looked further)
  pip install pandas ??

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

"""

import os
import glob
import pandas as pd

DATA_DIR = "temperatures"   # folder containing stations_group_YYYY.csv
OUTPUT_AVG = "average_temp.txt"
OUTPUT_RANGE = "largest_temp_range_station.txt"
OUTPUT_STABILITY = "temperature_stability_stations.txt"

MONTHS = ["January","February","March","April","May","June",
          "July","August","September","October","November","December"]

SEASON_MAP = {
    # Southern Hemisphere seasons
    "December": "Summer", "January": "Summer", "February": "Summer",
    "March": "Autumn", "April": "Autumn", "May": "Autumn",
    "June": "Winter", "July": "Winter", "August": "Winter",
    "September": "Spring", "October": "Spring", "November": "Spring",
}
SEASON_ORDER = ["Summer", "Autumn", "Winter", "Spring"]  # output order

ID_COLS = ["STATION_NAME", "STN_ID", "LAT", "LON"]

def load_all_csvs(data_dir: str) -> pd.DataFrame:
    """Load and vertically stack all station CSVs in long format."""
    pattern = os.path.join(data_dir, "stations_group_*.csv")
    files = sorted(glob.glob(pattern))
    if not files:
        raise FileNotFoundError(f"No files found matching {pattern}")

    long_rows = []
    for f in files:
        # infer year from filename if possible (not strictly required)
        try:
            year = int(os.path.basename(f).split("_")[-1].split(".")[0])
        except Exception:
            year = None

        df = pd.read_csv(f)
        # keep only known/expected columns
        keep = [c for c in ID_COLS + MONTHS if c in df.columns]
        missing_months = [m for m in MONTHS if m not in df.columns]
        if missing_months:
            # Not fatal; we’ll melt only the months that exist
            pass

        df = df[keep].copy()

        # melt months -> rows
        melt = df.melt(
            id_vars=[c for c in ID_COLS if c in df.columns],
            value_vars=[m for m in MONTHS if m in df.columns],
            var_name="Month",
            value_name="Temperature_C"
        )

        # attach year (optional, but may be useful)
        melt["Year"] = year

        # drop NaN temps
        melt = melt.dropna(subset=["Temperature_C"])
        long_rows.append(melt)

    out = pd.concat(long_rows, ignore_index=True)
    # enforce categorical month order (for any potential ordering)
    out["Month"] = pd.Categorical(out["Month"], categories=MONTHS, ordered=True)
   
    out["Season"] = out["Month"].map(SEASON_MAP)
    return out


def write_seasonal_averages(df: pd.DataFrame, out_path: str) -> None:
    """Compute overall seasonal averages (across all stations & years)."""
    seasonal = (
        df.groupby("Season", as_index=False)["Temperature_C"]
          .mean()
    )
    # Write in fixed season order; skip any seasons not present just in case
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
            stn_name = str(r["STATION_NAME"])
            stn_id = "NA" if pd.isna(r["STN_ID"]) else str(int(r["STN_ID"]))
            f.write(
                f"Station {stn_name} (ID: {stn_id}): "
                f"Range {r['Range']:.2f}°C (Max: {r['MaxTemp']:.2f}°C, Min: {r['MinTemp']:.2f}°C)\n"
            )

def write_stability(df: pd.DataFrame, out_path: str) -> None:
    """Compute per-station std dev (population, ddof=0), list most stable & most variable (ties allowed)."""
    stds = (
        df.groupby(["STATION_NAME","STN_ID"])["Temperature_C"]
          .std(ddof=0)   # population std dev across all available monthly points
          .reset_index(name="StdDev")
    )

    # musthandle rare case where a station might have <2 data points (std == NaN)
    stds = stds.dropna(subset=["StdDev"])

    min_std = stds["StdDev"].min()
    max_std = stds["StdDev"].max()

    most_stable = stds[stds["StdDev"] == min_std].sort_values(["STATION_NAME","STN_ID"])
    most_variable = stds[stds["StdDev"] == max_std].sort_values(["STATION_NAME","STN_ID"])

    with open(out_path, "w", encoding="utf-8") as f:
        f.write("Most Stable Station(s):\n")
        for _, r in most_stable.iterrows():
            stn_name = str(r["STATION_NAME"])
            stn_id = "NA" if pd.isna(r["STN_ID"]) else str(int(r["STN_ID"]))
            f.write(f"- {stn_name} (ID: {stn_id}): Std Dev {r['StdDev']:.2f}°C\n")

        f.write("\nMost Variable Station(s):\n")
        for _, r in most_variable.iterrows():
            stn_name = str(r["STATION_NAME"])
            stn_id = "NA" if pd.isna(r["STN_ID"]) else str(int(r["STN_ID"]))
            f.write(f"- {stn_name} (ID: {stn_id}): Std Dev {r['StdDev']:.2f}°C\n")
