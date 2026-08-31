"""06 - Exploratory data analysis. Figures 1-9, Tables 1-3."""
import sys, numpy as np, pandas as pd
sys.path.insert(0, str(__import__("pathlib").Path(__file__).parent))
from _cfg import FINAL, FIG, RES, FOCAL_COUNTY
from _viz import *

d = pd.read_csv(FINAL/"soybean_illinois_climate_1980_2025.csv",dtype={"county_ansi":str,"fips5":str})
st = pd.read_csv(FINAL.parent/"raw/nass_il_state_totals.csv")
F = d[d.is_focal==1].sort_values("year")

# ---------------- Table 1: dataset characteristics --------------------------
t1 = pd.DataFrame([
 ("Spatial unit","County (USDA NASS / Census FIPS)"),
 ("Number of counties","102"),
 ("Focal unit",f"{FOCAL_COUNTY} County, FIPS 17019"),
 ("Temporal coverage","1980-2025 (46 years)"),
 ("Panel observations",f"{len(d):,}"),
 ("Balanced-panel rule","counties with >= 42 of 46 years"),
 ("Balanced-panel size",f"{int(d.in_balanced_panel.sum()):,} rows, {d.loc[d.in_balanced_panel==1,'county'].nunique()} counties"),
 ("Production source","USDA NASS Quick Stats, SURVEY program, Period=YEAR"),
 ("Climate source","NOAA NCEI nClimDiv, county monthly"),
 ("Climate resolution","monthly; county polygons pre-aggregated by NCEI"),
 ("Target variable","yield_anom = yield residual from county-specific linear trend"),
 ("Growing season","April-September"),
 ("Critical window","July-August (R3-R6 pod set and seed fill)"),
], columns=["Attribute","Value"])
t1.to_csv(RES/"table1_dataset_characteristics.csv",index=False)

# ---------------- Table 2: descriptive statistics ---------------------------
vars2 = ["yield_bu_ac","yield_kg_ha","yield_anom","acres_planted","production_bu",
         "pcp_grow","pcp_critical","tmp_grow","tmax_critical","pdsi08","zndx08"]
t2 = d[vars2].describe().T[["count","mean","std","min","25%","50%","75%","max"]]
t2["cv_%"] = (t2["std"]/t2["mean"]*100).round(1)
t2 = t2.round(3); t2.index.name="variable"
t2.to_csv(RES/"table2_descriptive_statistics.csv")

# ---------------- Table 3: climate-production correlations ------------------
cl = [c for c in d.columns if c.startswith(("pcp","tmp","tmax","tmin","pdsi","zndx","hot_","dry_","heat_"))]
cl = [c for c in cl if d[c].std()>0 and d[c].nunique()>5]
rows=[]
for v in cl:
    k=d.yield_anom.notna()&d[v].notna()
    r=np.corrcoef(d.loc[k,v],d.loc[k,"yield_anom"])[0,1]
    rraw=np.corrcoef(d.loc[k,v],d.loc[k,"yield_bu_ac"])[0,1]
    kf=F[v].notna()
    rf=np.corrcoef(F.loc[kf,v],F.loc[kf,"yield_anom"])[0,1] if kf.sum()>10 else np.nan
    rows.append(dict(variable=v,r_detrended=r,r2=r*r,r_raw_yield=rraw,r_champaign=rf,n=int(k.sum())))
t3=pd.DataFrame(rows).sort_values("r2",ascending=False).round(4)
t3.to_csv(RES/"table3_climate_production_correlations.csv",index=False)
print(f"[06] tables 1-3 written | {len(t3)} climate variables screened")

# ================= FIGURES ==================================================
# F1 national/state production over time
f,ax=fig(); ax.plot(st.year,st.production_bu/1e6,color=S1,lw=2.2,marker="o",ms=4)
style(ax,"Figure 1. Illinois soybean production, 1980 to 2025",
      "State total, official USDA NASS estimate","Year","Production (million bushels)",src=SRC)
save(f,FIG/"fig01_state_production_timeseries.png")

# F2 production by county, recent decade
r=d[d.year>=2015].groupby("county").production_bu.mean().nlargest(25)/1e6
f,ax=fig(11,7.5); cols=[FOCAL if c==FOCAL_COUNTY else S1 for c in r.index]
ax.barh(range(len(r)),r.values,color=cols,height=.72)
ax.set_yticks(range(len(r))); ax.set_yticklabels(r.index,fontsize=8.5); ax.invert_yaxis()
style(ax,"Figure 2. Mean annual soybean production by county, 2015 to 2025",
      f"Top 25 counties. {FOCAL_COUNTY} highlighted.","Production (million bushels)",None,src=SRC)
ax.grid(axis="y",lw=0); ax.grid(axis="x",color=GRID,lw=.7)
save(f,FIG/"fig02_production_by_county.png")

# F3 county yield trends spaghetti
f,ax=fig(11,6.5)
for c,g in d.groupby("county"):
    if c==FOCAL_COUNTY: continue
    ax.plot(g.year,g.yield_bu_ac,color="#c9c8c2",lw=.6,alpha=.55,zorder=1)
ax.plot(F.year,F.yield_bu_ac,color=FOCAL,lw=2.6,zorder=3,label=f"{FOCAL_COUNTY} County")
sm=d.groupby("year").apply(lambda g: (g.production_bu.sum()/g.acres_harvested.sum()),include_groups=False)
ax.plot(sm.index,sm.values,color=S1,lw=2.4,ls="--",zorder=2,label="Illinois (acreage-weighted)")
style(ax,"Figure 3. County soybean yield trajectories, 1980 to 2025",
      "102 counties in gray","Year","Yield (bu/acre)",legend=True,src=SRC)
save(f,FIG/"fig03_county_yield_trends.png")

# F4 temperature trend
f,ax=fig()
ts=d.groupby("year").tmax_critical.mean()
ax.plot(ts.index,ts.values,color=S2,lw=2.0,marker="o",ms=3.5,label="Illinois mean")
ax.plot(F.year,F.tmax_critical,color=FOCAL,lw=1.4,alpha=.8,label=f"{FOCAL_COUNTY}")
b=np.polyfit(ts.index,ts.values,1); ax.plot(ts.index,np.polyval(b,ts.index),color=INK2,ls=":",lw=1.6,
        label=f"trend {b[0]*10:+.2f} °F/decade")
style(ax,"Figure 4. July-August maximum temperature, 1980 to 2025",
      "Critical window for pod set and seed fill","Year","Mean daily maximum (°F)",legend=True,src=SRC)
save(f,FIG/"fig04_temperature_trend.png")

# F5 precipitation trend
f,ax=fig()
ps=d.groupby("year").pcp_critical.mean()
ax.bar(ps.index,ps.values,color=S3,width=.72)
b=np.polyfit(ps.index,ps.values,1); ax.plot(ps.index,np.polyval(b,ps.index),color=INK2,ls=":",lw=1.8,
        label=f"trend {b[0]*10:+.2f} in/decade")
style(ax,"Figure 5. July-August precipitation, 1980 to 2025",
      "Illinois county mean","Year","Precipitation (inches)",legend=True,src=SRC)
save(f,FIG/"fig05_precipitation_trend.png")

# F6 temperature-yield relationship
f,ax=fig()
ax.scatter(d.tmax_critical,d.yield_anom,s=8,c=d.yield_anom,cmap=DIV,vmin=-13,vmax=13,alpha=.45,lw=0)
q=pd.qcut(d.tmax_critical,12,duplicates="drop")
bm=d.groupby(q,observed=True).agg(x=("tmax_critical","mean"),y=("yield_anom","mean"))
ax.plot(bm.x,bm.y,color=INK,lw=2.4,marker="o",ms=5,label="binned mean")
ax.axhline(0,color=MUTED,lw=.9)
style(ax,"Figure 6. Yield anomaly against July-August maximum temperature",
      f"n = {len(d):,} county-years","Mean daily maximum, Jul-Aug (°F)","Yield anomaly (bu/acre)",legend=True,src=SRC)
save(f,FIG/"fig06_temperature_yield.png")

# F7 precipitation-yield relationship
f,ax=fig()
ax.scatter(d.pcp_critical,d.yield_anom,s=8,c=d.yield_anom,cmap=DIV,vmin=-13,vmax=13,alpha=.45,lw=0)
q=pd.qcut(d.pcp_critical,12,duplicates="drop")
bm=d.groupby(q,observed=True).agg(x=("pcp_critical","mean"),y=("yield_anom","mean"))
ax.plot(bm.x,bm.y,color=INK,lw=2.4,marker="o",ms=5,label="binned mean")
cf=np.polyfit(d.pcp_critical,d.yield_anom,2); xs=np.linspace(d.pcp_critical.min(),d.pcp_critical.max(),100)
ax.plot(xs,np.polyval(cf,xs),color=S3,lw=2.0,ls="--",label=f"quadratic, optimum {-cf[1]/(2*cf[0]):.1f} in")
ax.axhline(0,color=MUTED,lw=.9)
style(ax,"Figure 7. Yield anomaly against July-August precipitation",
      "Response saturates then reverses","Precipitation, Jul-Aug (inches)","Yield anomaly (bu/acre)",legend=True,src=SRC)
save(f,FIG/"fig07_precipitation_yield.png")

# F8 climate anomaly vs production anomaly
f,ax=fig()
ax.scatter(d.zndx08_z,d.yield_anom,s=9,color=S1,alpha=.35,lw=0)
q=pd.qcut(d.zndx08_z,12,duplicates="drop")
bm=d.groupby(q,observed=True).agg(x=("zndx08_z","mean"),y=("yield_anom","mean"))
ax.plot(bm.x,bm.y,color=S2,lw=2.6,marker="o",ms=5,label="binned mean")
ax.axhline(0,color=MUTED,lw=.9); ax.axvline(0,color=MUTED,lw=.9)
style(ax,"Figure 8. Yield anomaly against August moisture anomaly",
      "Palmer Z-index expressed as a county-specific z-score","Moisture anomaly (z)","Yield anomaly (bu/acre)",legend=True,src=SRC)
save(f,FIG/"fig08_climate_anomaly_vs_yield.png")

# F9 correlation matrix
sel=["yield_anom","pcp_critical","pcp_grow","tmax_critical","tmp_grow","zndx08",
     "pdsi08","tmin10","pcp_win","heat_x_dry"]
C=d[sel].corr()
f,ax=fig(8.6,7.4)
im=ax.imshow(C.values,cmap=DIV,vmin=-1,vmax=1)
ax.set_xticks(range(len(sel))); ax.set_xticklabels(sel,rotation=45,ha="right",fontsize=8.5,color=INK2)
ax.set_yticks(range(len(sel))); ax.set_yticklabels(sel,fontsize=8.5,color=INK2)
for i in range(len(sel)):
    for j in range(len(sel)):
        ax.text(j,i,f"{C.values[i,j]:.2f}",ha="center",va="center",fontsize=7.6,
                color="#ffffff" if abs(C.values[i,j])>.62 else INK)
ax.grid(False); [s.set_visible(False) for s in ax.spines.values()]
ax.tick_params(length=0)
ax.text(0,1.045,"Figure 9. Correlation matrix, target and climate predictors",
        transform=ax.transAxes,fontsize=14.5,color=INK,va="bottom",fontweight="semibold")
f.colorbar(im,ax=ax,fraction=.038,pad=.02).outline.set_visible(False)
save(f,FIG/"fig09_correlation_matrix.png")
print("[06] EDA complete: 9 figures, 3 tables")
