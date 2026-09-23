#!/usr/bin/env python3
"""Step 6 - Validate FVI against the satellite burn label (covered area only).

Outputs ROC AUC, Youden operating point, and Table 4 (per-grade damage
concentration ratio). Restricts to the dNBR-covered swath (which contains the
whole burn scar); the un-imaged north/south strips are excluded.
"""
import numpy as np, rasterio
from sklearn.metrics import roc_auc_score, average_precision_score, roc_curve

fvi = rasterio.open("FVI.tif").read(1)
grade = rasterio.open("FVI_grade.tif").read(1)
burn = np.load("burn.npy"); cover = np.load("cover.npy")
m = cover & np.isfinite(fvi)
y = burn[m].astype(int); sc = fvi[m]
auc = roc_auc_score(y, sc); ap = average_precision_score(y, sc)
fpr, tpr, th = roc_curve(y, sc); i = (tpr-fpr).argmax()
print("AUC=%.3f AUC-PR=%.3f Youden thr=%.1f sens=%.3f spec=%.3f"
      % (auc, ap, th[i], tpr[i], 1-fpr[i]))
print("burned %.1f%% of covered area" % (y.mean()*100))
names = ["Very Low","Low","Moderate","High","Very High"]
tb = burn.sum(); ta = (cover & (grade > 0)).sum()
for k in range(1, 6):
    ib = (burn & (grade == k)).sum()/tb*100
    ia = (cover & (grade == k)).sum()/ta*100
    print(f"Grade {k} ({names[k-1]:9}): burn {ib:5.1f}%  area {ia:5.1f}%  conc {ib/ia:.2f}")
