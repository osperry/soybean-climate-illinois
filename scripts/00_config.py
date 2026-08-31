"""Shared configuration and provenance constants."""
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
RAW, PROC, FINAL = ROOT/"data/raw", ROOT/"data/processed", ROOT/"data/final"
FIG, RES, MOD = ROOT/"figures", ROOT/"results", ROOT/"models"
for d in (RAW,PROC,FINAL,FIG,RES,MOD): d.mkdir(parents=True,exist_ok=True)

SEED = 42
FOCAL_COUNTY, FOCAL_FIPS = "CHAMPAIGN", "17019"

# ---- Growing season (agronomic justification, see README §Methodology) -------
# Illinois soybeans: planted early-to-mid May, emergence late May, vegetative
# June, flowering (R1-R2) late June-July, pod set (R3-R4) late July, seed fill
# (R5-R6) August, maturity (R7-R8) September, harvest October.
# Yield is set primarily during R3-R6, i.e. late July through August.
GROW_MONTHS    = [4,5,6,7,8,9]      # April-September, planting through maturity
CRITICAL_MONTHS= [7,8]              # July-August, pod set and seed fill
SUMMER_MONTHS  = [6,7,8]            # meteorological summer

# ---- Provenance -------------------------------------------------------------
PROVENANCE = {
 "production": dict(
   source="USDA NASS Quick Stats",
   url="https://quickstats.nass.usda.gov/",
   accessed="2026-08-31",
   params="source_desc=SURVEY; sector_desc=CROPS; commodity_desc=SOYBEANS; "
          "agg_level_desc=COUNTY; state_name=ILLINOIS; domain_desc=TOTAL; "
          "period=YEAR; year=1980..2025",
   note="Query-tool CSV export. No API key. Period filtered to YEAR to exclude "
        "in-season forecasts and acreage revisions."),
 "climate": dict(
   source="NOAA NCEI nClimDiv, county-level monthly",
   url="https://www.ncei.noaa.gov/pub/data/cirs/climdiv/",
   accessed="2026-08-31",
   files=["climdiv-pcpncy-v1.0.0-20260806","climdiv-tmpccy-v1.0.0-20260806",
          "climdiv-tmaxcy-v1.0.0-20260806","climdiv-tmincy-v1.0.0-20260806",
          "climdiv-pdsicy-v1.0.0-20260806","climdiv-zndxcy-v1.0.0-20260806"],
   spatial_resolution="county polygon (pre-aggregated by NCEI from station network)",
   temporal_resolution="monthly",
   units="precipitation inches; temperature degrees Fahrenheit; Palmer indices dimensionless",
   note="ERA5 analogue. NCEI performs the gridding and polygon aggregation "
        "upstream, so no area-weighting step is executed in this pipeline. "
        "See README Limitations."),
 "geography": dict(
   source="USDA NASS county ANSI (FIPS) codes and Agricultural Statistics Districts",
   note="fips5 = '17' + county_ansi. Joins to Census TIGER."),
}
