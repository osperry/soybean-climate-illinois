"""11 - Robustness checks (spec section 18)."""
import sys, json, numpy as np, pandas as pd, warnings
warnings.filterwarnings("ignore")
sys.path.insert(0, str(__import__("pathlib").Path(__file__).parent))
import statsmodels.formula.api as smf
from _cfg import FINAL, RES

d=pd.read_csv(FINAL/"soybean_illinois_climate_1980_2025.csv",dtype={"county_ansi":str})
d["PCP"]=d.pcp_critical; d["TMX"]=d.tmax_critical
d["PCP2"]=d.PCP**2; d["TMX2"]=d.TMX**2; d["PT"]=d.PCP*d.TMX
d["cty"]=d.county.astype("category"); d["yr"]=d.year.astype("category")
FORM="yield_anom ~ PCP + PCP2 + TMX + TMX2 + PT + C(cty) + C(yr)"

def run(df,label,form=FORM,tgt="yield_anom"):
    f=form.replace("yield_anom",tgt)
    m=smf.ols(f,data=df).fit(cov_type="cluster",cov_kwds={"groups":df.county})
    gp=lambda k: float(m.params[k]) if k in m.params.index else np.nan
    pv=lambda k: float(m.pvalues[k]) if k in m.pvalues.index else np.nan
    Pname = "PCP" if "PCP" in m.params.index else "pcp_grow"
    P2name= "PCP2" if "PCP2" in m.params.index else "I(pcp_grow ** 2)"
    Pb,P2b,Tb,T2b,PTb = gp(Pname),gp(P2name),gp("TMX"),gp("TMX2"),gp("PT")
    Pbar = df[Pname].mean() if Pname in df else df.PCP.mean()
    Tbar = df.TMX.mean()
    return dict(check=label,n=int(m.nobs),r2=round(m.rsquared,4),
        dY_dT=round(Tb+2*T2b*Tbar+PTb*Pbar,4), dY_dP=round(Pb+2*P2b*Pbar+PTb*Tbar,4),
        p_TMX=round(pv("TMX"),5), p_PCP=round(pv(Pname),5), p_interaction=round(pv("PT"),5))

base=d[d.in_balanced_panel==1]
R=[run(base,"Reference: balanced panel, two-way FE")]
R.append(run(d,"All 102 counties (no balance rule)"))
R.append(run(base[base.n_years_county==46],"Fully balanced only (28 counties)"))
q=base.yield_anom.quantile([.01,.99])
R.append(run(base[(base.yield_anom>q.iloc[0])&(base.yield_anom<q.iloc[1])],"Trim 1% extreme yield years"))
cq=base.PCP.quantile([.02,.98])
R.append(run(base[(base.PCP>cq.iloc[0])&(base.PCP<cq.iloc[1])],"Trim 2% extreme precip years"))
R.append(run(base[~base.year.isin([1988,2003,2012])],"Drop 1988, 2003, 2012"))
R.append(run(base[base.year<=2002],"Early period only (1980-2002)"))
R.append(run(base[base.year>=2003],"Late period only (2003-2025)"))
R.append(run(base,"County FE only (no year FE)",FORM.replace(" + C(yr)","")))
R.append(run(base,"Alternative indicator: growing-season precip",
    "yield_anom ~ pcp_grow + I(pcp_grow**2) + TMX + TMX2 + PT + C(cty) + C(yr)"))
R.append(run(base,"Target: log yield",tgt="log_yield"))
R.append(run(base,"Target: raw yield (trend uncontrolled)",tgt="yield_bu_ac"))
g=base.sort_values(["county","year"]).copy()
g["yg"]=g.groupby("county").yield_bu_ac.pct_change()*100
R.append(run(g.dropna(subset=["yg"]),"Target: yield growth (%)",tgt="yg"))

t=pd.DataFrame(R); t.to_csv(RES/"table9_robustness.csv",index=False)
print("=== ROBUSTNESS (spec section 18) ===")
print(t.to_string(index=False))
sig=(t.p_TMX<.05).sum()
print(f"\n[11] temperature term significant at 5% in {sig} of {len(t)} specifications")
print(f"[11] dY/dT sign negative in {(t.dY_dT<0).sum()} of {len(t)}")
json.dump(dict(specs=len(t),temp_sig=int(sig),neg_sign=int((t.dY_dT<0).sum()),
  dY_dT_range=[float(t.dY_dT.min()),float(t.dY_dT.max())]),open(RES/"11_robustness_summary.json","w"),indent=2)
