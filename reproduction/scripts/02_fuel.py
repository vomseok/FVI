#!/usr/bin/env python3
"""Step 2 - Fuel factor (0-100) from MOE mid-level land-cover map.

Input : directory of MOE mid-level (중분류) land-cover sheets. Each sheet is a
        shapefile in EPSG:5186 with field 'L2_CODE' (22 classes). Tested with
        '토지피복_2025 중분류_경북' (SG04_*.zip, 162 sheets; 72 intersect the grid).
Output: fuel.tif (0-100 relative flammability, EPSG:5186, 3233x3033)

NOTE: scores come from config/fuel_scores_corrected.csv, aligned to the ACTUAL
MOE mid-level code scheme (fixes the earlier mis-mapping of bare-land/water codes
610/620/710/720 and the missing 160/240/250).
"""
import argparse, os, glob, zipfile, tempfile, shutil, csv
import numpy as np, geopandas as gpd, rasterio
from rasterio.transform import from_origin
from rasterio.features import rasterize
from rasterio.enums import MergeAlg

W, H, RES = 3233, 3033, 30.0
GT = from_origin(326000.0, 481000.0, RES, RES)

def load_scores(path):
    s = {}
    with open(path, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            s[int(r["class_code"])] = float(r["flammability_0_100"])
    return s

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sheets-dir", required=True, help="dir with land-cover sheet .zip or extracted .shp")
    ap.add_argument("--scores", default="../config/fuel_scores_corrected.csv")
    ap.add_argument("--out", default="fuel.tif")
    a = ap.parse_args()
    scores = load_scores(a.scores)

    fuel = np.full((H, W), np.nan, "float32")
    zips = sorted(glob.glob(os.path.join(a.sheets_dir, "*.zip")))
    shps = sorted(glob.glob(os.path.join(a.sheets_dir, "**", "*.shp"), recursive=True))
    tmp = tempfile.mkdtemp()
    def burn(shp):
        g = gpd.read_file(shp)[["L2_CODE", "geometry"]]
        g = g[g.geometry.notna()].copy()
        g["s"] = g["L2_CODE"].astype(int).map(scores)
        g = g[g["s"].notna()]
        if len(g):
            rasterize(list(zip(g.geometry, g["s"].astype("float32"))),
                      out=fuel, transform=GT, merge_alg=MergeAlg.replace)
    for z in zips:
        d = os.path.join(tmp, "s"); os.makedirs(d, exist_ok=True)
        with zipfile.ZipFile(z) as zf: zf.extractall(d)
        for shp in glob.glob(d+"/*.shp"): burn(shp)
        shutil.rmtree(d)
    for shp in shps: burn(shp)
    shutil.rmtree(tmp)

    cov = np.isfinite(fuel)
    print("coverage %.1f%%" % (cov.mean()*100))
    fuel = np.where(cov, fuel, np.nanmean(fuel)).astype("float32")
    prof = dict(driver="GTiff", height=H, width=W, count=1, dtype="float32",
                crs="EPSG:5186", transform=GT, nodata=np.nan, compress="deflate")
    with rasterio.open(a.out, "w", **prof) as d: d.write(fuel, 1)
    print("saved", a.out)

if __name__ == "__main__":
    main()
