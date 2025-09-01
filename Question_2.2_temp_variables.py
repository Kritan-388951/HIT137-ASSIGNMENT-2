
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
