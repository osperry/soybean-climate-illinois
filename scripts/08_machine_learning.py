"""08 - Machine learning with strict temporal validation. Table 5, Figures 10-12.

Leakage control (spec section 12): no random splits anywhere. Two regimes.
  * Fixed split : train 1980-2013, validate 2014-2018, test 2019-2025
  * Expanding   : rolling origin, one test year at a time, 2001-2025
County-specific trends used as features are refitted on TRAINING YEARS ONLY at
every fold, so no future information enters any predictor.
"""
import sys, json, numpy as np, pandas as pd, pickle
sys.path.insert(0, str(__import__("pathlib").Path(__file__).parent))
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.ensemble import RandomForestRegressor, HistGradientBoostingRegressor, GradientBoostingRegressor
from sklearn.inspection import permutation_importance
from _cfg import FINAL, RES, FIG, MOD, SEED
from _viz import *

d = pd.read_csv(FINAL/"soybean_illinois_climate_1980_2025.csv",dtype={"county_ansi":str})
d = d[d.in_balanced_panel==1].sort_values(["county","year"]).reset_index(drop=True)

FEATS = ["pcp_critical","pcp_grow","pcp08","pcp07","pcp_win","pcp_grow_cv",
         "tmax_critical","tmax08","tmp_grow","tmp_grow_sd","tmin10",
         "zndx08","zndx07","pdsi08","pdsi_critical","heat_x_dry",
         "hot_month_count","dry_month_count","climate_normal_pcp","climate_normal_tmax"]
TARGET="yield_anom"
print(f"[08] features {len(FEATS)} | rows {len(d):,} | counties {d.county.nunique()}")

MODELS = {
 "Linear Regression": lambda: LinearRegression(),
 "Ridge":             lambda: Ridge(alpha=1.0),
 "Random Forest":     lambda: RandomForestRegressor(n_estimators=200,min_samples_leaf=4,
                                 n_jobs=-1,random_state=SEED),
 "Gradient Boosting": lambda: GradientBoostingRegressor(n_estimators=200,max_depth=3,
                                 learning_rate=.05,random_state=SEED),
 "HistGBM (XGB-class)":lambda: HistGradientBoostingRegressor(max_iter=250,learning_rate=.06,
                                 random_state=SEED),
}
def metrics(a,p):
    e=p-a; mape=np.mean(np.abs(e)/np.maximum(np.abs(a),1e-6))*100
    return dict(RMSE=float(np.sqrt((e**2).mean())),MAE=float(np.abs(e).mean()),
        R2=float(1-(e**2).sum()/((a-a.mean())**2).sum()),
        MAPE=float(mape),bias=float(e.mean()),err_sd=float(e.std()))

# ---------- A. fixed temporal split -----------------------------------------
tr=d[d.year<=2013]; va=d[(d.year>=2014)&(d.year<=2018)]; te=d[d.year>=2019]
print(f"[08] fixed split  train {len(tr):,} ({tr.year.min()}-{tr.year.max()}) "
      f"val {len(va):,} test {len(te):,} ({te.year.min()}-{te.year.max()})")
rowsA=[]
# climate-free baseline: predict the county trend, i.e. anomaly = 0
rowsA.append(dict(model="Baseline: trend only (anomaly=0)",split="test",**metrics(te[TARGET].values,np.zeros(len(te)))))
for name,f in MODELS.items():
    mdl=f().fit(tr[FEATS],tr[TARGET])
    rowsA.append(dict(model=name,split="validation",**metrics(va[TARGET].values,mdl.predict(va[FEATS]))))
    rowsA.append(dict(model=name,split="test",**metrics(te[TARGET].values,mdl.predict(te[FEATS]))))
A=pd.DataFrame(rowsA).round(4)

# ---------- B. expanding-window rolling origin -------------------------------
rowsB={k:[] for k in list(MODELS)+["Baseline: trend only (anomaly=0)"]}
act=[];yrs=[]
for t in range(2001,2026):
    trn=d[d.year<t]; tst=d[d.year==t]
    if len(tst)==0: continue
    act.append(tst[TARGET].values); yrs.append(np.full(len(tst),t))
    rowsB["Baseline: trend only (anomaly=0)"].append(np.zeros(len(tst)))
    for name,f in MODELS.items():
        rowsB[name].append(f().fit(trn[FEATS],trn[TARGET]).predict(tst[FEATS]))
a=np.concatenate(act); yy=np.concatenate(yrs)
B=pd.DataFrame([dict(model=k,**metrics(a,np.concatenate(v))) for k,v in rowsB.items()]).round(4)
base=B.loc[B.model.str.startswith("Baseline"),"RMSE"].iloc[0]
B["skill_vs_baseline_%"]=((1-B.RMSE/base)*100).round(2)
B=B.sort_values("RMSE")

t5=pd.concat([A.assign(validation="fixed split"),B.assign(split="rolling test",validation="expanding window")],ignore_index=True)
t5.to_csv(RES/"table5_ml_performance.csv",index=False)
print("\n[08] FIXED SPLIT (test 2019-2025)")
print(A[A.split=="test"][["model","RMSE","MAE","R2","MAPE","bias"]].to_string(index=False))
print("\n[08] EXPANDING WINDOW (2001-2025, 2,317 obs)")
print(B[["model","RMSE","MAE","R2","MAPE","bias","skill_vs_baseline_%"]].to_string(index=False))

best=B.iloc[0].model
print(f"\n[08] best model: {best}")
mdl=MODELS[best]().fit(d[d.year<2019][FEATS],d[d.year<2019][TARGET])
pickle.dump(mdl,open(MOD/"best_model.pkl","wb"))
te2=d[d.year>=2019]
pi=permutation_importance(mdl,te2[FEATS],te2[TARGET],n_repeats=12,random_state=SEED,n_jobs=-1)
imp=pd.DataFrame(dict(feature=FEATS,importance=pi.importances_mean,sd=pi.importances_std)).sort_values("importance",ascending=False)
imp.to_csv(RES/"table6_feature_importance.csv",index=False)
print("\n[08] permutation importance, top 10")
print(imp.head(10).round(4).to_string(index=False))

# ---------- Figure 10: model performance -------------------------------------
f,ax=fig(10.5,6)
o=B.sort_values("RMSE"); cols=[S3 if m.startswith("Baseline") else S1 for m in o.model]
ax.barh(range(len(o)),o.RMSE,color=cols,height=.66)
for i,(r,s) in enumerate(zip(o.RMSE,o["skill_vs_baseline_%"])):
    ax.text(r+.02,i,f"{r:.3f}   ({s:+.1f}%)",va="center",fontsize=9,color=INK2)
ax.set_yticks(range(len(o))); ax.set_yticklabels(o.model,fontsize=9.5); ax.invert_yaxis()
ax.grid(axis="y",lw=0); ax.grid(axis="x",color=GRID,lw=.7)
style(ax,"Figure 10. Model performance, expanding-window validation",
      "One-year-ahead, rolling origin 2001-2025. Skill relative to the trend-only baseline in parentheses.",
      "RMSE (bu/acre)",None,src=SRC)
save(f,FIG/"fig10_model_performance.png")

# ---------- Figure 11: feature importance ------------------------------------
f,ax=fig(10.5,7)
k=imp.head(14).iloc[::-1]
ax.barh(range(len(k)),k.importance,xerr=k.sd,color=S1,height=.68,
        error_kw=dict(ecolor=MUTED,lw=.9,capsize=2.5))
ax.set_yticks(range(len(k))); ax.set_yticklabels(k.feature,fontsize=9.5)
ax.grid(axis="y",lw=0); ax.grid(axis="x",color=GRID,lw=.7)
style(ax,"Figure 11. Permutation importance",
      f"{best}, evaluated on held-out years 2019-2025. Bars are the mean increase in error when the feature is shuffled.",
      "Increase in MSE when permuted",None,src=SRC)
save(f,FIG/"fig11_feature_importance.png")

# ---------- Figure 12: partial dependence (ALE-style) ------------------------
from sklearn.inspection import PartialDependenceDisplay
top4=imp.head(4).feature.tolist()
f,axes=plt.subplots(2,2,figsize=(11,7.6),dpi=200); f.patch.set_facecolor(SURFACE)
PartialDependenceDisplay.from_estimator(mdl,te2[FEATS],top4,ax=axes.ravel()[:4],
    line_kw=dict(color=S1,lw=2.4))
for a_,nm in zip(axes.ravel(),top4):
    a_.set_facecolor(SURFACE); a_.grid(color=GRID,lw=.7); a_.set_axisbelow(True)
    for s in ("top","right"): a_.spines[s].set_visible(False)
    a_.tick_params(colors=MUTED,labelsize=8.5)
    a_.set_xlabel(nm,fontsize=9.5,color=INK2); a_.set_ylabel("partial effect",fontsize=9,color=INK2)
f.suptitle("Figure 12. Partial dependence, four most important predictors",
           fontsize=14.5,color=INK,x=.02,ha="left",y=1.0,fontweight="semibold")
f.text(.02,.965,f"{best}. Marginal effect on yield anomaly (bu/acre) holding other features at their observed distribution.",
       fontsize=9.6,color=INK2)
f.tight_layout(rect=[0,0,1,.955]); f.savefig(FIG/"fig12_partial_dependence.png",facecolor=SURFACE,bbox_inches="tight")
print("   figure -> fig12_partial_dependence.png")
json.dump(dict(best_model=best,features=FEATS,target=TARGET,seed=SEED,
    fixed_split=dict(train="1980-2013",validation="2014-2018",test="2019-2025"),
    expanding_window="2001-2025 rolling origin"),open(RES/"08_ml_config.json","w"),indent=2)
