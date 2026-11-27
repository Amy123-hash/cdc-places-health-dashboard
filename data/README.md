# Data Folder

This folder contains the cleaned CDC PLACES county-level data used by the dashboard.

**Source:** CDC PLACES: Local Data for Better Health, County Data, 2025 Release.
https://data.cdc.gov/500-Cities-Places/PLACES-Local-Data-for-Better-Health-County-Data-20/swc5-untb

The raw CDC download is not committed to GitHub. It is cleaned with `src/clean_data.py`, and only the cleaned files are stored here.

## Files

### `places_county_clean_wide.csv` (used by the dashboard)

One row per county, using age-adjusted prevalence.

| Column | Description |
|---|---|
| `locationid` | 5-digit county FIPS code (read as text to keep leading zeros) |
| `stateabbr`, `statedesc` | State abbreviation and name |
| `locationname` | County name |
| `diabetes_pct` | Diabetes among adults (%) |
| `obesity_pct` | Obesity among adults (%) |
| `uninsured_pct` | Lack of health insurance among adults aged 18-64 (%) |
| `*_low`, `*_high` | Lower and upper confidence limits for each indicator |
| `totalpopulation`, `totalpop18plus` | County population and adult population |

### `places_county_clean_long.csv`

One row per county, measure and estimate type (age-adjusted and crude prevalence). It has the columns `year`, `stateabbr`, `statedesc`, `locationname`, `locationid`, `measureid`, `measure`, `data_value_type`, `data_value`, `low_confidence_limit`, `high_confidence_limit`, `totalpopulation` and `totalpop18plus`.

## Loading the data

Keep the county code as text so leading zeros are preserved:

```python
import pandas as pd

df = pd.read_csv("data/places_county_clean_wide.csv", dtype={"locationid": str})
```

## Regenerating the files

1. Download the county-level CSV from the source link above.
2. Run: `python src/clean_data.py <raw_file.csv> data`

## Notes

- PLACES values are model-based estimates, not direct survey counts. Use the confidence limits when comparing counties.
- Indicators: `DIABETES`, `OBESITY` and `ACCESS2` (lack of health insurance).
- Counties missing any of the three indicators are left out of the wide file.
