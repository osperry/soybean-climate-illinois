# Soybean Yield and Climate Variability in Illinois, 1980 to 2025

### A county-level panel analysis with Champaign County as the focal unit

Version 1.0 | 2026-08-31 | Data: USDA NASS Quick Stats, NOAA NCEI nClimDiv

---

## Abstract

**Objective.** Quantify how historical climate variability has been associated with soybean yield across Illinois counties, and test whether climate information improves out-of-sample prediction relative to a technology-trend baseline. Champaign County is examined as the focal unit within the state panel.

**Data.** A balanced county by year panel of 4,459 observations covering 102 Illinois counties from 1980 to 2025. Production comes from USDA NASS Quick Stats (SURVEY program, county level, Period = YEAR). Climate comes from NOAA NCEI nClimDiv county monthly precipitation, mean, maximum and minimum temperature, Palmer Drought Severity Index and Palmer Z-index. The analytical target is the detrended yield anomaly, the residual from a county-specific linear yield trend.

**Methods.** Exploratory analysis, panel regression escalating to two-way fixed effects with county-clustered standard errors, five machine-learning models under strict temporal validation (fixed 1980-2013 / 2014-2018 / 2019-2025 split and expanding-window rolling origin), permutation importance, county-level sensitivity estimation, six climate perturbation experiments, and thirteen robustness specifications.

**Main findings.** Detrending is decisive: correlations between climate and yield roughly double once the county-specific technology trend is removed. The strongest single predictor is the July-August Palmer Z-index (r = 0.490 against the anomaly, 0.311 against raw yield). The two-way fixed-effects model explains 66.8% of anomaly variance. The estimated marginal effect of temperature at sample means is **-0.66 bu/acre per °F**, and it is conditional on moisture: **-0.89 bu/acre per °F in dry conditions versus -0.43 in wet**. Precipitation response is nonlinear with an interior optimum near 12.5 inches over July-August. Machine learning beats a trend-only baseline by **15.7%** in RMSE under expanding-window validation, confirming that climate carries genuine predictive content, though gradient boosting improves on penalised linear regression by only about 5%. County sensitivity varies more than tenfold, from 0.47 bu/acre per standard deviation of moisture in Mercer County to 3.60 in Clay County. Champaign sits near the middle at 1.74, the 42nd percentile. Under a +1 °C and -10% precipitation experiment, mean simulated yield falls 0.73 bu/acre (1.6%), all 91 panel counties decline, and losses concentrate in the southwest. The temperature effect is negative and significant at 5% in all thirteen robustness specifications.

**Implications.** Climate variability is robustly and negatively associated with Illinois soybean yield after controlling for county and year effects, with the damage concentrated in the July-August reproductive window and driven by a heat and moisture interaction rather than by heat alone. Vulnerability is highest where baseline yields are already lowest. These are associations, not causal estimates, and the perturbation experiments are sensitivity analyses, not climate projections.

---

## 1. Introduction

Illinois is consistently among the two largest soybean-producing states in the United States, harvesting roughly 10 million acres annually and producing 600 to 690 million bushels in recent years. Soybean is a rainfed crop across nearly the entire state, which makes yield unusually exposed to growing-season weather and makes Illinois a useful natural laboratory for climate-yield relationships.

The central analytical difficulty is that observed yield is dominated by a technology trend. Illinois state yield rose from 33.5 bu/acre in 1980 to 62.5 in 2025, an increase of roughly 0.65 bu/acre per year driven by cultivar improvement, seed treatment, planting equipment, and agronomic practice. That trend is an order of magnitude larger than any plausible climate signal within the sample, and because temperature also trended over the same period, a model that fails to remove it will attribute technology gains to warming and can return a positive temperature coefficient. Recovering the climate signal therefore requires the trend to be removed first, at the county level, because county trends themselves range from 0.29 to 0.85 bu/acre per year.

### Research questions

1. How has historical climate variability been associated with soybean yield across Illinois counties from 1980 to 2025?
2. Which climate variables have the strongest relationship with yield?
3. Are temperature and precipitation effects linear or nonlinear?
4. Are some counties more climate-sensitive than others?
5. Are extreme and anomaly-based indicators more informative than seasonal averages?
6. Does machine learning improve prediction relative to conventional statistical models and to a trend-only baseline?
7. How does simulated yield respond to warmer and drier conditions?

---

## 2. Data

### 2.1 Production

| Attribute | Value |
|---|---|
| Source | USDA NASS Quick Stats |
| Program | `source_desc = SURVEY`, `Period = YEAR` |
| Geography | `agg_level_desc = COUNTY`, Illinois |
| Domain | `domain_desc = TOTAL` (the only value available at county level) |
| Coverage | 1980 to 2025, 46 years |
| Variables | acres planted, acres harvested, production (bu), yield (bu/acre) |
| Access | Query-tool CSV export, no API key |

Only four variables exist at county level. Value of production and the irrigated versus non-irrigated splits are published at state level and above only.

**A key structural detail.** NASS reports counties suppressed for disclosure in an `OTHER (COMBINED) COUNTIES` bucket, and it publishes **one such bucket per Agricultural Statistics District, not one per state**. In 2019 there are nine, all carrying a blank county ANSI code. The primary key on the raw export is therefore `county_ansi + ag_district_code + year`. Keying on county and year alone silently collapses those rows. The cleaning script asserts uniqueness and drops the 48 aggregate rows.

### 2.2 Climate

| Attribute | Value |
|---|---|
| Source | NOAA NCEI nClimDiv, county-level monthly |
| Files | `climdiv-{pcpn,tmpc,tmax,tmin,pdsi,zndx}cy-v1.0.0-20260806` |
| Layout | Fixed width: state code (cols 1-2, Illinois = 11), county FIPS (3-5), element (6-7), year (8-11), then twelve 7-character monthly values |
| Units | Precipitation inches, temperature °F, Palmer indices dimensionless |
| Coverage | 1980 to 2025, all 102 Illinois counties |

nClimDiv is the ERA5 analogue in this design: an operational reanalysis-style product providing consistent long-record gridded-to-polygon climate. One structural difference matters and is stated plainly here and again in Limitations. **NCEI performs the gridding and polygon aggregation upstream**, so this pipeline executes no area-weighting step of its own. That removes a source of analyst error but also removes a documented methodological choice, and it fixes the temporal resolution at monthly.

County values are genuinely county-specific rather than climate-division clones. In 2012, 96 counties produced 82 distinct August precipitation values and 86 distinct August PDSI values, and within every Agricultural Statistics District the member counties differ. Temperature fields are smoother: the same 96 counties produced only 55 distinct August maximum-temperature values.

### 2.3 Geography

`fips5 = "17" + county_ansi`, joining to Census TIGER. County names in NASS do not match Census spelling (`DU PAGE`, `ST CLAIR`, `JO DAVIESS` against `DuPage`, `St. Clair`, `Jo Daviess`), so all joins use FIPS. County boundary geometry for the choropleth was taken from a public county GeoJSON keyed on the same FIPS codes.

### 2.4 Data quality report

| Check | Result |
|---|---|
| Raw production rows | 4,507 |
| Aggregate (non-county) rows dropped | 48 |
| Duplicate county-year keys after cleaning | 0 |
| Sentinel or unparsed cells | 0 |
| Identity `production_bu / acres_harvested == yield_bu_ac` | 4,459 of 4,459, max residual 0.25 bu/acre |
| `acres_harvested <= acres_planted` violations | 0 |
| Zero-production rows (distinguished from missing) | 0 |
| Climate join completeness | 4,459 of 4,459, zero nulls |
| Panel county totals reconcile to published state totals | Exact, 0.000% error, all 46 years, three measures |

The final reconciliation check is the one that matters most. Internal consistency checks pass even on a file that has silently lost rows; only comparison against an independently published aggregate detects that failure mode.

---

## 3. Methodology

### 3.1 Growing season definition

Illinois soybeans are planted in early to mid May, emerge in late May, are vegetative through June, flower (R1-R2) from late June into July, set pods (R3-R4) in late July, fill seed (R5-R6) through August, mature (R7-R8) in September and are harvested in October.

Yield is determined principally during R3 through R6. The pipeline therefore defines:

- **Growing season**: April through September, planting through maturity
- **Critical window**: July and August, pod set and seed fill

This is an agronomic choice, not a statistical one, and it was fixed before any model was estimated. The empirical results support it: July and August precipitation correlate 0.32 and 0.34 with the yield anomaly while June correlates 0.08 and September 0.02.

### 3.2 Target variable

```
yield_anom = yield_bu_ac - (a_county + b_county * year)
```

fitted separately within each county by ordinary least squares. County trend slopes range from 0.290 (DuPage) to 0.846 (Piatt) bu/acre per year, so a single pooled detrend would be misspecified.

### 3.3 Feature engineering

Thirty-eight engineered features across five families: seasonal precipitation and temperature aggregates, within-season variability, Palmer drought indices, heat and dry stress proxies, and county-specific anomalies expressed both in natural units and as z-scores against each county's own 1980-2025 climatology. Anomaly standardisation matters because baseline yield spans 18 bu/acre across the state's north-south gradient.

### 3.4 Panel specification

The panel is repeated observations of counties over years, so observations are not independent. Standard errors are clustered on county throughout. Seven specifications were estimated, escalating from pooled OLS to two-way fixed effects, plus alternative targets in logs and raw levels.

### 3.5 Machine learning and leakage control

No random splits are used anywhere. Two validation regimes:

- **Fixed temporal split**: train 1980-2013 (3,089 rows), validate 2014-2018 (437), test 2019-2025 (525)
- **Expanding-window rolling origin**: for each year from 2001 to 2025, train on all prior years and predict that year (2,317 test observations in total)

Random splits are inadmissible here for two reasons. Temporally, they let future information into training. Spatially, counties within a year are strongly correlated through shared weather, so a random split places near-duplicates of test observations into the training set. Blocking on year addresses both.

The comparison of scientific interest is not between algorithms but between **a trend-only baseline** (predict the county trend, that is, anomaly = 0) and **models that use climate**. That contrast tests whether climate information has predictive content at all.

### 3.6 Scenarios

Six perturbation experiments apply uniform shifts to observed climate and re-predict with the fitted model. **These are sensitivity experiments, not climate projections.** They apply no CMIP6 or IPCC pattern, carry no probability information, and hold constant the agronomic adaptation, cultivar change, and planting-date shifts that would accompany any real climate change.

---

## 4. Results

### 4.1 Descriptive and exploratory

Illinois state yield rose from 33.5 bu/acre in 1980 to 62.5 in 2025. The detrended state anomaly has a standard deviation of about 4.2 bu/acre, so roughly 85% of raw yield variation is technology rather than weather.

The three worst years are 2012 (-9.6), 1988 (-8.7) and 2003 (-8.5). The three best are 2018 (+6.8), 2021 (+6.3) and 1985 (+6.1). The downside tail is deeper than the upside, which matters for how the response is specified.

Abandonment carries no signal in Illinois: the gap between acres planted and acres harvested has a median of 0.54% and a maximum of 3.23%. This is a useful null result and distinguishes Illinois from the Plains states.

### 4.2 Climate-yield correlations (Table 3)

Ranked by correlation with the detrended anomaly across all 4,459 county-years:

| Variable | r (detrended) | r (raw yield) | r (Champaign only) |
|---|---|---|---|
| Palmer Z-index, Jul-Aug | **0.490** | 0.311 | 0.453 |
| Jul-Aug precipitation (z-score) | 0.476 | 0.279 | 0.394 |
| August max temperature (anomaly) | **-0.469** | -0.286 | -0.426 |
| August Palmer Z-index (z-score) | 0.468 | 0.236 | 0.444 |
| Jul-Aug precipitation | 0.464 | 0.296 | 0.394 |
| Heat by dryness interaction | -0.463 | -0.265 | -0.448 |

Three findings.

**Detrending roughly doubles every correlation.** The Palmer Z-index moves from 0.311 against raw yield to 0.490 against the anomaly. Climate has no trend and yield does, so the trend acts as pure noise in the raw correlation.

**The Palmer Z-index outperforms raw precipitation.** Z-index is the current-month moisture departure accounting for antecedent soil water. PDSI, which has longer memory, performs worse (0.349 for August) because it carries drought signal from months that no longer affect the crop.

**Anomaly and z-score forms outperform natural units**, confirming that county-relative departures carry more information than absolute levels in a panel spanning a large climatic gradient.

### 4.3 Panel regression (Table 4)

| Specification | n | R² | Adj. R² | RMSE |
|---|---|---|---|---|
| M1 Baseline pooled OLS | 4,051 | 0.254 | 0.253 | 4.63 |
| M2 Quadratic + interaction | 4,051 | 0.361 | 0.360 | 4.28 |
| M3 M2 + county FE | 4,051 | 0.379 | 0.365 | 4.22 |
| **M4 Two-way FE (county + year)** | 4,051 | **0.668** | **0.656** | **3.09** |
| M5 Palmer Z specification | 4,051 | 0.353 | 0.337 | 4.31 |
| M6 Raw yield, two-way FE | 4,051 | 0.857 | 0.853 | 4.32 |
| M7 Log yield, county FE | 4,051 | 0.859 | 0.856 | 0.10 |

Adding the quadratic terms and the interaction lifts R² from 0.254 to 0.361, which is the single largest specification gain and establishes that the relationship is nonlinear. Year fixed effects add a further 0.29, confirming that a large share of yield variation is common statewide shocks.

**M4 climate coefficients, county-clustered standard errors:**

| Term | Coefficient | SE | p | 95% CI |
|---|---|---|---|---|
| Precipitation | -3.978 | 1.322 | 0.003 | [-6.570, -1.387] |
| Precipitation² | -0.0625 | 0.0070 | <0.001 | [-0.0761, -0.0488] |
| Max temperature | 8.770 | 1.390 | <0.001 | [6.045, 11.495] |
| Max temperature² | -0.0581 | 0.0076 | <0.001 | [-0.0729, -0.0433] |
| Precipitation × temperature | 0.0648 | 0.0145 | <0.001 | [0.0364, 0.0931] |

Because the model contains an interaction, individual coefficients are not directly interpretable. Evaluated at sample means (7.73 inches July-August precipitation, 85.5 °F July-August maximum temperature):

| Quantity | Estimate |
|---|---|
| Marginal effect of temperature | **-0.664 bu/acre per °F** |
| Marginal effect of precipitation | **+0.591 bu/acre per inch** |
| Precipitation optimum, at mean temperature | 12.46 inches |
| Temperature optimum, at mean precipitation | 79.78 °F |

**The interaction is the substantive result.** The temperature effect is conditional on moisture:

| Moisture condition | dYield/dTemperature |
|---|---|
| Dry (10th percentile, 4.3 in) | **-0.887 bu/acre per °F** |
| At the mean (7.7 in) | -0.664 |
| Wet (90th percentile, 11.4 in) | **-0.429** |

Warming costs roughly twice as much in dry conditions as in wet. An additive model would systematically understate warming risk. The same pattern appears non-parametrically: mean yield anomaly is +1.44 in cool and wet conditions, +1.45 in hot and wet, -1.17 in cool and dry, and -5.26 in hot and dry. Heat alone is nearly costless; heat with drought is not.

The precipitation response has an interior optimum near 12.5 inches and turns down beyond it. Binned means confirm the shape: the anomaly rises from -6.4 bu/acre in the driest decile to +2.1 at 16 inches, then falls to +1.7 in the wettest decile. The drought penalty is roughly three times the wet-year bonus.

Diagnostics: Breusch-Pagan rejects homoskedasticity for most specifications, which is why all standard errors are clustered. Durbin-Watson for M4 is 1.97, close to the null of no residual autocorrelation.

### 4.4 Machine learning (Table 5)

**Expanding-window rolling origin, 2001-2025, 2,317 test observations:**

| Model | RMSE | MAE | R² | Skill vs baseline |
|---|---|---|---|---|
| **Gradient Boosting** | **4.844** | 3.680 | **0.284** | **+15.7%** |
| HistGBM | 4.870 | 3.706 | 0.276 | +15.3% |
| Random Forest | 4.895 | 3.723 | 0.269 | +14.8% |
| Linear Regression | 5.090 | 3.892 | 0.209 | +11.5% |
| Ridge | 5.095 | 3.896 | 0.208 | +11.4% |
| Baseline: trend only | 5.748 | 4.424 | -0.008 | 0.0 |

**Fixed split, test 2019-2025:**

| Model | RMSE | MAE | R² |
|---|---|---|---|
| HistGBM | **3.925** | 3.166 | 0.122 |
| Gradient Boosting | 3.990 | 3.265 | 0.092 |
| Ridge | 4.124 | 3.337 | 0.030 |
| Random Forest | 4.137 | 3.399 | 0.024 |
| Baseline: trend only | 4.895 | 4.119 | **-0.366** |

Two conclusions, and the second is more important than the first.

**Climate information genuinely improves prediction.** Every climate model beats the trend-only baseline in both validation regimes, by 11 to 16% in RMSE. The baseline's negative out-of-sample R² confirms it carries no information about deviations from trend, which is what it should do by construction.

**The gain from algorithm sophistication is modest.** Gradient boosting beats ridge regression by 4.9% in RMSE. Most of the available signal is captured by a penalised linear model. The nonlinearity and interaction that matter are the ones already written into the parametric specification.

### 4.5 Feature importance (Table 6)

Permutation importance for gradient boosting, evaluated on held-out years 2019-2025:

| Feature | Importance | SD |
|---|---|---|
| Jul-Aug precipitation | **0.106** | 0.013 |
| Growing-season precipitation | 0.078 | 0.008 |
| August maximum temperature | 0.067 | 0.013 |
| Jul-Aug PDSI | 0.059 | 0.006 |
| Heat by dryness interaction | 0.052 | 0.011 |
| Within-season precipitation variability | 0.035 | 0.004 |
| Within-season temperature variability | 0.029 | 0.011 |
| Jul-Aug maximum temperature | 0.026 | 0.004 |

Moisture terms occupy four of the top five positions. The engineered heat-by-dryness interaction ranks fifth on its own, independent evidence for the interaction found parametrically. Within-season variability terms rank above several seasonal means, indicating that the distribution of weather within the season carries information beyond its total.

These are associational rankings from a predictive model and should not be read as causal effect sizes.

### 4.6 County climate sensitivity (Table 7)

Sensitivity was estimated county by county as the yield-anomaly response to a one-standard-deviation August moisture anomaly.

**Most sensitive:**

| County | District | r (moisture) | β (bu/acre per SD) |
|---|---|---|---|
| CLAY | East Southeast | 0.679 | **3.596** |
| RICHLAND | East Southeast | 0.687 | 3.223 |
| WAYNE | Southeast | **0.693** | 2.987 |
| EDWARDS | Southeast | 0.618 | 2.254 |
| FRANKLIN | Southeast | 0.604 | 2.162 |

**Least sensitive:**

| County | District | r (moisture) | β (bu/acre per SD) |
|---|---|---|---|
| MERCER | Northwest | 0.174 | **0.556** |
| KNOX | West | 0.186 | 0.468 |
| ROCK ISLAND | Northwest | 0.233 | 0.864 |
| BUREAU | Northwest | 0.230 | 1.002 |

**Sensitivity varies more than sevenfold in β and by a factor of four in correlation.** A pooled climate coefficient averages a county where August moisture explains 48% of anomaly variance with one where it explains 3%.

The pattern is geographic and systematic. Southern and southeastern counties on thinner, less water-retentive soils are far more exposed; northern and western counties on deep glacial soils buffer moisture deficits. Two cross-sectional relationships confirm this:

- `r(mean Aug max temperature, moisture sensitivity) = +0.606`. Structurally hotter counties respond more sharply to moisture.
- `r(recent yield level, moisture sensitivity) = -0.512`. **Higher-yielding counties are less climate-exposed.** Advantage compounds: the best ground both yields more and varies less.

### 4.7 Champaign County, the focal unit

| Metric | Champaign | State panel |
|---|---|---|
| Observations | 44 (1980-2023) | 4,459 |
| Mean yield 2015-2025 | 64.3 bu/acre | 58.7 |
| Technology trend | 0.660 bu/acre/yr | 0.627 mean |
| Moisture sensitivity β | +1.740 bu/acre per SD | 0.47 to 3.60 range |
| Sensitivity rank | 53rd of 91 (42nd percentile) | |
| r with Jul-Aug Palmer Z | 0.453 | 0.490 pooled |
| Simulated change under +1 °C, -10% precip | **-0.24 bu/acre (-0.47%)** | -0.73 (-1.62%) mean |

Champaign is a high-yielding, near-median-sensitivity county that is **less exposed than the state average** under the perturbation experiments. Its worst recorded year is 2003 at -13.99 bu/acre below trend, followed by 1988 at -12.25 and 2012 at -11.34.

**Champaign has no 2024 or 2025 observation.** It was suppressed under the recent collapse in NASS county coverage, described in Limitations.

### 4.8 Scenario results (Tables 8a, 8b)

Sensitivity experiments, not projections.

| Scenario | ΔT | ΔP | Mean Δyield | % of mean yield | P10 | P90 | Counties worse |
|---|---|---|---|---|---|---|---|
| S1 Baseline | 0 | 0 | 0.00 | 0.0% | 0.00 | 0.00 | 0 |
| S2 | +1 °C | 0 | -0.31 | -0.68% | -1.73 | +0.78 | 89 of 91 |
| S3 | 0 | -10% | -0.27 | -0.59% | -1.12 | +0.51 | 88 of 91 |
| **S4** | **+1 °C** | **-10%** | **-0.73** | **-1.62%** | -2.55 | +0.82 | **91 of 91** |
| S5 | +2 °C | 0 | -0.64 | -1.42% | -2.82 | +1.11 | 91 of 91 |
| S6 | +2 °C | -20% | **-2.03** | **-4.48%** | -4.98 | +0.62 | 91 of 91 |

**The combination exceeds the sum of its parts.** S2 alone costs 0.31 bu/acre and S3 alone costs 0.27, summing to 0.58, but S4 costs 0.73. The excess is the interaction, and it is the same mechanism identified in the regression and the feature importance.

Impacts are geographically heterogeneous. Under S4:

| Largest losses | Δ bu/acre | Δ % | | Smallest / positive | Δ bu/acre |
|---|---|---|---|---|---|
| JACKSON (SW) | -1.92 | -5.26% | | LAKE (NE) | +0.20 |
| GREENE (WSW) | -1.68 | -3.52% | | KANE (NE) | +0.19 |
| PULASKI (SW) | -1.62 | -4.31% | | VERMILION (E) | +0.09 |
| WASHINGTON (SW) | -1.53 | -4.17% | | EDGAR (ESE) | +0.07 |

Losses concentrate in the southwest, where baseline yields are already the lowest in the state. The few counties showing small positive responses are in the cool northeast, consistent with those locations sitting below the estimated temperature optimum.

### 4.9 Robustness (Table 9)

Thirteen specifications. The estimated marginal effect of temperature at means:

| Check | dY/dT | p (temperature) |
|---|---|---|
| Reference: balanced panel, two-way FE | -0.664 | <0.001 |
| All 102 counties, no balance rule | -0.625 | <0.001 |
| Fully balanced only (28 counties) | -0.552 | <0.001 |
| Trim 1% extreme yield years | -0.519 | <0.001 |
| Trim 2% extreme precipitation years | -0.629 | <0.001 |
| Drop 1988, 2003, 2012 | **-0.334** | <0.001 |
| Early period only (1980-2002) | -0.591 | 0.003 |
| Late period only (2003-2025) | **-0.838** | <0.001 |
| County FE only, no year FE | -0.404 | <0.001 |
| Alternative indicator: growing-season precipitation | -0.658 | <0.001 |
| Target: log yield | -0.019 | <0.001 |
| Target: raw yield | -0.698 | <0.001 |
| Target: yield growth (%) | -2.534 | <0.001 |

**The temperature effect is negative and significant at 5% in all thirteen specifications.** The magnitude is stable between -0.52 and -0.70 across most checks.

Two departures are informative rather than concerning. Dropping the three drought years halves the effect to -0.334, confirming that a substantial share of the estimated relationship is carried by extreme years, which is expected for a nonlinear damage function. And the late period (2003-2025) shows a larger effect (-0.838) than the early period (-0.591), consistent with either increased exposure or the changing county composition of the recent panel; the design cannot separate those.

---

## 5. Discussion

### 5.1 Mechanism

The results describe a coherent agronomic mechanism. Damage concentrates in July and August, the pod set and seed fill window, and is essentially absent in June and September. It operates through moisture more than heat, and heat matters mainly by amplifying moisture stress, which is consistent with the physiology of pod abortion and reduced seed fill under combined high vapour pressure deficit and low soil water. The precipitation response saturates and reverses, consistent with waterlogging, disease pressure and nitrogen loss at the wet extreme.

The county-level sensitivity gradient tracks soil water-holding capacity rather than climate exposure per se. Southern Illinois receives comparable rainfall to the north but has thinner, less retentive soils, so the same deficit translates into more stress.

### 5.2 What the evidence supports and what it does not

The design is observational panel data. County and year fixed effects absorb time-invariant county characteristics and statewide annual shocks, which removes large classes of confounding, but they do not remove county-specific time-varying factors: differential technology adoption, drainage tile installation, cultivar turnover, pest and disease pressure, or local land-use change.

The correct statement of the finding is therefore: **higher July-August temperatures and lower July-August moisture were statistically associated with lower soybean yield after controlling for county and year fixed effects, and this association is robust across thirteen specifications.** It is not: temperature caused yield to decline.

### 5.3 The 2003 anomaly, and a hypothesis that fails its test

One year resists climate explanation entirely. Decomposing the climate model's predictions by year, 1988 is explained to 88% and 2012 to 41%, but **2003 is explained to only 15%**. At a mean residual of **-3.43 bu/acre it is the largest unexplained shortfall in the record, rank 1 of 46 years.** Statewide August PDSI in 2003 was slightly positive and precipitation near normal, yet yield fell 8.5 bu/acre below trend. 2003 contributed 14 of the 39 observations exceeding three standard deviations in the entire panel.

The damage was regionally concentrated: Northwest Illinois lost 18.3 bu/acre while East district lost 15.1 with a positive Palmer Z-index.

**The obvious explanation was tested and does not hold.** 2003 is a documented severe soybean aphid outbreak year in the North Central region, with populations exceeding 1,000 per plant and 40% yield loss recorded at those densities (Ragsdale et al., *Journal of Integrated Pest Management*, 2012). The soybean aphid overwinters as eggs on common buckthorn, *Rhamnus cathartica*, which is concentrated **north of 41 degrees latitude** at densities above 10,000 per acre (Tilmon et al., *Journal of Integrated Pest Management*, 2011). Illinois straddles that line, spanning 37.2 to 42.5 degrees, which makes the hypothesis falsifiable against this panel. Five tests were run.

| Test | Result | Interpretation |
|---|---|---|
| Raw 2003 anomaly against county latitude | r = -0.775 | Strong northern concentration, consistent with the hypothesis |
| Model **residual** against latitude, 2003 | r = -0.124 | The gradient is climate, not the unexplained part |
| Rank of 2003 among 46 years by absolute latitude-residual correlation | **33 of 46** | Unremarkable |
| North (>= 41 N) minus South residual gap, 2003 | **+1.72** | **Wrong sign.** The north performed better once climate is removed |
| Same raw gradient in 1988, before the aphid existed in North America | r = -0.655 | A northern gradient in a bad year is not diagnostic |
| Aphid-era shift in the north-south residual gap, pre- versus post-2000 | Welch t = 0.205, **p = 0.84** | No detectable effect |

The northern concentration in 2003 is real, but it is **fully accounted for by climate**. Northwestern Illinois recorded a genuine August moisture deficit that year (district mean Palmer Z-index -2.60). What remains unexplained after the climate model is spatially uniform, which is the opposite of the signature a northern-origin pest would leave. The two other documented outbreak years behave inconsistently as well: 2005 shows a northern residual skew of -1.77, which is in the predicted direction, while 2001 shows -0.82 and 2003 shows the wrong sign entirely. None of the three ranks among the five most northern-skewed years on record, which are 1996, 2000, 2002, 2007 and 1982.

The finding is therefore narrower than a pest attribution and, in a way, more useful: **2003 is the largest unexplained shortfall in 46 years, and the most plausible candidate explanation does not match its geography.** The cause remains open. A definitive test would require county-level aphid scouting records or insecticide application data from the 2003 season, neither of which is in this dataset.

This is also a caution about the class of explanation. A documented event that coincides in time with an anomaly, and appears to match its geography, can still fail once the climate signal is removed from that geography. The raw spatial pattern looked like confirmation. It was not.

Supporting output: `results/table10_aphid_hypothesis_test.csv` and `results/12_aphid_hypothesis_test.json`.

### 5.4 Comparison with expectations from the literature

The estimated marginal effect of -0.66 bu/acre per °F, the nonlinear precipitation optimum, the dominance of the reproductive window, and the heat-moisture interaction are all qualitatively consistent with the published US crop-climate literature. The finding that penalised linear regression captures most of the signal available to gradient boosting is also consistent with work reporting that well-specified parametric damage functions are hard to beat when the functional form is known.

---

## 6. Limitations

**Monthly resolution cannot resolve frost or daily extremes.** The coldest monthly mean minimum temperature in the entire record is 32.3 °F in October and 46.4 °F in September. A monthly average never reaches a killing frost even in years when frost occurred. April minimum temperature correlates 0.005 with the yield anomaly, which is an instrument limitation, not evidence that frost does not matter. Degree days above a threshold, dry-spell length and rainfall intensity are likewise unavailable. **This is the single largest methodological gap and the primary upgrade path is gridMET 4 km daily data**, which additionally carries vapour pressure deficit natively.

**Vapour pressure deficit is absent.** VPD outperforms temperature as a yield predictor in recent work and cannot be constructed from these variables.

**No spatial aggregation step is executed.** NCEI performs the gridding and polygon aggregation upstream. The pipeline therefore inherits, rather than documents, the weighting method and the treatment of grid cells crossing county boundaries.

**Snow is not available.** nClimDiv contains no snow variable. Winter precipitation is the correct substitute for the soil-recharge mechanism and correlates only 0.055 with the anomaly.

**County coverage collapses after 2018.** From 102 counties reporting in 2000 to 62 in 2025, with the share of state harvested acreage carrying county attribution falling from 100% to 61%. Two consequences: county rows must never be summed to a state total in recent years, and survival is not random, so the recent panel is selected toward large producers precisely where out-of-sample validation occurs.

**Confounders are not controlled.** Cultivar turnover, drainage, fertiliser, pest pressure, machinery, crop insurance, price and policy are all absent. County fixed effects absorb the time-invariant portion only.

**No causal identification.** There is no experiment, instrument or discontinuity. All estimates are associations.

**Scenarios are not projections.** The six experiments apply uniform perturbations to observed climate. They use no CMIP6 or IPCC pattern, carry no probability, and assume no agronomic adaptation, cultivar change or planting-date shift. Real climate change would arrive with spatial structure, altered variability, elevated CO₂ fertilisation and an adaptive response, none of which is modelled.

**Machine-learning importance is not causal.** Permutation importance ranks predictive contribution under correlated features and should not be read as effect size.

**Champaign is one county in a panel.** Its 44 observations do not support independent estimation. All Champaign results are projections of state-panel estimates onto that county, which is why the panel design was chosen.

---

## 7. Conclusions

**1. Is climate variability associated with soybean yield?** Yes, robustly. The two-way fixed-effects model explains 66.8% of detrended yield variance, and the temperature effect is negative and significant at 5% in all thirteen robustness specifications, with a stable magnitude near -0.6 bu/acre per °F.

**2. Which variables matter most?** July-August moisture, best measured by the Palmer Z-index (r = 0.490) rather than raw precipitation (0.464) or PDSI (0.349). August maximum temperature follows (-0.469). Timing dominates magnitude: June precipitation correlates 0.08 and September 0.02, while August correlates 0.34. Anomaly and z-score forms beat natural units.

**3. Are relationships nonlinear?** Yes, decisively. Adding quadratic terms and an interaction raises R² from 0.254 to 0.361, the largest single specification gain. Precipitation has an interior optimum near 12.5 inches over July-August with the response reversing beyond it, and the drought penalty is roughly three times the wet-year bonus. Crucially, the temperature effect is conditional on moisture, at -0.89 bu/acre per °F in dry conditions against -0.43 in wet.

**4. Which counties are most vulnerable?** Sensitivity varies more than sevenfold, from 0.47 bu/acre per standard deviation of moisture in Mercer County to 3.60 in Clay County. Vulnerability concentrates in the southern and southeastern districts and correlates negatively with baseline yield (-0.512), so exposure is highest where the buffer is thinnest. Champaign sits at the 42nd percentile, less exposed than the state average.

**5. Does climate improve prediction?** Yes. Climate models beat a trend-only baseline by 15.7% in RMSE under expanding-window validation and by 19.8% under the fixed 2019-2025 test split. But the increment from algorithm sophistication is small: gradient boosting beats ridge regression by only 4.9%, so most of the signal is linear once the correct nonlinear terms are specified.

**5b. Can the largest anomaly be attributed?** No. 2003 is the largest unexplained shortfall in the record at -3.43 bu/acre, rank 1 of 46. The documented 2003 soybean aphid outbreak was tested as a candidate using the buckthorn 41-degree-latitude threshold and **rejected**: the northern concentration is fully explained by climate, the residual carries no latitude gradient (r = -0.124), the north-south residual gap has the wrong sign (+1.72), and there is no aphid-era shift (p = 0.84). The cause remains open.

**6. Are results robust?** Yes. The sign and significance of the temperature effect survive all thirteen checks, including dropping the balance rule, trimming extreme years, splitting the sample by period, changing the target to logs, levels and growth rates, and substituting alternative climate indicators. Removing 1988, 2003 and 2012 halves the magnitude, which confirms that extreme years carry a disproportionate share of a nonlinear damage function.

**7. What do the scenarios imply?** Under +1 °C with a 10% precipitation reduction, mean simulated yield falls 0.73 bu/acre (1.6%) and all 91 panel counties decline. Under +2 °C with a 20% reduction, the loss is 2.03 bu/acre (4.5%). The combination consistently exceeds the sum of the separate perturbations, which is the interaction expressing itself. Losses concentrate in the already-lowest-yielding southwest. **These are sensitivity experiments and carry no information about the likelihood of any future climate state.**

### Direct answer to the central question

Between 1980 and 2025, Illinois soybean yield was strongly and negatively associated with July-August heat and moisture deficit, once the county-specific technology trend of roughly 0.65 bu/acre per year was removed. Moisture matters more than heat, and heat matters mainly by amplifying moisture stress. The relationship is nonlinear with an interior precipitation optimum, and it is highly heterogeneous across counties, with sensitivity varying more than sevenfold and concentrating where baseline productivity is lowest. Climate information carries genuine out-of-sample predictive value, improving on a trend-only baseline by 15 to 20%. Simulated warming and drying reduce yield in essentially every county, with combined perturbations doing more damage than their separate effects would suggest. All of this is association under a fixed-effects design, not causal identification, and the perturbation experiments are sensitivity analyses rather than climate projections.
