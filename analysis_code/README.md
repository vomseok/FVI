# FVI Reproducibility Package

## Purpose

This package implements reproducible sensitivity and validation procedures for the **physical fire hazard/susceptibility** version of the Fire Vulnerability Index (FVI). It does **not** claim to measure IPCC vulnerability or full wildfire risk. Results are valid only after the documented real input rasters, weather observations, and burn-perimeter data are supplied.

> **Current status:** The original factor rasters, raw ASOS/AWS station observations, and the 3,300 ha validation perimeter were not present in the active workspace when this package was assembled. Therefore the CSV/JSON files under `results/` are transparent execution manifests with no fabricated numerical results. They will be overwritten only by an actual execution using documented source data.

## Required inputs (not included)

| Input | Requirement | Example |
|---|---|---|
| `topography.tif` | 0–100 normalized, 30 m, EPSG:5186 | Slope/aspect/elevation composite |
| `meteorology.tif` | 0–100 normalized, 30 m, EPSG:5186 | 2025-03-22 to 2025-03-28 event-period composite, or separately documented winter–spring climatology |
| `fuel.tif` | 0–100 normalized, 30 m, EPSG:5186 | Mid-level land-cover classes mapped via `config/fuel_scores.csv` |
| `burn_label.tif` | Binary 30 m burn label aligned with FVI | Prefer an official or satellite-derived burn scar |
| `burn_perimeter.gpkg` | Burned-land polygons in EPSG:5186 | Used for boundary-tolerance sensitivity |

All inputs must document source, date, preprocessing, coordinate reference system, and no-data treatment. The grid must be aligned before calculating FVI.

## Run sequence

Install dependencies:

```bash
pip install numpy rasterio geopandas scikit-learn
```

Run each weight scenario with the real input data:

```bash
cd analysis_code
python sensitivity_analysis.py \
  --topography ../data/topography.tif \
  --meteorology ../data/meteorology.tif \
  --fuel ../data/fuel.tif \
  --burn-label ../data/burn_label.tif \
  --scenario-config ../config/scenarios.json \
  --out-dir ../results/sensitivity
```

Run grid and boundary validation using the base FVI raster:

```bash
python validation.py \
  --fvi-30m ../results/sensitivity/scenario_01_fvi.tif \
  --burn-polygons ../data/burn_perimeter.gpkg \
  --parameters ../config/grid_parameters.json \
  --out-dir ../results/validation
```

## Interpretation safeguards

* `scenario_01` is the base AHP-documented setting (0.30/0.30/0.40); scenarios 02–03 are pre-specified sensitivity cases, not calibrated alternatives.
* Fuel scores are **relative flammability ranks**, not observed fuel loads, moisture, age, or density. Scores and score bounds must be justified with cited fire-ecology sources before manuscript resubmission.
* A 10 m product generated from 30 m inputs is a **resampling sensitivity analysis**, not independent 10 m information.
* The 2025 event-period meteorology maps event-specific physical hazard. A separate winter–spring climatology must be calculated before calling the product long-term/proactive.
* Report AUC together with PR-AUC, Youden threshold, sensitivity, specificity, the fraction of area classified high hazard, and boundary-tolerance results. Do not describe AUC around 0.60 as high predictive performance.
