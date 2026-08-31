"""Shared plotting theme. Palette validated with the dataviz six-checks
validator under --pairs all: worst CVD dE 9.2, worst normal-vision dE 24.0."""
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
SURFACE="#fcfcfb"; INK="#0b0b0b"; INK2="#52514e"; MUTED="#8c8b85"; GRID="#e3e2dc"
S1="#2a78d6"; S2="#eb6834"; S3="#1baf7a"; S4="#eda100"; FOCAL="#e34948"
DIV=LinearSegmentedColormap.from_list("rwb",["#e34948","#ef8b8a","#f0efec","#7ba9e4","#2a78d6"])
SEQ=LinearSegmentedColormap.from_list("blues",["#eaf1fb","#9cc0ea","#4a8dd9","#1c5296","#0d2b52"])
def fig(w=11,h=6.5,dpi=200):
    f,ax=plt.subplots(figsize=(w,h),dpi=dpi); f.patch.set_facecolor(SURFACE); ax.set_facecolor(SURFACE)
    return f,ax
def style(ax,title=None,sub=None,xl=None,yl=None,legend=False,src=None):
    for s in ("top","right"): ax.spines[s].set_visible(False)
    for s in ("left","bottom"): ax.spines[s].set_color("#d9d8d2"); ax.spines[s].set_linewidth(.8)
    ax.tick_params(colors=MUTED,labelsize=9,length=3,width=.8)
    ax.grid(axis="y",color=GRID,lw=.7,alpha=.9); ax.set_axisbelow(True)
    if xl: ax.set_xlabel(xl,fontsize=10.5,color=INK2,labelpad=9)
    if yl: ax.set_ylabel(yl,fontsize=10.5,color=INK2,labelpad=9)
    y=1.055 if sub else 1.02
    if title: ax.text(0,y,title,transform=ax.transAxes,fontsize=14.5,color=INK,va="bottom",fontweight="semibold")
    if sub: ax.text(0,1.012,sub,transform=ax.transAxes,fontsize=9.6,color=INK2,va="bottom")
    if src: ax.text(1,-.155,src,transform=ax.transAxes,fontsize=8,color=MUTED,ha="right",va="top")
    if legend: ax.legend(frameon=True,fontsize=9.5,facecolor=SURFACE,edgecolor=GRID,labelcolor=INK2)
def save(f,path):
    f.tight_layout(); f.savefig(path,facecolor=SURFACE,bbox_inches="tight"); plt.close(f)
    print(f"   figure -> {path.name}")
SRC="Source: USDA NASS Quick Stats; NOAA NCEI nClimDiv"
