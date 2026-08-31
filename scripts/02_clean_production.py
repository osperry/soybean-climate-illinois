"""02 - Clean production data. Mirrors the IBGE cleaning contract.

Handles: sentinel codes, thousands separators, duplicate keys, non-county
aggregate rows, unit verification, and the identity check.
"""
import sys, json, numpy as np, pandas as pd
sys.path.insert(0, str(__import__("pathlib").Path(__file__).parent))
from _cfg import RAW, PROC, RES

SENTINELS = {"(D)","(S)","(Z)","(NA)","(X)","-",""}

def main():
    d = pd.read_csv(RAW/"nass_il_soybeans_county_raw.csv",
                    dtype={"county_ansi":str,"ag_district_code":str,"state_ansi":str})
    rep = {"rows_in": len(d)}

    # -- 1. sentinel handling: distinguish MISSING from genuine ZERO -----------
    meas = ["acres_planted","acres_harvested","production_bu","yield_bu_ac"]
    for c in meas:
        s = d[c].astype(str).str.strip().str.replace(",","",regex=False)
        d[c] = pd.to_numeric(s.where(~s.isin(SENTINELS)), errors="coerce")
    rep["sentinel_or_unparsed_cells"] = int(d[meas].isna().sum().sum())

    # -- 2. aggregate rows are NOT counties -----------------------------------
    d["county_ansi"] = d.county_ansi.astype(str).str.zfill(3).replace("nan","")
    d["is_county_estimate"] = (~d.county.str.startswith("OTHER")).astype(int)
    rep["aggregate_rows_dropped"] = int((d.is_county_estimate==0).sum())
    d = d[d.is_county_estimate==1].copy()

    # -- 3. duplicate key audit ------------------------------------------------
    #  NASS publishes one OTHER-COUNTIES bucket per Ag District, so the raw key
    #  is county_ansi + ag_district_code + year. Real counties must be unique on
    #  county_ansi + year alone.
    dup = d.duplicated(["county_ansi","year"]).sum()
    rep["duplicate_county_year"] = int(dup)
    assert dup == 0, "duplicate county-year rows survived cleaning"

    # -- 4. produced_soy indicator (do not read zero as missing) ---------------
    d["produced_soy"] = np.where(d.acres_planted.notna() & (d.acres_planted>0), 1,
                        np.where(d.acres_planted.notna(), 0, np.nan))
    rep["zero_production_rows"] = int((d.produced_soy==0).sum())

    # -- 5. unit + identity verification ---------------------------------------
    ok = d.acres_harvested.notna() & d.production_bu.notna() & d.yield_bu_ac.notna() & (d.acres_harvested>0)
    resid = (d.loc[ok,"production_bu"]/d.loc[ok,"acres_harvested"] - d.loc[ok,"yield_bu_ac"]).abs()
    rep["identity_checked"] = int(ok.sum())
    rep["identity_max_residual_bu_per_acre"] = round(float(resid.max()),4)
    rep["identity_failures_gt_0.55"] = int((resid>0.55).sum())
    rep["harvested_gt_planted"] = int((d.acres_harvested > d.acres_planted + 0.5).sum())

    # -- 6. metric conversions (kg/ha for international comparability) ---------
    KG_PER_BU, HA_PER_ACRE = 27.2155, 0.404685642
    d["yield_kg_ha"]      = d.yield_bu_ac * (KG_PER_BU/HA_PER_ACRE)
    d["production_tonnes"]= d.production_bu * KG_PER_BU/1000.0
    d["area_harvested_ha"]= d.acres_harvested * HA_PER_ACRE
    d["fips5"] = "17" + d.county_ansi

    keep = ["state","state_ansi","county","county_ansi","fips5","ag_district",
            "ag_district_code","year","produced_soy","acres_planted","acres_harvested",
            "production_bu","yield_bu_ac","yield_kg_ha","production_tonnes","area_harvested_ha"]
    d = d[keep].sort_values(["county","year"]).reset_index(drop=True)
    rep.update(rows_out=len(d), counties=int(d.county.nunique()),
               year_min=int(d.year.min()), year_max=int(d.year.max()))
    d.to_csv(PROC/"production_clean.csv", index=False)
    (RES/"02_cleaning_report.json").write_text(json.dumps(rep, indent=2))
    for k,v in rep.items(): print(f"[02] {k:38} {v}")

if __name__ == "__main__":
    main()
