"""03 - Acquire NOAA nClimDiv county monthly climate (ERA5 analogue).

nClimDiv fixed-width layout:
  cols 1-2  NCDC state code (Illinois = 11, NOT FIPS 17)
  cols 3-5  county FIPS (3 digit)
  cols 6-7  element code
  cols 8-11 year
  then 12 x 7-char monthly values, missing sentinel -9.99 / -99.90
"""
import sys, json, pandas as pd
sys.path.insert(0, str(__import__("pathlib").Path(__file__).parent))
from _cfg import RAW, RES, PROVENANCE

LAYOUT = dict(state_code="cols 1-2 (Illinois=11)", county_fips="cols 3-5",
              element="cols 6-7", year="cols 8-11",
              months="12 fields of width 7", missing="values <= -99 treated as null")
RECIPE = """
Reproduce:
  base=https://www.ncei.noaa.gov/pub/data/cirs/climdiv/
  for f in climdiv-pcpncy climdiv-tmpccy climdiv-tmaxcy climdiv-tmincy \\
           climdiv-pdsicy climdiv-zndxcy ; do
      curl -O ${base}${f}-v1.0.0-20260806
  done
Filter lines beginning '11' for Illinois. Version suffix changes monthly;
list the directory to get the current one.
"""
def main():
    files = [RAW/"nclimdiv_pcp_tmp_county.csv", RAW/"nclimdiv_drought_temp_extra.csv"]
    for f in files:
        if not f.exists(): raise SystemExit(f"Missing {f}\n{RECIPE}")
        print(f"[03] staged: {f.name}  rows={len(pd.read_csv(f)):,}")
    (RES/"03_provenance_climate.json").write_text(json.dumps(
        {**PROVENANCE['climate'], "fixed_width_layout": LAYOUT, "recipe": RECIPE.strip()}, indent=2))
    print("[03] provenance written : results/03_provenance_climate.json")
if __name__ == "__main__": main()
