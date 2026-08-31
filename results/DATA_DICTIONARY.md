# Data Dictionary

`data/final/soybean_illinois_climate_1980_2025.csv`

**90 columns, 4,459 rows, 102 counties, 1980-2025, zero nulls.**

Read `county_ansi`, `ag_district_code`, `state_ansi` and `fips5` as **text**. Integer casting turns `001` into `1`.

## Identity

| Column | Type | Unit | Range | Distinct |
|---|---|---|---|---|
| `state` | text |  |  | 1 |
| `state_ansi` | number |  | 17.0 to 17.0 | 1 |
| `county` | text |  |  | 102 |
| `county_ansi` | text |  |  | 102 |
| `fips5` | text |  |  | 102 |
| `ag_district` | text |  |  | 9 |
| `ag_district_code` | number |  | 10.0 to 90.0 | 9 |
| `year` | number |  | 1980.0 to 2025.0 | 46 |
| `is_focal` | number |  | 0.0 to 1.0 | 2 |
| `n_years_county` | number |  | 28.0 to 46.0 | 12 |
| `in_balanced_panel` | number |  | 0.0 to 1.0 | 2 |
| `produced_soy` | number |  | 1.0 to 1.0 | 1 |

## Production

| Column | Type | Unit | Range | Distinct |
|---|---|---|---|---|
| `acres_planted` | number | acres | 1100.0 to 329000.0 | 1234 |
| `acres_harvested` | number | acres | 800.0 to 328400.0 | 1671 |
| `production_bu` | number | bushels | 17700.0 to 22634000.0 | 4177 |
| `yield_bu_ac` | number | bu/acre | 13.0 to 80.4 | 439 |
| `yield_kg_ha` | number | kg/ha | 874.263 to 5406.978 | 439 |
| `production_tonnes` | number | tonnes | 481.714 to 615995.627 | 4177 |
| `area_harvested_ha` | number | hectares | 323.749 to 132898.765 | 1671 |

## Target

| Column | Type | Unit | Range | Distinct |
|---|---|---|---|---|
| `yield_anom` | number | bu/acre | -24.147 to 18.1 | 4459 |
| `yield_trend` | number | bu/acre | 21.158 to 73.764 | 4459 |
| `trend_slope` | number | bu/acre/yr | 0.29 to 0.846 | 102 |
| `log_yield` | number | log(bu/acre) | 2.565 to 4.387 | 439 |

## Climate: monthly raw

| Column | Type | Unit | Range | Distinct |
|---|---|---|---|---|
| `pcp04` | number | inches | 0.66 to 16.93 | 839 |
| `pcp05` | number | inches | 0.36 to 15.0 | 958 |
| `pcp06` | number | inches | 0.2 to 13.34 | 963 |
| `pcp07` | number | inches | 0.3 to 13.44 | 904 |
| `pcp08` | number | inches | 0.03 to 13.22 | 820 |
| `pcp09` | number | inches | 0.02 to 12.49 | 863 |
| `tmp04` | number | deg F | 38.7 to 63.2 | 224 |
| `tmp05` | number | deg F | 52.1 to 74.1 | 205 |
| `tmp06` | number | deg F | 61.5 to 80.5 | 161 |
| `tmp07` | number | deg F | 66.2 to 85.3 | 180 |
| `tmp08` | number | deg F | 64.6 to 83.4 | 180 |
| `tmp09` | number | deg F | 57.0 to 76.5 | 175 |
| `tmin04` | number | deg F | 27.5 to 51.9 | 220 |
| `tmin05` | number | deg F | 41.0 to 63.4 | 210 |
| `tmin09` | number | deg F | 46.4 to 65.6 | 174 |
| `tmax07` | number | deg F | 75.7 to 97.9 | 209 |
| `tmax08` | number | deg F | 75.5 to 96.3 | 200 |
| `tmax_jja` | number | deg F | 75.67 to 92.67 | 432 |
| `pdsi06` | number | index | -4.89 to 7.09 | 932 |
| `pdsi07` | number | index | -5.42 to 8.0 | 970 |
| `pdsi08` | number | index | -5.67 to 8.41 | 991 |
| `zndx07` | number | index | -5.4 to 10.47 | 992 |
| `zndx08` | number | index | -4.04 to 9.51 | 928 |
| `pcp08_anom` | number | inches | -3.73 to 9.029 | 4176 |
| `pcp08_z` | number | inches | -2.072 to 4.2 | 4290 |
| `tmax08_anom` | number | deg F | -5.883 to 9.111 | 2986 |
| `tmax08_z` | number | deg F | -2.146 to 3.108 | 3666 |
| `pdsi08_anom` | number | index | -6.236 to 7.695 | 4226 |
| `pdsi08_z` | number | index | -2.775 to 2.804 | 4361 |
| `zndx08_anom` | number | index | -4.696 to 9.031 | 4128 |
| `zndx08_z` | number | index | -2.183 to 4.016 | 4331 |

## Climate: engineered

| Column | Type | Unit | Range | Distinct |
|---|---|---|---|---|
| `pcp_win` | number | inches | 1.85 to 22.83 | 1228 |
| `pcp_prevND` | number | inches | 0.92 to 18.21 | 1156 |
| `tmin10` | number | deg F | 32.3 to 54.6 | 209 |
| `pdsi_jja` | number | index | -5.05 to 7.58 | 927 |
| `zndx_jja` | number | index | -4.37 to 6.16 | 742 |
| `pdsi_may` | number | index | -5.16 to 6.87 | 892 |
| `pcp_grow` | number | inches | 8.25 to 44.29 | 2258 |
| `pcp_critical` | number | inches | 1.39 to 19.83 | 1398 |
| `pcp_summer` | number | inches | 3.09 to 29.29 | 1748 |
| `tmp_grow` | number | deg F | 59.683 to 74.133 | 1169 |
| `tmp_critical` | number | deg F | 66.1 to 82.15 | 392 |
| `tmp_summer` | number | deg F | 65.667 to 80.967 | 646 |
| `tmax_critical` | number | deg F | 76.1 to 95.05 | 438 |
| `tmax_summer` | number | deg F | 75.67 to 92.67 | 432 |
| `tmp_range_crit` | number | deg F | 28.45 to 46.8 | 977 |
| `pcp_grow_cv` | number | inches | 0.075 to 1.216 | 4459 |
| `tmp_grow_sd` | number | deg F | 5.565 to 13.634 | 4405 |
| `pdsi_critical` | number | index | -5.39 to 7.83 | 1877 |
| `zndx_critical` | number | index | -4.125 to 6.715 | 1764 |
| `drought_flag` | number |  | 0.0 to 1.0 | 2 |
| `severe_drought` | number |  | 0.0 to 1.0 | 2 |
| `hot_month_count` | number | count of months | 0.0 to 2.0 | 3 |
| `dry_month_count` | number | count of months | 0.0 to 2.0 | 3 |
| `heat_x_dry` | number | index | -792.183 to 380.568 | 4374 |
| `pcp_grow_anom` | number | inches | -14.985 to 19.287 | 4379 |
| `pcp_grow_z` | number | inches | -2.97 to 3.342 | 4427 |
| `pcp_critical_anom` | number | inches | -6.069 to 12.454 | 4323 |
| `pcp_critical_z` | number | inches | -2.225 to 4.014 | 4399 |
| `tmp_grow_anom` | number | deg F | -3.785 to 3.226 | 3997 |
| `tmp_grow_z` | number | deg F | -2.712 to 2.353 | 4239 |
| `tmp_critical_anom` | number | deg F | -5.48 to 5.922 | 3443 |
| `tmp_critical_z` | number | deg F | -2.589 to 2.74 | 3976 |
| `tmax_critical_anom` | number | deg F | -6.299 to 7.77 | 3577 |
| `tmax_critical_z` | number | deg F | -2.505 to 2.917 | 3999 |
| `climate_normal_pcp` | number |  | 7.124 to 8.869 | 102 |
| `climate_normal_tmax` | number |  | 81.79 to 88.767 | 102 |

## Key definitions

- **`yield_anom`** - the modelling target. Residual from a county-specific linear trend of `yield_bu_ac` on `year`. Removes the ~0.65 bu/acre/yr technology trend.
- **`zndx*` (Palmer Z-index)** - short-memory monthly moisture departure. Outperforms both raw precipitation and PDSI as a yield predictor.
- **`pdsi*` (Palmer Drought Severity Index)** - long-memory drought index. NOAA classes: <= -4 extreme, -3 severe, -2 moderate, -1 mild, +/-1 near normal.
- **`heat_x_dry`** - engineered interaction, `tmax_critical * (-zndx08)`. Ranks fifth in permutation importance on its own.
- **`*_anom`** - departure from that county's own 1980-2025 mean.
- **`*_z`** - the same departure divided by that county's own standard deviation.
- **`in_balanced_panel`** - 1 if the county has >= 42 of 46 years. Inclusion rule fixed before modelling.
- **`is_focal`** - 1 for Champaign County (FIPS 17019).

## Companion files

| File | Contents |
|---|---|
| `data/raw/nass_il_state_totals.csv` | Illinois state totals. **Use for any state-level series.** County sums are invalid after 2018. |
| `results/table7_county_climate_sensitivity.csv` | County dimension table: identity, coverage, trend, volatility, sensitivity |
| `results/column_profile_final.csv` | Auto-generated profile of all 90 columns |
| `data/raw/il_county_boundaries.txt` | Simplified county polygons, `fips5|lon,lat lon,lat ...` |
