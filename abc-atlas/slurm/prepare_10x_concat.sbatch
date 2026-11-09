#!/usr/bin/env bash
#SBATCH --job-name=abc-10x-concat
#SBATCH --output=logs/10x-concat-%j.log
#SBATCH --mem=48G
#SBATCH --cpus-per-task=2
#SBATCH --time=8:00:00
# After every split task: appends all 106 GB of pieces into processed/tenx/WholeBrain.h5ad, one piece
# at a time, so memory stays near the largest piece (about 10 GB) plus the 4 M-row metadata and UMAP.
set -euo pipefail
cd "$SLURM_SUBMIT_DIR"   # submit from this dataset's folder, with the environment active
python prepare_10x.py concat WholeBrain
