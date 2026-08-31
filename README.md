# Soybean Yield and Climate Variability in Illinois, 1980-2025

County-level panel analysis of the association between climate variability and
soybean yield across 102 Illinois counties, with **Champaign County (FIPS 17019)**
as the focal unit.

Structural analogue of a Brazil state-level IBGE + ERA5 design:

| Brazil design | This pipeline |
|---|---|
| IBGE production, state x year, 1974-2023 | USDA NASS Quick Stats, county x year, 1980-2025 |
| 27 states | 102 counties (91 in balanced panel) |
| ERA5 reanalysis, gridded t2m + tp | NOAA NCEI nClimDiv, county monthly |
| State boundaries | Census county FIPS + NASS Ag Districts |
| State + year fixed effects | County + year fixed effects |
| State climate-sensitivity ranking | County climate-sensitivity ranking |
| production_tonnes | **yield_anom** (detrended yield) - see note below |

**Target choice.** Production confounds area expansion, which the Brazil spec
itself lists as a confounder. This pipeline targets the county-detrended yield
anomaly, isolating the climate signal. `production_tonnes` and `yield_kg_ha` are
carried in the final dataset for international comparability.

---

## Quick start

```bash
pip install pandas numpy matplotlib scikit-learn statsmodels
cd scripts
python 01_download_production.py     # provenance + staging check
python 02_clean_production.py        # -> data/processed/production_clean.csv
python 03_download_climate.py        # provenance + staging check
python 04_process_climate.py         # -> data/processed/climate_features.csv
python 05_merge_data.py              # -> data/final/soybean_illinois_climate_1980_2025.csv
python 06_eda.py                     # figures 1-9,  tables 1-3
python 07_statistical_models.py      # table 4, 4b
python 08_machine_learning.py        # figures 10-12, tables 5-6
python 09_sensitivity_analysis.py    # figures 13-16, tables 7, 8a, 8b
python 10_generate_results.py        # figures 17-18, manifest, column profile
python 11_robustness.py              # table 9
```

Runtime is a few minutes end to end. Random seed is fixed at 42 in `00_config.py`.

---

## Project structure

```
soybean_climate_illinois/
|
+-- data/
|   +-- raw/          nass_il_soybeans_county_raw.csv, nclimdiv_*.csv,
|   |                 nass_il_state_totals.csv, il_county_boundaries.txt
|   +-- processed/    production_clean.csv, climate_features.csv
|   +-- final/        soybean_illinois_climate_1980_2025.csv   <- ANALYTICAL PANEL
|
+-- scripts/          00_config.py, _cfg.py, _viz.py, 01..11
+-- figures/          fig01 .. fig18 (PNG, 200 dpi)
+-- models/           m4_twoway_fe.pkl, best_model.pkl
+-- results/          FINAL_REPORT.md, DATA_DICTIONARY.md,
|                     table1..table9 (CSV), *.json provenance and manifests
+-- README.md
```

---

## Methodology summary

**Growing season.** April-September (planting through maturity).
**Critical window.** July-August (R3-R6, pod set and seed fill). Agronomic, fixed
before modelling. Empirically supported: Jul/Aug precipitation correlate 0.32/0.34
with the anomaly, June 0.08, September 0.02.

**Target.**
```
yield_anom = yield_bu_ac - (a_county + b_county * year)
```
County-specific because county trends span 0.290 to 0.846 bu/acre/yr.

**Inclusion rule.** Counties with >= 42 of 46 years. 91 counties, 4,051 rows.
Fixed before modelling, not tuned on results.

**Panel.** Standard errors clustered on county throughout. Seven specifications
escalating to two-way (county + year) fixed effects.

**Leakage control.** No random splits anywhere.
- Fixed split: train 1980-2013, validate 2014-2018, test 2019-2025
- Expanding window: rolling origin, one test year at a time, 2001-2025
Random splits fail twice over here: temporally they admit future information,
and spatially, counties within a year share weather, so a random split puts
near-duplicates of test rows into training.

**Key comparison.** Not algorithm versus algorithm, but **trend-only baseline
versus climate models**. That contrast tests whether climate has predictive
content at all.

---

## Headline results

| Result | Value |
|---|---|
| Two-way FE R-squared | 0.668 |
| dYield/dTemperature at means | -0.664 bu/acre per °F |
| dYield/dTemperature, dry (P10) | -0.887 |
| dYield/dTemperature, wet (P90) | -0.429 |
| Jul-Aug precipitation optimum | 12.46 inches |
| Best single climate variable | Palmer Z-index Jul-Aug, r = 0.490 |
| ML skill vs trend-only baseline | +15.7% RMSE (expanding window) |
| Gradient boosting vs Ridge | +4.9% RMSE only |
| County sensitivity range | 0.47 (Mercer) to 3.60 (Clay) bu/acre per SD |
| Champaign sensitivity | 1.740, 42nd percentile |
| Scenario +1C and -10% precip | -0.73 bu/acre (-1.62%), 91 of 91 counties down |
| Robustness | temperature negative and p<0.05 in 13 of 13 specs |

---

## Validation performed

| Check | Result |
|---|---|
| Panel sums to published state totals, 46 years, 3 measures | Exact, 0.000% error |
| production_bu / acres_harvested == yield_bu_ac | 4,459 of 4,459, max residual 0.25 |
| acres_harvested <= acres_planted | 0 violations |
| Duplicate county-year keys | 0 |
| Climate join completeness | 4,459 of 4,459, zero nulls |
| Independent cross-check vs external saved NASS query (Champaign 2003-2023) | 21 of 21 match |

---

## Four traps this pipeline handles explicitly

1. **`OTHER (COMBINED) COUNTIES` is published per Ag District, not per state.**
   Raw key is `county_ansi + ag_district_code + year`. Keying on county+year alone
   silently collapses up to nine rows per year.
2. **Read `county_ansi` as text.** Integer casting turns `001` into `1` and drops
   Adams County from every join.
3. **Join on FIPS, never on name.** NASS writes `DU PAGE`, `ST CLAIR`,
   `JO DAVIESS`; Census writes `DuPage`, `St. Clair`, `Jo Daviess`.
4. **Never sum county rows to a state total after 2018.** Coverage fell from 102
   counties to 62; 2025 county sums give 6.30M planted acres against an actual
   10.30M. Use `data/raw/nass_il_state_totals.csv`.

---

## Known limitations

Full treatment in `results/FINAL_REPORT.md` section 6. The three that bind hardest:

- **Monthly resolution cannot resolve frost or daily extremes.** Coldest monthly
  mean minimum on record is 32.3 °F in October. No degree-days, dry-spell length,
  or rainfall intensity. Upgrade path: **gridMET 4 km daily**, which also carries
  vapour pressure deficit natively.
- **County coverage collapses after 2018**, and survival is not random, so the
  recent panel is selected toward large producers exactly where validation happens.
- **No causal identification.** Fixed effects absorb time-invariant county traits
  and statewide annual shocks, not county-specific time-varying confounders.

---

## Scenario disclaimer

The six perturbation experiments in `09_sensitivity_analysis.py` are **sensitivity
experiments, not climate projections**. They apply uniform shifts to observed
climate, use no CMIP6 or IPCC pattern, carry no probability information, and assume
no agronomic adaptation, cultivar change, or planting-date shift.

---

## Provenance

| Source | Access | Retrieved |
|---|---|---|
| USDA NASS Quick Stats | Query-tool CSV export, no API key | 2026-08-31 |
| NOAA NCEI nClimDiv | `ncei.noaa.gov/pub/data/cirs/climdiv/`, `*cy-v1.0.0-20260806` | 2026-08-31 |
| County boundaries | Public county GeoJSON, FIPS-keyed | 2026-08-31 |

Re-run recipes are printed by `01_download_production.py` and
`03_download_climate.py` and stored in `results/01_provenance_production.json`
and `results/03_provenance_climate.json`.

Note: the NASS Quick Stats API requires its own key, issued separately from
api.data.gov. An api.data.gov key (which works for FoodData Central) returns
HTTP 401 against Quick Stats. This pipeline avoids the issue by using the
public query-tool export.
