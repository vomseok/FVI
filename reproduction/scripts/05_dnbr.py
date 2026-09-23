#!/usr/bin/env python3
"""Step 5 - Satellite burn severity/perimeter from Sentinel-2 dNBR.

Input : two Sentinel-2 L2A scenes (Copernicus Browser 'Analytical' GeoTIFF),
        pre-fire and post-fire, each providing B08 (NIR) and B12 (SWIR).
        Tested: pre 2025-03-14, post 2025-04-08 (both EPSG:4326).
Output: dNBR.tif, burn_severity.tif (Key&Benson 6-class), burn_perimeter.tif
        (1 burned / 0 unburned / 255 no-data), reprojected to the EPSG:5186 grid.

NBR = (B08-B12)/(B08+B12); dNBR = (NBR_pre - NBR_post)*1000.
Burn core = dNBR>=270 (moderate-low+) & connected component >= 9 ha
(robust to spring green-up between the two dates).
"""
import argparse, glob, numpy as np, rasterio
from rasterio.warp import reproject, Resampling
from rasterio.transform import from_origin
from rasterio.crs import CRS
from scipy import ndimage

W, H, RES = 3233, 3033, 30.0
GT = from_origin(326000.0, 481000.0, RES, RES); DST = CRS.from_epsg(5186)

def nbr(scene_dir):
    b08 = rasterio.open(glob.glob(f"{scene_dir}/*_B08_*.tif*")[0])
    b12 = rasterio.open(glob.glob(f"{scene_dir}/*_B12_*.tif*")[0])
    a, s = b08.read(1).astype("float32"), b12.read(1).astype("float32")
    den = a+s; den[den == 0] = np.nan
    n = (a-s)/den; n[(a == 0) | (s == 0)] = np.nan
    return n, b08.transform, b08.crs

def to_grid(arr, tr, crs):
    out = np.full((H, W), np.nan, "float32")
    reproject(arr, out, src_transform=tr, src_crs=crs, dst_transform=GT, dst_crs=DST,
              src_nodata=np.nan, dst_nodata=np.nan, resampling=Resampling.bilinear)
    return out

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pre", required=True, help="dir with pre-fire B08/B12 tiffs")
    ap.add_argument("--post", required=True, help="dir with post-fire B08/B12 tiffs")
    ap.add_argument("--core-thr", type=float, default=270)
    ap.add_argument("--min-ha", type=float, default=9)
    a = ap.parse_args()
    np0, t0, c0 = nbr(a.pre); np1, t1, c1 = nbr(a.post)
    dnbr = (to_grid(np0, t0, c0) - to_grid(np1, t1, c1))*1000.0
    cover = np.isfinite(dnbr)
    sev = np.zeros((H, W), "uint8")
    for lo, hi, v in [(-9e9,-100,1),(-100,100,2),(100,270,3),(270,440,4),(440,660,5),(660,9e9,6)]:
        sev[cover & (dnbr >= lo) & (dnbr < hi)] = v
    core = cover & (dnbr >= a.core_thr)
    lab, n = ndimage.label(core)
    sizes = ndimage.sum(np.ones_like(lab), lab, range(1, n+1))
    keep = np.where(sizes >= a.min_ha*1e4/900)[0]+1
    burn = ndimage.binary_closing(np.isin(lab, keep), np.ones((3,3))) & cover
    prof = dict(driver="GTiff", height=H, width=W, count=1, crs=DST, transform=GT, compress="deflate")
    with rasterio.open("dNBR.tif","w",dtype="float32",nodata=np.nan,**prof) as d:
        d.write(np.where(cover, dnbr, np.nan).astype("float32"), 1)
    with rasterio.open("burn_severity.tif","w",dtype="uint8",nodata=0,**prof) as d: d.write(sev, 1)
    with rasterio.open("burn_perimeter.tif","w",dtype="uint8",nodata=255,**prof) as d:
        d.write(np.where(cover, burn.astype("uint8"), 255).astype("uint8"), 1)
    np.save("cover.npy", cover); np.save("burn.npy", burn); np.save("dnbr.npy", dnbr)
    print("burn %.0f ha / covered %.0f ha" % (burn.sum()*900/1e4, cover.sum()*900/1e4))
    print("saved dNBR.tif, burn_severity.tif, burn_perimeter.tif")

if __name__ == "__main__":
    main()
