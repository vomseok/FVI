#!/usr/bin/env python3
"""Step 8 - Forest type (수종) x burn-severity overlay.

Forest classes are read from fuel.tif by their unique flammability score
(100=coniferous, 80=mixed, 60=broadleaf). Reports per-type area, burned area,
burn rate, mean dNBR, and share of total damage - empirical support for the
fuel ranking (coniferous >> mixed > broadleaf).
"""
import numpy as np, rasterio
fuel = rasterio.open("fuel.tif").read(1)
burn = np.load("burn.npy"); cover = np.load("cover.npy"); dnbr = np.load("dnbr.npy")
covm = cover & np.isfinite(dnbr); tb = burn[covm].sum()
print(f"{'Type':11}{'area_ha':>10}{'burned_ha':>11}{'rate%':>8}{'meanDNBR':>10}{'dmg%':>8}")
for code, nm in [(100,"Coniferous"),(80,"Mixed"),(60,"Broadleaf")]:
    cls = covm & (np.abs(fuel-code) < 1e-3)
    b = cls & burn
    print(f"{nm:11}{cls.sum()*900/1e4:10.0f}{b.sum()*900/1e4:11.0f}"
          f"{b.sum()/cls.sum()*100:8.1f}{np.nanmean(dnbr[cls]):10.0f}{b.sum()/tb*100:8.1f}")
nf = covm & ~np.isin(np.round(fuel), [100, 80, 60])
b = nf & burn
print(f"{'Non-forest':11}{nf.sum()*900/1e4:10.0f}{b.sum()*900/1e4:11.0f}"
      f"{b.sum()/nf.sum()*100:8.1f}{np.nanmean(dnbr[nf]):10.0f}{b.sum()/tb*100:8.1f}")
