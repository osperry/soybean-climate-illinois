"""07 - Panel statistical models. Table 4.

Specifications escalate from a naive pooled OLS to a two-way fixed-effects
model with county-clustered standard errors, matching spec sections 9-10.
"""
import sys, json, numpy as np, pandas as pd
sys.path.insert(0, str(__import__("pathlib").Path(__file__).parent))
import statsmodels.formula.api as smf
import statsmodels.api as sm
from statsmodels.stats.diagnostic import het_breuschpagan
from _cfg import FINAL, RES, MOD, FOCAL_COUNTY

d = pd.read_csv(FINAL/"soybean_illinois_climate_1980_2025.csv",dtype={"county_ansi":str})
d = d[d.in_balanced_panel==1].copy()
d["PCP"]=d.pcp_critical; d["TMX"]=d.tmax_critical
d["PCP2"]=d["PCP"]**2; d["TMX2"]=d["TMX"]**2; d["PT"]=d["PCP"]*d["TMX"]
d["cty"]=d.county.astype("category"); d["yr"]=d.year.astype("category")
print(f"[07] estimation sample: {len(d):,} rows, {d.county.nunique()} counties, {d.year.nunique()} years")

SPECS = {
 "M1 Baseline pooled OLS"        : "yield_anom ~ PCP + TMX",
 "M2 Quadratic + interaction"    : "yield_anom ~ PCP + PCP2 + TMX + TMX2 + PT",
 "M3 M2 + county FE"             : "yield_anom ~ PCP + PCP2 + TMX + TMX2 + PT + C(cty)",
 "M4 Two-way FE (county + year)" : "yield_anom ~ PCP + PCP2 + TMX + TMX2 + PT + C(cty) + C(yr)",
 "M5 Palmer Z specification"     : "yield_anom ~ zndx08 + I(zndx08**2) + TMX + TMX2 + C(cty)",
 "M6 Raw yield, two-way FE"      : "yield_bu_ac ~ PCP + PCP2 + TMX + TMX2 + PT + year + C(cty)",
 "M7 Log yield, county FE"       : "log_yield ~ PCP + PCP2 + TMX + TMX2 + PT + year + C(cty)",
}
rows=[]; coefs=[]
for name,f in SPECS.items():
    m = smf.ols(f, data=d).fit(cov_type="cluster", cov_kwds={"groups": d.county})
    yhat=m.fittedvalues; resid=m.resid
    rmse=float(np.sqrt(np.mean(resid**2))); mae=float(np.mean(np.abs(resid)))
    try:
        bp = het_breuschpagan(resid, m.model.exog)[1]
    except Exception: bp=np.nan
    dw = float(sm.stats.durbin_watson(resid))
    rows.append(dict(model=name, n=int(m.nobs), k=int(m.df_model), r2=m.rsquared,
        adj_r2=m.rsquared_adj, RMSE=rmse, MAE=mae, aic=m.aic, bic=m.bic,
        F_pvalue=float(m.f_pvalue), breusch_pagan_p=bp, durbin_watson=dw,
        se_type="cluster(county)"))
    for term in [t for t in m.params.index if not t.startswith("C(")]:
        ci=m.conf_int().loc[term]
        coefs.append(dict(model=name,term=term,coef=m.params[term],se=m.bse[term],
            t=m.tvalues[term],p=m.pvalues[term],ci_low=ci[0],ci_high=ci[1]))
    if name.startswith("M4"): m.save(str(MOD/"m4_twoway_fe.pkl"))

t4=pd.DataFrame(rows).round(5); t4.to_csv(RES/"table4_regression_models.csv",index=False)
cf=pd.DataFrame(coefs).round(5); cf.to_csv(RES/"table4b_regression_coefficients.csv",index=False)
print("\n[07] MODEL COMPARISON")
print(t4[["model","n","k","r2","adj_r2","RMSE","breusch_pagan_p","durbin_watson"]].to_string(index=False))

m4 = smf.ols(SPECS["M4 Two-way FE (county + year)"],data=d).fit(cov_type="cluster",cov_kwds={"groups":d.county})
print("\n[07] M4 climate coefficients (county-clustered SE)")
print(cf[cf.model.str.startswith("M4")][["term","coef","se","p","ci_low","ci_high"]].to_string(index=False))
Pb,P2b = m4.params["PCP"], m4.params["PCP2"]
Tb,T2b = m4.params["TMX"], m4.params["TMX2"]; PTb = m4.params["PT"]
Pbar, Tbar = d["PCP"].mean(), d["TMX"].mean()
# With an interaction the turning point is conditional; evaluate at the sample mean
P_opt = -(Pb + PTb*Tbar)/(2*P2b)
T_opt = -(Tb + PTb*Pbar)/(2*T2b)
me_T  = Tb + 2*T2b*Tbar + PTb*Pbar          # dY/dT at means
me_P  = Pb + 2*P2b*Pbar + PTb*Tbar          # dY/dP at means
print(f"\n[07] sample means           : Jul-Aug precip {Pbar:.2f} in, Jul-Aug tmax {Tbar:.2f} °F")
print(f"[07] precip optimum | T=mean: {P_opt:.2f} inches")
print(f"[07] temp optimum   | P=mean: {T_opt:.2f} °F")
print(f"[07] dYield/dT at means     : {me_T:+.3f} bu/acre per °F")
print(f"[07] dYield/dP at means     : {me_P:+.3f} bu/acre per inch")
# heat penalty is larger in dry conditions: evaluate dY/dT at P = 10th vs 90th pct
for q,lab in [(.1,"dry (P10)"),(.9,"wet (P90)")]:
    Pq=d["PCP"].quantile(q); print(f"[07] dYield/dT at {lab:10}: {Tb+2*T2b*Tbar+PTb*Pq:+.3f} bu/acre per °F  (P={Pq:.1f} in)")
json.dump(dict(precip_optimum_in_at_mean_T=float(P_opt),temp_optimum_F_at_mean_P=float(T_opt),
   dY_dT_at_means=float(me_T),dY_dP_at_means=float(me_P),
   dY_dT_dry_P10=float(Tb+2*T2b*Tbar+PTb*d["PCP"].quantile(.1)),
   dY_dT_wet_P90=float(Tb+2*T2b*Tbar+PTb*d["PCP"].quantile(.9)),
   mean_precip_in=float(Pbar),mean_tmax_F=float(Tbar),n=int(m4.nobs),
   r2_M4=float(m4.rsquared)),open(RES/"07_key_estimates.json","w"),indent=2)
