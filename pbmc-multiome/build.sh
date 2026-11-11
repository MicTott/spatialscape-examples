#!/usr/bin/env bash
# The whole app from nothing, on a laptop with the environment active (see ../setup_env.sh):
#   bash build.sh
# 1. download.sh fetches the four 10x files into raw/ (2.7 GB; a file that is there is skipped).
# 2. prepare.py turns the matrix into processed/pbmc.h5ad: both UMAPs, the cell types, gene activity, marker-set
#    scores and the most variable peaks (skipped when the file is there; run it yourself after editing it).
# 3. `spatialscape build` writes the two samples and streams the fragment file once for the tracks; `validate`
#    checks the result. Then: spatialscape serve bundles --open
set -euo pipefail
cd "$(dirname "$0")"
bash download.sh
[ -s processed/pbmc.h5ad ] || python prepare.py
spatialscape build dataset.yaml
spatialscape validate bundles/pbmc-multiome
