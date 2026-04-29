# Housing Affordability Tracker

Tracks rent-to-income ratios, cost burden, and affordability trends across 30 US metros using real public data from the Census Bureau, HUD, and the Federal Reserve.

## Stack
- **Data**: Census ACS, HUD Fair Market Rents, FRED (St. Louis Fed)
- **Frontend**: Vanilla HTML/CSS/JS + Chart.js (zero dependencies)
- **Optional backend**: `fetch_data.py` to pull live data via free APIs

## Quick Start (no API keys needed)
```bash
open index.html
```
The frontend ships with embedded 2023 data. Works immediately.

## Live Data Setup

### 1. Get free API keys
- **Census**: https://api.census.gov/data/key_signup.html (instant)
- **HUD**: https://www.huduser.gov/portal/dataset/fmr-api.html (1-2 days)
- **FRED**: https://fred.stlouisfed.org/docs/api/api_key.html (instant)

### 2. Set environment variables
```bash
export CENSUS_API_KEY=your_key
export HUD_API_KEY=your_key
export FRED_API_KEY=your_key
```

### 3. Fetch fresh data
```bash
pip install requests
python fetch_data.py
# outputs city_data.json
```

### 4. Plug into frontend
In `index.html`, replace the `CITIES` array by fetching `city_data.json`:
```javascript
const res = await fetch('./city_data.json');
const { metros } = await res.json();
// map metros to CITIES format
```

## Features
- **30 metros** with rent, income, cost burden, YoY rent change
- **City detail panel** — rent vs income trend chart (2017–2023), contextual insight
- **Filters** — Critical / Stressed / Affordable
- **Sort** — by cost burden, rent, income, or city name
- **Comparison bar chart** — switchable between cost burden %, rent, income
- **What constitutes "burdened"**: HUD defines 30%+ of income on housing = cost-burdened; 50%+ = severely burdened

## Disclaimer
- "Rent figures represent Census ACS median gross rent across the full metro statistical area, which includes suburban and lower-cost areas. City core rents are typically higher."


## Data Sources
| Source | Dataset | URL |
|--------|---------|-----|
| Census Bureau | ACS 1-Year, B25064 + B19013 | api.census.gov |
| HUD | Fair Market Rents FY2024 | huduser.gov |
| FRED | CPI Shelter Index CUSR0000SEHA | fred.stlouisfed.org |
