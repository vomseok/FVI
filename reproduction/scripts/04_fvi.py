#!/usr/bin/env python3
"""Step 4 - FVI = 0.30*topography + 0.30*meteorology + 0.40*fuel (AHP weights),
then 5-class Natural Breaks (Jenks) with Goodness-of-Variance-Fit.

Outputs: FVI.tif (0-100), FVI_grade.tif (uint8 1-5), and prints Table 3.
"""
import argparse, numpy as np, rasterio, jenkspy

def gvf(x, bk):
    sdam = ((x-x.mean())**2).sum(); sdcm = 0.0
    for i in range(len(bk)-1):
        m = (x >= bk[i]) & (x <= bk[i+1]) if i == len(bk)-2 else (x >= bk[i]) & (x < bk[i+1])
        if m.sum(): sdcm += ((x[m]-x[m].mean())**2).sum()
    return 1 - sdcm/sdam

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--topo", default="topography.tif")
    ap.add_argument("--met", default="meteorology.tif")
    ap.add_argument("--fuel", default="fuel.tif")
    ap.add_argument("--wt", type=float, default=0.30); ap.add_argument("--wm", type=float, default=0.30)
    ap.add_argument("--wf", type=float, default=0.40)
    a = ap.parse_args()
    topo = rasterio.open(a.topo).read(1); met = rasterio.open(a.met).read(1)
    fuel = rasterio.open(a.fuel).read(1); prof = rasterio.open(a.fuel).profile
    fvi = (a.wt*topo + a.wm*met + a.wf*fuel).astype("float32")
    valid = np.isfinite(fvi); v = fvi[valid]
    with rasterio.open("FVI.tif", "w", **prof) as d:
        d.write(np.where(valid, fvi, np.nan).astype("float32"), 1)
    rng = np.random.default_rng(20250322)
    samp = rng.choice(v, size=min(60000, v.size), replace=False)
    bk = np.array(jenkspy.jenks_breaks(samp, n_classes=5)); bk[0], bk[-1] = v.min(), v.max()
    print("Jenks breaks:", [round(float(b),1) for b in bk], "GVF=%.4f" % gvf(v, bk))
    grade = np.zeros(fvi.shape, "uint8")
    names = ["Very Low","Low","Moderate","High","Very High"]
    tot = valid.sum()
    for i in range(5):
        m = valid & (fvi >= bk[i]) & (fvi <= bk[i+1] if i == 4 else fvi < bk[i+1])
        grade[m] = i+1
        print(f"Grade {i+1} ({names[i]:9}) {bk[i]:.1f}-{bk[i+1]:.1f}: {m.sum()/tot*100:.1f}%")
    gp = prof.copy(); gp.update(dtype="uint8", nodata=0)
    with rasterio.open("FVI_grade.tif", "w", **gp) as d:
        d.write(np.where(valid, grade, 0).astype("uint8"), 1)
    print("saved FVI.tif, FVI_grade.tif")

if __name__ == "__main__":
    main()
