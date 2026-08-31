"""04 - Build agronomic climate indicators from monthly county data.

Feature families (spec section 5): temperature, precipitation, anomalies,
extremes proxies, drought indices. Anomalies are county-specific departures
from that county's own 1980-2025 mean, so they are comparable across a
north-south gradient of 18 bu/acre in baseline yield.
"""
import sys, json, numpy as np, pandas as pd
sys.path.insert(0, str(__import__("pathlib").Path(__file__).parent))
from _cfg import RAW, PROC, RES, GROW_MONTHS, CRITICAL_MONTHS, SUMMER_MONTHS

def main():
    a = pd.read_csv(RAW/"nclimdiv_pcp_tmp_county.csv", dtype={"county_ansi":str})
    b = pd.read_csv(RAW/"nclimdiv_drought_temp_extra.csv", dtype={"county_ansi":str})
    for d in (a,b): d["county_ansi"]=d.county_ansi.str.zfill(3)
    c = a.merge(b, on=["county_ansi","year"], how="inner", validate="one_to_one")
    rep={"rows_pcp_tmp":len(a),"rows_extra":len(b),"rows_merged":len(c)}

    P=lambda m:f"pcp{m:02d}"; T=lambda m:f"tmp{m:02d}"
    # ---- precipitation -------------------------------------------------------
    c["pcp_grow"]     = c[[P(m) for m in GROW_MONTHS]].sum(axis=1)
    c["pcp_critical"] = c[[P(m) for m in CRITICAL_MONTHS]].sum(axis=1)
    c["pcp_summer"]   = c[[P(m) for m in SUMMER_MONTHS]].sum(axis=1)
    # ---- temperature ---------------------------------------------------------
    c["tmp_grow"]     = c[[T(m) for m in GROW_MONTHS]].mean(axis=1)
    c["tmp_critical"] = c[[T(m) for m in CRITICAL_MONTHS]].mean(axis=1)
    c["tmp_summer"]   = c[[T(m) for m in SUMMER_MONTHS]].mean(axis=1)
    c["tmax_critical"]= c[["tmax07","tmax08"]].mean(axis=1)
    c["tmax_summer"]  = c["tmax_jja"]
    c["tmp_range_crit"]= c["tmax_critical"] - c[["tmin09","tmin10"]].mean(axis=1)
    # ---- variability within the growing season ------------------------------
    c["pcp_grow_cv"]  = c[[P(m) for m in GROW_MONTHS]].std(axis=1)/c["pcp_grow"].replace(0,np.nan)*6
    c["tmp_grow_sd"]  = c[[T(m) for m in GROW_MONTHS]].std(axis=1)
    # ---- drought (Palmer) ----------------------------------------------------
    c["pdsi_critical"]= c[["pdsi07","pdsi08"]].mean(axis=1)
    c["zndx_critical"]= c[["zndx07","zndx08"]].mean(axis=1)
    c["drought_flag"] = (c.pdsi08 <= -2).astype(int)
    c["severe_drought"]=(c.pdsi08 <= -3).astype(int)
    # ---- heat / dry stress proxies (monthly resolution limits, see README) ---
    c["hot_month_count"] = (c[["tmax07","tmax08"]] >= 88).sum(axis=1)
    c["dry_month_count"] = (c[[P(m) for m in CRITICAL_MONTHS]] < 2.5).sum(axis=1)
    c["heat_x_dry"]      = c.tmax_critical * (-c.zndx08)

    # ---- county-specific anomalies (z-scores vs own 1980-2025 climatology) ---
    ANOM = ["pcp_grow","pcp_critical","pcp08","tmp_grow","tmp_critical",
            "tmax_critical","tmax08","pdsi08","zndx08"]
    g = c.groupby("county_ansi")
    for v in ANOM:
        c[f"{v}_anom"] = (c[v]-g[v].transform("mean"))
        sd = g[v].transform("std")
        c[f"{v}_z"] = c[f"{v}_anom"]/sd.replace(0,np.nan)

    c["climate_normal_pcp"] = g["pcp_critical"].transform("mean")
    c["climate_normal_tmax"]= g["tmax_critical"].transform("mean")

    rep["engineered_features"]=int(c.shape[1]-a.shape[1]-b.shape[1]+2)
    rep["nulls_total"]=int(c.isna().sum().sum())
    rep["growing_season"]=f"months {GROW_MONTHS} (April-September)"
    rep["critical_window"]=f"months {CRITICAL_MONTHS} (July-August, R3-R6 pod set and seed fill)"
    c.to_csv(PROC/"climate_features.csv", index=False)
    (RES/"04_climate_processing_report.json").write_text(json.dumps(rep, indent=2))
    for k,v in rep.items(): print(f"[04] {k:26} {v}")
    print(f"[04] columns out            {c.shape[1]}")
if __name__ == "__main__": main()
