"""05 - Merge production and climate into the analytical panel, and build the
detrended yield target.

Target: yield_anom = residual of a COUNTY-SPECIFIC linear trend in yield.
Rationale (spec section 8): technology, cultivar improvement and machinery
produce a strong upward trend (~0.65 bu/acre/yr statewide) that is orthogonal
to climate. Left in, it is absorbed by any climate variable that also trends,
inverting the sign of warming coefficients.
"""
import sys, json, numpy as np, pandas as pd
sys.path.insert(0, str(__import__("pathlib").Path(__file__).parent))
from _cfg import PROC, FINAL, RES, FOCAL_COUNTY

MIN_YEARS = 42   # inclusion rule, fixed BEFORE modelling

def main():
    p = pd.read_csv(PROC/"production_clean.csv", dtype={"county_ansi":str,"fips5":str,"ag_district_code":str})
    c = pd.read_csv(PROC/"climate_features.csv", dtype={"county_ansi":str})
    p["county_ansi"]=p.county_ansi.str.zfill(3); c["county_ansi"]=c.county_ansi.str.zfill(3)

    rep={"production_rows":len(p),"climate_rows":len(c)}
    m = p.merge(c, on=["county_ansi","year"], how="left", validate="one_to_one")
    rep["merged_rows"]=len(m)
    rep["unmatched_climate"]=int(m.pcp_critical.isna().sum())
    rep["counties"]=int(m.county.nunique()); rep["years"]=int(m.year.nunique())
    assert rep["unmatched_climate"]==0, "climate join incomplete"

    # ---- county-specific trend and detrended target -------------------------
    m = m.sort_values(["county","year"]).reset_index(drop=True)
    m["trend_slope"]=np.nan; m["yield_trend"]=np.nan
    for cty, idx in m.groupby("county").groups.items():
        g = m.loc[idx]
        s,i = np.polyfit(g.year.values, g.yield_bu_ac.values, 1)
        m.loc[idx,"trend_slope"]=s
        m.loc[idx,"yield_trend"]=s*g.year.values+i
    m["yield_anom"]=m.yield_bu_ac-m.yield_trend
    m["log_yield"]=np.log(m.yield_bu_ac)

    # ---- panel balance -------------------------------------------------------
    n = m.groupby("county").year.count()
    m["n_years_county"]=m.county.map(n)
    m["in_balanced_panel"]=(m.n_years_county>=MIN_YEARS).astype(int)
    m["is_focal"]=(m.county==FOCAL_COUNTY).astype(int)
    rep["min_years_rule"]=MIN_YEARS
    rep["counties_in_balanced_panel"]=int((n>=MIN_YEARS).sum())
    rep["rows_in_balanced_panel"]=int(m.in_balanced_panel.sum())
    rep["focal_county"]=FOCAL_COUNTY
    rep["focal_rows"]=int(m.is_focal.sum())
    rep["focal_year_range"]=[int(m.loc[m.is_focal==1,'year'].min()),int(m.loc[m.is_focal==1,'year'].max())]
    rep["trend_slope_min"]=round(float(m.groupby('county').trend_slope.first().min()),3)
    rep["trend_slope_max"]=round(float(m.groupby('county').trend_slope.first().max()),3)

    m.to_csv(FINAL/"soybean_illinois_climate_1980_2025.csv", index=False)
    (RES/"05_merge_report.json").write_text(json.dumps(rep, indent=2))
    for k,v in rep.items(): print(f"[05] {k:28} {v}")
    print(f"[05] {'final columns':28} {m.shape[1]}")
if __name__ == "__main__": main()
