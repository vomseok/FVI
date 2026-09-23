#!/usr/bin/env python3
"""Step 1 - Topography factor (0-100) on the analysis grid.

Input : national DEM (ArcInfo GRID or GeoTIFF). Tested with NGII '전국DEM'
        (EPSG:5174, Bessel Modified Central Belt, 30 m) -> reprojected to EPSG:5186.
Output: topography.tif  (0-100, EPSG:5186, 3233x3033, 30 m)

Method (manuscript): slope (Sobel), aspect (arctan2, max at south 180 deg),
elevation; each min-max normalized 0-100; AHP weighted sum 0.50/0.30/0.20.
"""
import argparse, numpy as np, rasterio
from rasterio.transform import from_origin
from rasterio.warp import reproject, Resampling
from rasterio.crs import CRS
from scipy.ndimage import convolve

W, H, RES = 3233, 3033, 30.0
GT = from_origin(326000.0, 481000.0, RES, RES)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dem", required=True, help="national DEM path (AIG dir or tif)")
    ap.add_argument("--src-epsg", type=int, default=5174, help="DEM CRS (전국DEM = 5174)")
    ap.add_argument("--out", default="topography.tif")
    a = ap.parse_args()

    src = rasterio.open(a.dem)
    dem = np.full((H, W), np.nan, "float32")
    reproject(rasterio.band(src, 1), dem,
              src_crs=CRS.from_epsg(a.src_epsg), src_transform=src.transform,
              dst_crs=CRS.from_epsg(5186), dst_transform=GT,
              src_nodata=src.nodata, dst_nodata=np.nan, resampling=Resampling.bilinear)

    z = np.where(np.isfinite(dem), dem, np.nanmean(dem)).astype("float64")
    kx = np.array([[-1,0,1],[-2,0,2],[-1,0,1]], float)/(8*RES)
    ky = np.array([[-1,-2,-1],[0,0,0],[1,2,1]], float)/(8*RES)
    dzdx, dzdy = convolve(z, kx, mode="nearest"), convolve(z, ky, mode="nearest")
    slope = np.degrees(np.arctan(np.hypot(dzdx, dzdy)))
    aspect = (90.0 - np.degrees(np.arctan2(dzdy, -dzdx))) % 360.0

    valid = np.isfinite(dem)
    def nrm(x):
        lo, hi = np.nanpercentile(x[valid], 0.5), np.nanpercentile(x[valid], 99.5)
        return np.clip((x-lo)/(hi-lo), 0, 1)*100.0
    slope_n, elev_n = nrm(slope), nrm(dem)
    aspect_n = np.where(slope < 0.5, 0.0, (np.cos(np.radians(aspect-180.0))+1)/2*100.0)

    topo = np.where(valid, 0.50*slope_n + 0.30*aspect_n + 0.20*elev_n, np.nan).astype("float32")
    prof = dict(driver="GTiff", height=H, width=W, count=1, dtype="float32",
                crs=CRS.from_epsg(5186), transform=GT, nodata=np.nan, compress="deflate")
    with rasterio.open(a.out, "w", **prof) as d:
        d.write(topo, 1)
    print("saved", a.out)

if __name__ == "__main__":
    main()
