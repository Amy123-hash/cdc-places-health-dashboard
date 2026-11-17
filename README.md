# CDC PLACES Health Dashboard

Interactive dashboard for comparing county-level chronic disease and health indicators using CDC PLACES data.

<!-- Add a screenshot of the dashboard here once it is running:
![Dashboard screenshot](docs/screenshot.png) -->

## Project Overview

This project develops an interactive dashboard using CDC PLACES county-level data to explore and compare community health indicators across the United States.

The dashboard focuses on three health indicators:

| Indicator | PLACES measure ID |
|---|---|
| Diabetes among adults | `DIABETES` |
| Obesity among adults | `OBESITY` |
| Lack of health insurance among adults aged 18-64 | `ACCESS2` |

Users will be able to filter by state and county, compare indicators, and explore differences in estimated chronic disease burden across communities.

## Data Source

CDC PLACES: Local Data for Better Health, County Data, 2025 Release.

Dataset: https://data.cdc.gov/500-Cities-Places/PLACES-Local-Data-for-Better-Health-County-Data-20/swc5-untb

**Data notes:** PLACES values are model-based estimates, not direct survey counts for each county. Treat small differences between counties with caution, and use the confidence intervals included in the dataset when interpreting comparisons.

### Getting the data

The raw data is not committed to the repository (see `.gitignore`). To get it:

1. Download the county-level CSV from the dataset link above.
2. Save it in the `data/` directory (for example, `data/places_county.csv`).

## Technologies

- Python
- pandas
- Plotly
- Streamlit
- Jupyter (for the exploration notebook)
- GitHub

## Repository Structure

```
cdc-places-health-dashboard/
├── data/              # Place the downloaded PLACES CSV here (not tracked in Git)
├── notebooks/         # Data exploration (data_exploration.ipynb)
├── src/               # Data cleaning and analysis scripts
├── app.py             # Streamlit dashboard (planned)
├── requirements.txt   # Project dependencies
└── README.md
```

## Running the Project

1. Clone the repository and move into it:

   ```bash
 git clone <repository-url>
cd cdc-places-health-dashboard
   ```

2. Create and activate a virtual environment:

   ```bash
   python -m venv venv
   source venv/bin/activate      # macOS/Linux
   venv\Scripts\activate         # Windows
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Download the data into `data/`.

5. Explore the data in the notebook:

   ```bash
   jupyter notebook notebooks/data_exploration.ipynb
   ```

6. Launch the dashboard (once `app.py` is added):

   ```bash
   streamlit run app.py
   ```

## Team Members

- Taylor DiMenna
- Van Mont
- Afrah Beshir

## Project Status

Currently in development.

## License

To be determined by the team.
