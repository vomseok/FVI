#!/usr/bin/env python3
"""Step 3 - Meteorology factor (0-100) from KMA ASOS daily observations.

Input : KMA ASOS daily CSV (기상자료개방포털 'OBS_ASOS_DD', cp949) covering the
        fire week plus antecedent days (tested 2025-03-01..2025-03-28).
        Station coordinates from config/station_coords.csv.
Output: meteorology.tif (0-100, EPSG:5186, 3233x3033)

Method: per-station fire-week (2025-03-22..28) means of effective humidity
(실효습도, r=0.7 decay), wind speed, temperature -> IDW (power 2) to the grid ->
each normalized 0-100 (humidity inverted: dry=high) -> AHP sum 0.40/0.40/0.20.
"""
import argparse, numpy as np, pandas as pd, rasterio
from rasterio.transform import from_origin
from pyproj import Transformer

W, H, RES = 3233, 3033, 30.0
GT = from_origin(326000.0, 481000.0, RES, RES)

def eff_hum(rh_by_date, day, r=0.7, maxlag=20):
    tot = wsum = 0.0
    for n in range(maxlag+1):
        d = day - pd.Timedelta(days=n)
        v = rh_by_date.get(d)
        if v is not None and not np.isnan(v):
            w = r**n; tot += w*v; wsum += w
    return tot/wsum if wsum else np.nan

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--asos-csv", required=True)
    ap.add_argument("--coords", default="../config/station_coords.csv")
    ap.add_argument("--fire-start", default="2025-03-22")
    ap.add_argument("--fire-end", default="2025-03-28")
    ap.add_argument("--out", default="meteorology.tif")
    a = ap.parse_args()

    df = pd.read_csv(a.asos_csv, encoding="cp949").rename(columns={
        '평균기온(°C)':'T','평균 풍속(m/s)':'Wnd','평균 상대습도(%)':'RH','일시':'d','지점':'id'})
    df['d'] = pd.to_datetime(df['d'])
    co = pd.read_csv(a.coords).set_index('id')
    fire = pd.date_range(a.fire_start, a.fire_end)
    rows = []
    for sid, g in df.groupby('id'):
        if sid not in co.index: continue
        g = g.sort_values('d'); rh = dict(zip(g['d'], g['RH']))
        He = np.nanmean([eff_hum(rh, d) for d in fire])
        sub = g[g['d'].isin(fire)]
        rows.append(dict(lat=co.loc[sid,'lat'], lon=co.loc[sid,'lon'],
                         EH=He, Wnd=sub['Wnd'].mean(), T=sub['T'].mean()))
    st = pd.DataFrame(rows)
    tr = Transformer.from_crs(4326, 5186, always_xy=True)
    st['x'], st['y'] = tr.transform(st['lon'].values, st['lat'].values)

    xs = 326000 + (np.arange(W)+0.5)*RES
    ys = 481000 - (np.arange(H)+0.5)*RES
    X, Y = np.meshgrid(xs, ys)
    def idw(v, p=2):
        num = den = 0.0
        for xi, yi, vi in zip(st['x'], st['y'], v):
            d2 = (X-xi)**2 + (Y-yi)**2; d2[d2 < 1] = 1
            w = 1.0/d2**(p/2); num = num + w*vi; den = den + w
        return num/den
    EHg, Wg, Tg = idw(st['EH'].values), idw(st['Wnd'].values), idw(st['T'].values)
    def nrm(x):
        lo, hi = np.percentile(x, 0.5), np.percentile(x, 99.5)
        return np.clip((x-lo)/(hi-lo), 0, 1)*100
    met = (0.40*(100-nrm(EHg)) + 0.40*nrm(Wg) + 0.20*nrm(Tg)).astype("float32")
    prof = dict(driver="GTiff", height=H, width=W, count=1, dtype="float32",
                crs="EPSG:5186", transform=GT, nodata=np.nan, compress="deflate")
    with rasterio.open(a.out, "w", **prof) as d: d.write(met, 1)
    print("saved", a.out)

if __name__ == "__main__":
    main()
