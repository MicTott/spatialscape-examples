#!/usr/bin/env bash
# The whole app from nothing, on a laptop with R and spatialscape installed (see ../setup_env.sh):
#   bash build.sh
# 1. download.R fetches the spatialLIBD SpatialExperiment into raw/spe_dlpfc.rds (skipped when it is there).
# 2. `spatialscape init` writes dataset.init.yaml, the menu of what the object holds; dataset.yaml (committed) is the
#    version we kept of that menu. Diff the two to see what was chosen.
# 3. `spatialscape build` reads the .rds once into bundles/.cache/, then builds the twelve sections; `validate` checks
#    the result. Then: spatialscape serve bundles --open
set -euo pipefail
cd "$(dirname "$0")"
[ -s raw/spe_dlpfc.rds ] || Rscript download.R
spatialscape init raw/spe_dlpfc.rds --id visium-human-dlpfc --name "Human DLPFC, Visium (Maynard et al. 2021)" -o dataset.init.yaml
spatialscape build dataset.yaml
spatialscape validate bundles/visium-human-dlpfc
