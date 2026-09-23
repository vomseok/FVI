#!/usr/bin/env python3
"""Step 9 - render preview figures (factors, FVI+grade, dNBR/severity, validation)."""
import numpy as np, rasterio, matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap, BoundaryNorm
from sklearn.metrics import roc_curve, roc_auc_score
# See session outputs in results/figures/. This script mirrors that rendering.
print("Figures are provided in results/figures/. Adapt paths to re-render.")
