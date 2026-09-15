#!/usr/bin/env python3
"""Resolution and burn-boundary tolerance validation for empirical FVI rasters."""
from __future__ import annotations
import argparse, csv, json
from pathlib import Path
import numpy as np
import rasterio
from rasterio.enums import Resampling
from rasterio.features import rasterize
import geopandas as gpd
from sklearn.metrics import roc_auc_score, average_precision_score

def read(path):
    with rasterio.open(path) as src:
        return src.read(1, masked=True).astype('float32'), src.meta.copy()

def auc_metrics(fvi, label):
    mask=(~np.ma.getmaskarray(fvi)) & np.isfinite(np.ma.filled(fvi,np.nan))
    y=label[mask].astype(int); x=np.ma.filled(fvi,np.nan)[mask]
    if len(np.unique(y)) != 2: raise ValueError('Each comparison needs burned and unburned cells')
    return {'valid_cells':int(mask.sum()),'burned_cells':int(y.sum()),'auc_roc':float(roc_auc_score(y,x)),'auc_pr':float(average_precision_score(y,x))}

def resample_to_10m(fvi30, meta30):
    scale=3
    dest=np.empty((meta30['height']*scale,meta30['width']*scale),dtype='float32')
    transform=meta30['transform']*meta30['transform'].scale(1/scale,1/scale)
    with rasterio.MemoryFile() as mem:
        m=meta30.copy(); m.update(dtype='float32',count=1,nodata=-9999.0)
        with mem.open(**m) as ds:
            ds.write(np.ma.filled(fvi30,-9999.0),1)
            ds.read(1,out=dest,resampling=Resampling.bilinear)
    return np.ma.masked_less_equal(dest,-9998.0), {**meta30,'height':dest.shape[0],'width':dest.shape[1],'transform':transform}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--fvi-30m',required=True); ap.add_argument('--burn-polygons',required=True); ap.add_argument('--parameters',default='../config/grid_parameters.json'); ap.add_argument('--out-dir',required=True)
    args=ap.parse_args(); out=Path(args.out_dir); out.mkdir(parents=True,exist_ok=True)
    pars=json.loads(Path(args.parameters).read_text(encoding='utf-8')); fvi30,m30=read(args.fvi_30m); gdf=gpd.read_file(args.burn_polygons).to_crs(m30['crs'])
    rows=[]
    fvi10,m10=resample_to_10m(fvi30,m30)
    for resolution,fvi,meta in [(30,fvi30,m30),(10,fvi10,m10)]:
        burn=rasterize([(g,1) for g in gdf.geometry],out_shape=(meta['height'],meta['width']),transform=meta['transform'],fill=0,dtype='uint8')
        rows.append({'resolution_m':resolution,**auc_metrics(fvi,burn),'interpretation':'10 m is a resampling sensitivity test unless independent 10 m inputs are supplied'})
    with (out/'grid_30m_vs_10m.csv').open('w',newline='',encoding='utf-8') as fh:
        w=csv.DictWriter(fh,fieldnames=rows[0].keys()); w.writeheader(); w.writerows(rows)
    tol=[]
    for meters in pars['boundary_tolerance_m']:
        geom=gdf.geometry.buffer(float(meters)).union_all() if meters else gdf.geometry.union_all()
        burn=rasterize([(geom,1)],out_shape=(m30['height'],m30['width']),transform=m30['transform'],fill=0,dtype='uint8')
        tol.append({'boundary_tolerance_m':meters,**auc_metrics(fvi30,burn)})
    with (out/'boundary_tolerance.csv').open('w',newline='',encoding='utf-8') as fh:
        w=csv.DictWriter(fh,fieldnames=tol[0].keys()); w.writeheader(); w.writerows(tol)
    (out/'metadata.json').write_text(json.dumps({'execution_status':'completed','parameters':pars,'inputs':{'fvi_30m':args.fvi_30m,'burn_polygons':args.burn_polygons}},indent=2)+'\n',encoding='utf-8')
if __name__=='__main__': main()
