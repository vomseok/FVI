#!/usr/bin/env python3
"""Step 7 - Weight and fuel-score sensitivity of the AUC (vs satellite burn)."""
import numpy as np, rasterio
from sklearn.metrics import roc_auc_score
topo = rasterio.open("topography.tif").read(1); met = rasterio.open("meteorology.tif").read(1)
fuel = rasterio.open("fuel.tif").read(1)
burn = np.load("burn.npy"); cover = np.load("cover.npy")
m = cover & np.isfinite(fuel) & np.isfinite(topo) & np.isfinite(met)
y = burn[m].astype(int)
def auc(wt, wm, wf, p=0.0):
    fu = np.clip(fuel*(1+p), 0, 100)
    return roc_auc_score(y, (wt*topo+wm*met+wf*fu)[m])
print("Weight scenarios:")
for nm, w in [("base 30/30/40",(.30,.30,.40)),("terrain/weather 35/35/30",(.35,.35,.30)),
              ("fuel 25/25/50",(.25,.25,.50))]:
    print(f"  {nm:26} AUC={auc(*w):.3f}")
print("Fuel perturbation (base weights):")
for p in (-.10,-.05,0.,.05,.10):
    print(f"  {p:+.0%}: AUC={auc(.30,.30,.40,p):.3f}")
