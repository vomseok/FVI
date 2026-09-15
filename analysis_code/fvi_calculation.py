#!/usr/bin/env python3
"""Core calculation for the physical fire hazard/susceptibility index.

Inputs must be co-registered 0–100 rasters in EPSG:5186. This script does not
create or infer meteorology, land-cover scores, or burn labels: those inputs
must originate from documented source data.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import numpy as np
import rasterio

FACTORS = ('topography', 'meteorology', 'fuel')

def load_weights(path: str | Path, scenario_id: str) -> dict[str, float]:
    cfg = json.loads(Path(path).read_text(encoding='utf-8'))
    item = next((x for x in cfg['scenarios'] if x['scenario_id'] == scenario_id), None)
    if item is None:
        raise KeyError(f'Unknown scenario_id: {scenario_id}')
    weights = {k: float(v) for k, v in item['weights'].items()}
    if set(weights) != set(FACTORS) or not np.isclose(sum(weights.values()), 1.0):
        raise ValueError(f'Invalid weights: {weights}')
    return weights

def _read(path: str | Path):
    with rasterio.open(path) as src:
        arr = src.read(1, masked=True).astype('float32')
        meta = src.meta.copy()
    return arr, meta

def compute_fvi(topography_path, meteorology_path, fuel_path, weights):
    arrays, metas = zip(*[_read(p) for p in (topography_path, meteorology_path, fuel_path)])
    reference = metas[0]
    for meta in metas[1:]:
        for key in ('crs', 'transform', 'height', 'width'):
            if meta[key] != reference[key]:
                raise ValueError(f'Input rasters are not co-registered: mismatch in {key}')
    for name, arr in zip(FACTORS, arrays):
        valid = arr.compressed()
        if valid.size == 0 or valid.min() < -1e-5 or valid.max() > 100.00001:
            raise ValueError(f'{name} must be a 0–100 normalized raster with valid cells')
    combined_mask = np.ma.getmaskarray(arrays[0]) | np.ma.getmaskarray(arrays[1]) | np.ma.getmaskarray(arrays[2])
    fvi = sum(weights[name] * np.ma.filled(arr, np.nan) for name, arr in zip(FACTORS, arrays))
    fvi = np.ma.masked_array(fvi.astype('float32'), mask=combined_mask | ~np.isfinite(fvi))
    return fvi, reference

def write_raster(array, meta, output_path):
    out_meta = meta.copy()
    out_meta.update(dtype='float32', count=1, nodata=-9999.0, compress='deflate')
    out = np.ma.filled(array, -9999.0)
    with rasterio.open(output_path, 'w', **out_meta) as dst:
        dst.write(out.astype('float32'), 1)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--topography', required=True)
    ap.add_argument('--meteorology', required=True)
    ap.add_argument('--fuel', required=True)
    ap.add_argument('--scenario-config', default='../config/scenarios.json')
    ap.add_argument('--scenario-id', default='scenario_01')
    ap.add_argument('--output', required=True)
    args = ap.parse_args()
    weights = load_weights(args.scenario_config, args.scenario_id)
    fvi, meta = compute_fvi(args.topography, args.meteorology, args.fuel, weights)
    write_raster(fvi, meta, args.output)
    print(json.dumps({'scenario_id': args.scenario_id, 'weights': weights, 'valid_cells': int(fvi.count()), 'min': float(fvi.min()), 'max': float(fvi.max()), 'mean': float(fvi.mean())}, indent=2))

if __name__ == '__main__':
    main()
