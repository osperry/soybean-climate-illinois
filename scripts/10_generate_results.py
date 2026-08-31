"""10 - Figure 17 (choropleth), final dataset, data dictionary, results index."""
import sys, json, numpy as np, pandas as pd
sys.path.insert(0, str(__import__("pathlib").Path(__file__).parent))
from matplotlib.collections import PolyCollection
from matplotlib.cm import ScalarMappable
from matplotlib.colors import Normalize
from _cfg import FINAL, RAW, RES, FIG, FOCAL_COUNTY, PROVENANCE, GROW_MONTHS, CRITICAL_MONTHS
from _viz import *

# ---------- load boundaries ---------------------------------------------------
polys={}
for line in open(RAW/"il_county_boundaries.txt"):
    fips,coords = line.strip().split("|")
    polys[fips]=np.array([[float(x) for x in p.split(",")] for p in coords.split()])
print(f"[10] boundaries: {len(polys)} counties, {sum(len(v) for v in polys.values())} vertices")

sen = pd.read_csv(RES/"table7_county_climate_sensitivity.csv",dtype={"fips5":str})
sc  = pd.read_csv(RES/"table8b_scenario_by_county.csv",dtype={"fips5":str})
m   = sc.merge(sen[["fips5","beta_moisture_bu_per_sd","sensitivity_index"]],on="fips5",how="left")
COL = "d_S4 +1C and -10% precip"

def choropleth(ax, values, cmap, vmin, vmax, label):
    verts=[]; vals=[]
    for f,poly in polys.items():
        v = values.get(f, np.nan)
        verts.append(poly); vals.append(v)
    pc=PolyCollection(verts, array=np.array(vals,dtype=float), cmap=cmap,
                      norm=Normalize(vmin,vmax), edgecolors="#ffffff", linewidths=.55)
    ax.add_collection(pc); ax.autoscale_view()
    ax.set_aspect(1/np.cos(np.deg2rad(40)))
    ax.set_xticks([]); ax.set_yticks([])
    for s in ax.spines.values(): s.set_visible(False)
    ax.grid(False)
    return pc

vals = dict(zip(m.fips5, m[COL]))
foc  = m.loc[m.county==FOCAL_COUNTY, COL].iloc[0]
f,ax=plt.subplots(figsize=(8.4,10.6),dpi=200); f.patch.set_facecolor(SURFACE); ax.set_facecolor(SURFACE)
lim=max(abs(m[COL].min()),abs(m[COL].max()))
pc=choropleth(ax, vals, DIV, -lim, lim, COL)
# outline focal county
fp=polys.get("17019")
if fp is not None:
    ax.plot(np.append(fp[:,0],fp[0,0]),np.append(fp[:,1],fp[0,1]),color="#111111",lw=2.2,zorder=5)
    cx,cy=fp[:,0].mean(),fp[:,1].mean()
    ax.annotate(f"{FOCAL_COUNTY}\n{foc:+.2f} bu/acre",xy=(cx,cy),xytext=(cx-2.95,cy+1.15),
        fontsize=10,color=INK,fontweight="medium",
        bbox=dict(boxstyle="round,pad=.32",fc=SURFACE,ec="#111111",lw=1.0),
        arrowprops=dict(arrowstyle="->",color="#111111",lw=1.3),zorder=6)
cb=f.colorbar(pc,ax=ax,fraction=.036,pad=.02,shrink=.62)
cb.set_label("Change in predicted yield (bu/acre)",fontsize=10,color=INK2)
cb.ax.tick_params(colors=MUTED,labelsize=9); cb.outline.set_visible(False)
ax.text(0,1.045,"Figure 17. Simulated yield change under +1 °C and -10% precipitation",
        transform=ax.transAxes,fontsize=14.2,color=INK,va="bottom",fontweight="semibold")
ax.text(0,1.008,"Sensitivity experiment, not a climate projection. 91 counties in the balanced panel; 11 counties without sufficient data are unshaded.",
        transform=ax.transAxes,fontsize=9.4,color=INK2,va="bottom")
ax.text(1,-.02,SRC,transform=ax.transAxes,fontsize=8,color=MUTED,ha="right",va="top")
f.tight_layout(); f.savefig(FIG/"fig17_scenario_map.png",facecolor=SURFACE,bbox_inches="tight"); plt.close(f)
print("   figure -> fig17_scenario_map.png")

# bonus companion map: sensitivity
f,ax=plt.subplots(figsize=(8.4,10.6),dpi=200); f.patch.set_facecolor(SURFACE); ax.set_facecolor(SURFACE)
sv=dict(zip(m.fips5,m.beta_moisture_bu_per_sd))
pc=choropleth(ax,sv,SEQ,float(m.beta_moisture_bu_per_sd.min()),float(m.beta_moisture_bu_per_sd.max()),"")
if fp is not None:
    ax.plot(np.append(fp[:,0],fp[0,0]),np.append(fp[:,1],fp[0,1]),color="#e34948",lw=2.4,zorder=5)
cb=f.colorbar(pc,ax=ax,fraction=.036,pad=.02,shrink=.62)
cb.set_label("bu/acre per SD of August Palmer Z-index",fontsize=10,color=INK2)
cb.ax.tick_params(colors=MUTED,labelsize=9); cb.outline.set_visible(False)
ax.text(0,1.045,"Figure 18. County sensitivity to August moisture",transform=ax.transAxes,
        fontsize=14.2,color=INK,va="bottom",fontweight="semibold")
ax.text(0,1.008,f"Yield response to a one-standard-deviation moisture anomaly. {FOCAL_COUNTY} outlined in red.",
        transform=ax.transAxes,fontsize=9.4,color=INK2,va="bottom")
f.tight_layout(); f.savefig(FIG/"fig18_sensitivity_map.png",facecolor=SURFACE,bbox_inches="tight"); plt.close(f)
print("   figure -> fig18_sensitivity_map.png")

# ---------- final dataset -----------------------------------------------------
d=pd.read_csv(FINAL/"soybean_illinois_climate_1980_2025.csv",dtype={"county_ansi":str,"fips5":str})
print(f"[10] final dataset: {d.shape[0]:,} rows x {d.shape[1]} cols")
prof=[]
for c in d.columns:
    s=d[c]; num=pd.api.types.is_numeric_dtype(s)
    prof.append(dict(column=c,dtype="number" if num else "text",non_null=int(s.notna().sum()),
        nulls=int(s.isna().sum()),distinct=int(s.nunique()),
        min=round(float(s.min()),3) if num and s.notna().any() else "",
        max=round(float(s.max()),3) if num and s.notna().any() else "",
        example=str(s.dropna().iloc[0])[:24] if s.notna().any() else ""))
pd.DataFrame(prof).to_csv(RES/"column_profile_final.csv",index=False)
json.dump(dict(provenance=PROVENANCE,growing_season=GROW_MONTHS,critical_window=CRITICAL_MONTHS,
   rows=int(d.shape[0]),cols=int(d.shape[1]),counties=int(d.county.nunique()),
   focal=FOCAL_COUNTY),open(RES/"10_final_dataset_manifest.json","w"),indent=2)
print("[10] manifest + column profile written")
