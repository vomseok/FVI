#!/usr/bin/env python3
"""Scenario sensitivity analysis for FVI weights and fuel-score perturbations.

Run only with documented, co-registered real rasters and a rasterized burn label.
The script writes empirical results and never fills unavailable outcomes.
"""
from __future__ import annotations
import argparse, csv, json
from pathlib import Path
import numpy as np
import rasterio
from sklearn.metrics import roc_auc_score, average_precision_score, roc_curve
from fvi_calculation import compute_fvi, load_weights, write_raster

def read_label(path, ref_meta):
    with rasterio.open(path) as src:
        a = src.read(1, masked=True)
        if any(src.meta[k] != ref_meta[k] for k in ('crs','transform','height','width')):
            raise ValueError('Burn label raster is not aligned to factor rasters')
    return np.ma.filled(a, 0).astype(np.uint8)

def metric(y, score):
    auc = float(roc_auc_score(y, score))
    pr = float(average_precision_score(y, score))
    fpr, tpr, thresholds = roc_curve(y, score)
    j = tpr - fpr
    i = int(np.argmax(j))
    return {'auc_roc': auc, 'auc_pr': pr, 'youden_threshold': float(thresholds[i]), 'sensitivity': float(tpr[i]), 'specificity': float(1-fpr[i]), 'youden_j': float(j[i])}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--topography', required=True); ap.add_argument('--meteorology', required=True); ap.add_argument('--fuel', required=True)
    ap.add_argument('--burn-label', required=True); ap.add_argument('--scenario-config', default='../config/scenarios.json')
    ap.add_argument('--out-dir', required=True); ap.add_argument('--fuel-perturbation', type=float, default=0.0, help='Fractional multiplier, e.g. 0.10 for +10%% fuel sensitivity')
    args = ap.parse_args(); out = Path(args.out_dir); out.mkdir(parents=True, exist_ok=True)
    cfg = json.loads(Path(args.scenario_config).read_text(encoding='utf-8'))
    records=[]
    for scenario in cfg['scenarios']:
        weights=load_weights(args.scenario_config, scenario['scenario_id'])
        fvi, meta=compute_fvi(args.topography,args.meteorology,args.fuel,weights)
        if args.fuel_perturbation:
            # Fuel perturbation is bounded 0–100 and reruns the complete weighted sum.
            with rasterio.open(args.fuel) as src: fuel=src.read(1,masked=True).astype('float32')
            adjusted=np.clip(fuel*(1+args.fuel_perturbation),0,100)
            arrays=[]
            for p in (args.topography,args.meteorology):
                with rasterio.open(p) as src: arrays.append(src.read(1,masked=True).astype('float32'))
            fvi=np.ma.masked_invalid(weights['topography']*arrays[0]+weights['meteorology']*arrays[1]+weights['fuel']*adjusted)
        burn=read_label(args.burn_label, meta)
        mask=(~np.ma.getmaskarray(fvi)) & np.isfinite(np.ma.filled(fvi,np.nan))
        y=burn[mask].astype(int); score=np.ma.filled(fvi,np.nan)[mask]
        if len(np.unique(y)) != 2: raise ValueError('Burn label must contain both burned and unburned valid cells')
        m=metric(y,score)
        record={'scenario_id':scenario['scenario_id'],'scenario_name':scenario['name'],'fuel_perturbation_fraction':args.fuel_perturbation,**weights,'valid_cells':int(mask.sum()),'burned_cells':int(y.sum()),**m}
        records.append(record)
        write_raster(fvi,meta,out/f"{scenario['scenario_id']}_fvi.tif")
        with (out/f"{scenario['scenario_id']}_results.csv").open('w',newline='',encoding='utf-8') as fh:
            w=csv.DictWriter(fh,fieldnames=record.keys()); w.writeheader(); w.writerow(record)
    (out/'summary_statistics.json').write_text(json.dumps({'execution_status':'completed','records':records},indent=2)+'\n',encoding='utf-8')

if __name__=='__main__': main()
