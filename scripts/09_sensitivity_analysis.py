"""09 - County climate sensitivity and perturbation scenarios. Tables 7-8, Figs 13-16.

IMPORTANT: the scenarios below are SENSITIVITY EXPERIMENTS, not CMIP6 or IPCC
projections. They perturb observed climate by a fixed amount and re-predict.
They carry no information about the probability of any future climate state.
"""
import sys, json, pickle, numpy as np, pandas as pd
sys.path.insert(0, str(__import__("pathlib").Path(__file__).parent))
from sklearn.ensemble import GradientBoostingRegressor
from _cfg import FINAL, RES, FIG, MOD, SEED, FOCAL_COUNTY
from _viz import *

d = pd.read_csv(FINAL/"soybean_illinois_climate_1980_2025.csv",dtype={"county_ansi":str,"fips5":str})
d = d[d.in_balanced_panel==1].copy()
cfg=json.load(open(RES/"08_ml_config.json")); FEATS=cfg["features"]; TARGET=cfg["target"]

# ---------- Table 7: county climate sensitivity ------------------------------
rows=[]
for cty,g in d.groupby("county"):
    if len(g)<20: continue
    def r(v): 
        k=g[v].notna()&g[TARGET].notna()
        return float(np.corrcoef(g.loc[k,v],g.loc[k,TARGET])[0,1])
    # OLS slope of anomaly on standardized moisture and heat
    X=np.column_stack([np.ones(len(g)),(g.zndx08-g.zndx08.mean())/g.zndx08.std(),
                       (g.tmax_critical-g.tmax_critical.mean())/g.tmax_critical.std()])
    b,*_=np.linalg.lstsq(X,g[TARGET].values,rcond=None)
    rows.append(dict(county=cty,fips5=g.fips5.iloc[0],ag_district=g.ag_district.iloc[0],n=len(g),
        r_moisture=r("zndx08"),r_precip=r("pcp_critical"),r_heat=r("tmax_critical"),
        beta_moisture_bu_per_sd=float(b[1]),beta_heat_bu_per_sd=float(b[2]),
        yield_recent=float(g[g.year>=2015].yield_bu_ac.mean()),
        trend=float(g.trend_slope.iloc[0]),volatility=float(g[TARGET].std()),
        normal_pcp=float(g.pcp_critical.mean()),normal_tmax=float(g.tmax_critical.mean())))
t7=pd.DataFrame(rows)
t7["sensitivity_index"]=((t7.r_moisture.rank(pct=True)+(-t7.r_heat).rank(pct=True))/2).round(4)
t7=t7.sort_values("sensitivity_index",ascending=False).round(4)
t7.to_csv(RES/"table7_county_climate_sensitivity.csv",index=False)
print(f"[09] Table 7: {len(t7)} counties ranked")
print(t7.head(6)[["county","ag_district","r_moisture","r_heat","beta_moisture_bu_per_sd","sensitivity_index"]].to_string(index=False))
print("...")
print(t7.tail(4)[["county","ag_district","r_moisture","r_heat","beta_moisture_bu_per_sd","sensitivity_index"]].to_string(index=False))
foc=t7[t7.county==FOCAL_COUNTY].iloc[0]
print(f"\n[09] {FOCAL_COUNTY}: rank {int((t7.county==FOCAL_COUNTY).idxmax()) if False else list(t7.county).index(FOCAL_COUNTY)+1} of {len(t7)} "
      f"| r_moisture {foc.r_moisture:.3f} | beta_moisture {foc.beta_moisture_bu_per_sd:+.3f} bu/SD")

# ---------- Scenarios ---------------------------------------------------------
mdl = GradientBoostingRegressor(n_estimators=200,max_depth=3,learning_rate=.05,random_state=SEED).fit(d[FEATS],d[TARGET])
d["pred_baseline"]=mdl.predict(d[FEATS])

TEMP_F = ["tmax_critical","tmax08","tmp_grow","climate_normal_tmax"]
PREC   = ["pcp_critical","pcp_grow","pcp08","pcp07","pcp_win","climate_normal_pcp"]
def perturb(df,dT_C=0.0,dP_pct=0.0):
    x=df.copy(); dF=dT_C*1.8
    for c in TEMP_F: x[c]=x[c]+dF
    for c in PREC:   x[c]=x[c]*(1+dP_pct/100)
    x["heat_x_dry"]=x.tmax_critical*(-x.zndx08)          # recompute derived
    x["hot_month_count"]=(x[["tmax07","tmax08"]].add([dF,0]).ge(88)).sum(axis=1) if "tmax07" in x else x.hot_month_count
    return x
SCEN = {"S1 Baseline":(0,0),"S2 +1C":(1,0),"S3 -10% precip":(0,-10),
        "S4 +1C and -10% precip":(1,-10),"S5 +2C":(2,0),"S6 +2C and -20% precip":(2,-20)}
out=[]
for name,(dT,dP) in SCEN.items():
    d[f"pred_{name}"]=mdl.predict(perturb(d,dT,dP)[FEATS])
    dl=d[f"pred_{name}"]-d.pred_baseline
    out.append(dict(scenario=name,delta_T_C=dT,delta_P_pct=dP,
        mean_delta_bu=float(dl.mean()),
        pct_of_mean_yield=float(dl.mean()/d.yield_bu_ac.mean()*100),
        p10=float(dl.quantile(.1)),p90=float(dl.quantile(.9)),
        counties_worse=int((d.groupby("county")[f"pred_{name}"].mean()-d.groupby("county").pred_baseline.mean()<0).sum())))
S=pd.DataFrame(out).round(4); S.to_csv(RES/"table8a_scenario_state_summary.csv",index=False)
print("\n[09] SCENARIO SUMMARY (sensitivity experiments, NOT climate projections)")
print(S.to_string(index=False))

bycty=d.groupby(["county","fips5","ag_district"]).agg(
    baseline_yield=("yield_bu_ac","mean"),**{f"d_{k}":(f"pred_{k}","mean") for k in SCEN}).reset_index()
for k in SCEN: bycty[f"d_{k}"]=bycty[f"d_{k}"]-bycty["d_S1 Baseline"]
bycty["pct_S4"]=(bycty["d_S4 +1C and -10% precip"]/bycty.baseline_yield*100)
bycty=bycty.round(4); bycty.to_csv(RES/"table8b_scenario_by_county.csv",index=False)
print(f"\n[09] worst counties under S4 (+1C, -10% precip):")
print(bycty.nsmallest(6,"d_S4 +1C and -10% precip")[["county","ag_district","baseline_yield","d_S4 +1C and -10% precip","pct_S4"]].to_string(index=False))
print(f"[09] least affected:")
print(bycty.nlargest(4,"d_S4 +1C and -10% precip")[["county","ag_district","baseline_yield","d_S4 +1C and -10% precip","pct_S4"]].to_string(index=False))
fc=bycty[bycty.county==FOCAL_COUNTY].iloc[0]
print(f"\n[09] {FOCAL_COUNTY} under S4: {fc['d_S4 +1C and -10% precip']:+.2f} bu/acre ({fc.pct_S4:+.2f}%)")

# ---------- Figures 13-16 -----------------------------------------------------
f,ax=fig(11,7.6)
k=t7.sort_values("beta_moisture_bu_per_sd")
cols=[FOCAL if c==FOCAL_COUNTY else S1 for c in k.county]
ax.barh(range(len(k)),k.beta_moisture_bu_per_sd,color=cols,height=.86)
ax.set_yticks([]); ax.set_ylabel("91 counties, ordered",fontsize=10,color=INK2)
i=list(k.county).index(FOCAL_COUNTY)
ax.annotate(f"{FOCAL_COUNTY}",xy=(k.beta_moisture_bu_per_sd.iloc[i],i),xytext=(1.2,i-9),
    fontsize=10,color=FOCAL,arrowprops=dict(arrowstyle="->",color=FOCAL,lw=1.3))
ax.grid(axis="y",lw=0); ax.grid(axis="x",color=GRID,lw=.7)
style(ax,"Figure 13. County climate sensitivity to August moisture",
      "Yield response to a one-standard-deviation moisture anomaly, county-by-county regression",
      "bu/acre per SD of Palmer Z-index",None,src=SRC)
save(f,FIG/"fig13_county_climate_sensitivity.png")

for n,(key,ttl) in enumerate([("S2 +1C","Figure 14. Baseline versus +1 °C"),
                              ("S3 -10% precip","Figure 15. Baseline versus -10% precipitation"),
                              ("S4 +1C and -10% precip","Figure 16. Baseline versus +1 °C and -10% precipitation")],14):
    f,ax=fig(10.5,6)
    v=bycty[f"d_{key}"]
    ax.hist(v,bins=26,color=S2 if v.mean()<0 else S1,edgecolor=SURFACE,lw=1.1)
    ax.axvline(0,color=INK,lw=1.2); ax.axvline(v.mean(),color=FOCAL,lw=2,ls="--",
        label=f"mean {v.mean():+.2f} bu/acre")
    ax.axvline(bycty.loc[bycty.county==FOCAL_COUNTY,f"d_{key}"].iloc[0],color=S4,lw=2,
        label=f"{FOCAL_COUNTY} {bycty.loc[bycty.county==FOCAL_COUNTY,f'd_{key}'].iloc[0]:+.2f}")
    style(ax,ttl,"Sensitivity experiment, not a climate projection. Distribution across 91 counties.",
          "Change in predicted yield (bu/acre)","Counties",legend=True,src=SRC)
    save(f,FIG/f"fig{n}_scenario_{key.split()[0].lower()}.png")
json.dump({"scenarios":{k:dict(delta_T_C=v[0],delta_P_pct=v[1]) for k,v in SCEN.items()},
  "disclaimer":"Sensitivity experiments. Uniform perturbations of observed climate. "
               "Not CMIP6/IPCC projections and carry no probability information."},
  open(RES/"09_scenario_config.json","w"),indent=2)
