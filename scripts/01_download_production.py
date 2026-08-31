"""01 - Acquire USDA NASS county soybean production (IBGE analogue).

The Quick Stats API requires a key. This pipeline uses the public query-tool
CSV export instead, which requires none. Raw export is staged in data/raw/.
Re-run instructions are printed for reproducibility.
"""
import sys, json, pandas as pd
sys.path.insert(0, str(__import__("pathlib").Path(__file__).parent))
from _cfg import RAW, RES, PROVENANCE

SRC = RAW/"nass_il_soybeans_county_raw.csv"

RECIPE = """
Reproduce this export:
  1. https://quickstats.nass.usda.gov/
  2. Program        = SURVEY
     Sector         = CROPS
     Commodity      = SOYBEANS
     Data Item      = ACRES PLANTED / ACRES HARVESTED /
                      PRODUCTION MEASURED IN BU / YIELD MEASURED IN BU / ACRE
     Geographic Lvl = COUNTY
     State          = ILLINOIS
     Year           = 1980-2025
  3. Get Data -> Spreadsheet
Programmatic equivalent (needs a Quick Stats key, separate from api.data.gov):
  GET /api/api_GET/?key=KEY&source_desc=SURVEY&commodity_desc=SOYBEANS
      &agg_level_desc=COUNTY&state_name=ILLINOIS&year__GE=1980&format=CSV
NOTE: the 50,000-row API cap binds for multi-state pulls; use the bulk file
      https://www.nass.usda.gov/datasets/qs.crops_<YYYYMMDD>.txt.gz instead.
"""

def main():
    if not SRC.exists():
        raise SystemExit(f"Missing raw export: {SRC}\n{RECIPE}")
    d = pd.read_csv(SRC, dtype=str)
    print(f"[01] raw production rows : {len(d):,}")
    print(f"[01] columns             : {list(d.columns)}")
    (RES/"01_provenance_production.json").write_text(
        json.dumps({**PROVENANCE['production'], "rows": len(d), "recipe": RECIPE.strip()}, indent=2))
    print(f"[01] provenance written  : results/01_provenance_production.json")

if __name__ == "__main__":
    main()
