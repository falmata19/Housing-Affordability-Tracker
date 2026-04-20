"""
fetch_data.py
-------------
Fetches real housing affordability data from public APIs:
  - Census ACS: median rent + median household income by metro
  - HUD: Fair Market Rents by metro area
  - FRED (St. Louis Fed): national housing cost index

Get free API keys:
  - Census: https://api.census.gov/data/key_signup.html
  - HUD:    https://www.huduser.gov/portal/dataset/fmr-api.html
  - FRED:   https://fred.stlouisfed.org/docs/api/api_key.html

Run: python fetch_data.py
Outputs: city_data.json (plug into index.html or serve via FastAPI)
"""

import os, json, requests
from typing import Optional

CENSUS_KEY = os.getenv("CENSUS_API_KEY", "YOUR_CENSUS_KEY")
HUD_KEY    = os.getenv("HUD_API_KEY",    "YOUR_HUD_KEY")
FRED_KEY   = os.getenv("FRED_API_KEY",   "YOUR_FRED_KEY")

# ---------------------------------------------------------------------------
# Census ACS 1-Year: median gross rent + median household income by metro
# Variables: B25064_001E = median gross rent, B19013_001E = median HH income
# ---------------------------------------------------------------------------
def fetch_census_metros() -> list[dict]:
    url = "https://api.census.gov/data/2022/acs/acs1"
    params = {
        "get": "NAME,B25064_001E,B19013_001E",
        "for": "metropolitan statistical area/micropolitan statistical area:*",
        "key": CENSUS_KEY,
    }
    r = requests.get(url, params=params, timeout=30)
    r.raise_for_status()
    rows = r.json()
    headers = rows[0]
    results = []
    for row in rows[1:]:
        d = dict(zip(headers, row))
        rent   = int(d.get("B25064_001E") or 0)
        income = int(d.get("B19013_001E") or 0)
        if rent > 0 and income > 0:
            results.append({
                "name":   d["NAME"].split(",")[0].strip(),
                "rent":   rent,
                "income": income,
                "burden_pct": round(rent * 12 / income * 100, 1),
            })
    return sorted(results, key=lambda x: -x["burden_pct"])


# ---------------------------------------------------------------------------
# HUD Fair Market Rents (FY2024) — 2-bedroom FMR by metro
# ---------------------------------------------------------------------------
def fetch_hud_fmr(metro_code: str = "METRO41740M41740") -> Optional[dict]:
    url = f"https://www.huduser.gov/hudapi/public/fmr/data/{metro_code}"
    headers = {"Authorization": f"Bearer {HUD_KEY}"}
    r = requests.get(url, headers=headers, timeout=15)
    if r.status_code != 200:
        return None
    data = r.json()
    return {
        "fmr_1br": data.get("basicdata", {}).get("One-Bedroom"),
        "fmr_2br": data.get("basicdata", {}).get("Two-Bedroom"),
        "fmr_3br": data.get("basicdata", {}).get("Three-Bedroom"),
    }


# ---------------------------------------------------------------------------
# FRED: National median asking rent index (FRED series MSPUS)
# ---------------------------------------------------------------------------
def fetch_fred_series(series_id: str = "CUSR0000SEHA") -> list[dict]:
    """CUSR0000SEHA = CPI for Shelter (rental equivalent index)"""
    url = "https://api.stlouisfed.org/fred/series/observations"
    params = {
        "series_id": series_id,
        "api_key": FRED_KEY,
        "file_type": "json",
        "observation_start": "2017-01-01",
        "frequency": "a",  # annual
    }
    r = requests.get(url, params=params, timeout=15)
    r.raise_for_status()
    obs = r.json().get("observations", [])
    return [{"year": int(o["date"][:4]), "value": float(o["value"])} for o in obs if o["value"] != "."]


# ---------------------------------------------------------------------------
# Main: fetch, combine, save
# ---------------------------------------------------------------------------
def main():
    print("Fetching Census ACS metro data...")
    metros = fetch_census_metros()
    print(f"  Got {len(metros)} metros")

    print("Fetching FRED shelter CPI...")
    fred = fetch_fred_series()
    print(f"  Got {len(fred)} annual observations")

    output = {
        "metros": metros[:50],          # top 50 by cost burden
        "national_shelter_index": fred,
        "sources": {
            "census": "ACS 1-Year 2022 — B25064 (Median Gross Rent), B19013 (Median HH Income)",
            "hud": "HUD Fair Market Rents FY2024",
            "fred": "BLS CPI Shelter Index (CUSR0000SEHA)",
        }
    }

    with open("city_data.json", "w") as f:
        json.dump(output, f, indent=2)
    print("\nSaved city_data.json")
    print(f"Top 5 most burdened metros:")
    for m in metros[:5]:
        print(f"  {m['name']}: {m['burden_pct']}% burden (rent ${m['rent']}/mo, income ${m['income']:,}/yr)")


if __name__ == "__main__":
    main()
