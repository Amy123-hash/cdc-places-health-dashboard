"""
Clean the CDC PLACES county-level data for the dashboard.

Input : the raw PLACES county CSV downloaded from data.cdc.gov
Output: two files written to the output folder
    - places_county_clean_long.csv : one row per county / measure / estimate type
    - places_county_clean_wide.csv : one row per county, one column per indicator
                                     (this is the file the dashboard should load)

How to run
----------
Command line / Colab:
    python clean_data.py <raw_file.csv> <output_folder>
    !python clean_data.py "/content/raw_file.csv" /content/cleaned

With no arguments it looks for a file named PLACES*.csv in /content (Colab)
or the current folder, and writes to a folder called "cleaned".

In a notebook cell (after pasting this script into a cell):
    clean_places("/content/raw_file.csv", "/content/cleaned")
"""

import sys
from pathlib import Path

import pandas as pd

# ----------------------------------------------------------------------------
# Settings
# ----------------------------------------------------------------------------
# PLACES measure IDs for the three dashboard indicators
MEASURES = {
    "DIABETES": "diabetes_pct",
    "OBESITY": "obesity_pct",
    "ACCESS2": "uninsured_pct",  # lack of health insurance, adults 18-64
}

# "Age-adjusted prevalence" is better for comparing counties;
# "Crude prevalence" is the raw model estimate. Change here if needed.
PREFERRED_TYPE = "Age-adjusted prevalence"

KEEP_COLUMNS = [
    "year",
    "stateabbr",
    "statedesc",
    "locationname",
    "locationid",
    "measureid",
    "measure",
    "data_value_type",
    "data_value",
    "low_confidence_limit",
    "high_confidence_limit",
    "totalpopulation",
    "totalpop18plus",
]


def clean_places(input_path, output_dir="cleaned"):
    """Read the raw PLACES CSV, clean it, and write the cleaned files."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # --- 1. Load -------------------------------------------------------------
    df = pd.read_csv(input_path, dtype=str, low_memory=False)
    print(f"Raw data: {len(df):,} rows, {df.shape[1]} columns")

    # Standardize column names (the CSV and the API use different capitalization)
    df.columns = df.columns.str.strip().str.lower()

    missing = [c for c in KEEP_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(
            f"Expected columns not found in the file: {missing}\n"
            f"Columns in your file: {df.columns.tolist()}"
        )

    # --- 2. Keep only what the dashboard needs -------------------------------
    df = df[KEEP_COLUMNS].copy()
    df["measureid"] = df["measureid"].str.strip().str.upper()
    df = df[df["measureid"].isin(MEASURES)]
    print(f"After keeping the 3 indicators: {len(df):,} rows")

    # --- 3. Fix data types ---------------------------------------------------
    numeric_cols = [
        "year",
        "data_value",
        "low_confidence_limit",
        "high_confidence_limit",
        "totalpopulation",
        "totalpop18plus",
    ]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # County FIPS code must stay a 5-character text value (leading zeros matter)
    df["locationid"] = df["locationid"].str.strip().str.zfill(5)

    for col in ["stateabbr", "statedesc", "locationname", "data_value_type"]:
        df[col] = df[col].str.strip()

    # --- 4. Remove bad rows --------------------------------------------------
    before = len(df)
    df = df.dropna(subset=["data_value", "locationid"])
    print(f"Dropped {before - len(df):,} rows with no estimate or no county ID")

    # Keep one row per county / measure / type (latest year wins)
    before = len(df)
    df = (
        df.sort_values("year", kind="mergesort")
        .drop_duplicates(["locationid", "measureid", "data_value_type"], keep="last")
        .sort_values(["statedesc", "locationname", "measureid", "data_value_type"])
        .reset_index(drop=True)
    )
    print(f"Dropped {before - len(df):,} duplicate rows")

    # --- 5. Save the long version -------------------------------------------
    long_path = output_dir / "places_county_clean_long.csv"
    df.to_csv(long_path, index=False)

    # --- 6. Build the wide version (one row per county) ----------------------
    available_types = df["data_value_type"].unique().tolist()
    if PREFERRED_TYPE not in available_types:
        raise ValueError(
            f"'{PREFERRED_TYPE}' not found. Available types: {available_types}"
        )

    subset = df[df["data_value_type"] == PREFERRED_TYPE]
    index_cols = ["locationid", "stateabbr", "statedesc", "locationname"]

    wide = subset.pivot(
        index=index_cols, columns="measureid", values="data_value"
    ).rename(columns=MEASURES)

    # Confidence limits per indicator
    for col, suffix in [("low_confidence_limit", "low"), ("high_confidence_limit", "high")]:
        ci = subset.pivot(
            index=index_cols, columns="measureid", values=col
        ).rename(columns={k: f"{v}_{suffix}" for k, v in MEASURES.items()})
        wide = wide.join(ci)

    pop = subset.groupby("locationid")[["totalpopulation", "totalpop18plus"]].first()
    wide = wide.reset_index().merge(pop, on="locationid", how="left")

    # Put columns in a predictable order
    ordered = index_cols + list(MEASURES.values())
    ordered += [f"{v}_{s}" for v in MEASURES.values() for s in ("low", "high")]
    ordered += ["totalpopulation", "totalpop18plus"]
    wide = wide[[c for c in ordered if c in wide.columns]]

    # Counties missing any of the three indicators can't be compared fairly
    indicator_cols = list(MEASURES.values())
    incomplete = wide[indicator_cols].isna().any(axis=1).sum()
    if incomplete:
        print(f"Note: {incomplete:,} counties are missing at least one indicator")
    wide = wide.dropna(subset=indicator_cols).reset_index(drop=True)

    wide_path = output_dir / "places_county_clean_wide.csv"
    wide.to_csv(wide_path, index=False)

    # --- 7. Summary ----------------------------------------------------------
    print(f"\nDone. Estimate type used for the wide file: {PREFERRED_TYPE}")
    print(f"  {long_path}  ({len(df):,} rows)")
    print(f"  {wide_path}  ({len(wide):,} counties, {wide['statedesc'].nunique()} states/DC)")
    print("\nQuick check of indicator ranges (percent):")
    print(wide[indicator_cols].describe().loc[["min", "mean", "max"]].round(1))
    return df, wide


def _find_raw_file():
    """Look for a PLACES CSV in /content (Colab) or the current folder."""
    for folder in (Path("/content"), Path(".")):
        matches = sorted(folder.glob("PLACES*.csv"))
        if matches:
            return matches[0]
    return None


def main(argv):
    args = [a for a in argv[1:] if not a.startswith("-")]
    if args:
        input_path = args[0]
        output_dir = args[1] if len(args) > 1 else "cleaned"
    else:
        found = _find_raw_file()
        if found is None:
            print("Usage: python clean_data.py <raw_file.csv> [output_folder]")
            return
        print(f"Using raw file: {found}")
        input_path, output_dir = found, "cleaned"
    clean_places(input_path, output_dir)


if __name__ == "__main__" and "ipykernel" not in sys.modules:
    main(sys.argv)
