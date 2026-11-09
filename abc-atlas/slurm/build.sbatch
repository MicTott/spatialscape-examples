#!/usr/bin/env bash
#SBATCH --job-name=abc-atlas-build
#SBATCH --output=logs/build-%j.log
#SBATCH --mem=192G
#SBATCH --cpus-per-task=2
#SBATCH --time=12:00:00
# Builds bundles/abc-atlas from whatever processed holds: the MERFISH sections first, the 10x nuclei
# once prepare_10x.py has made WholeBrain.h5ad. Rerunning builds only the samples that are new or changed.
# Memory: the whole-brain matrix (4.04 M nuclei x 32,285 genes, 18.7 billion stored values) is 8 bytes per stored
# value, 139 GB, and the build keeps one copy plus a small mask over its index (the Pallium-Glut panel, 7.4 billion
# values, peaked at 59 GB), so 192 GB covers it. The work is one thread of numpy, so 2 CPUs: a small request
# backfills into a busy queue where 8 CPUs plus 256 GB waited days. The MERFISH sections alone need under 16 GB.
set -euo pipefail
cd "$SLURM_SUBMIT_DIR"   # submit from this dataset's folder, with the environment active
spatialscape build dataset.yaml
spatialscape validate bundles/abc-atlas
