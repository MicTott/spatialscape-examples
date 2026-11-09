#!/usr/bin/env bash
#SBATCH --job-name=cosmx-prepare
#SBATCH --output=logs/prepare-%A_%a.log
#SBATCH --array=1-8
#SBATCH --mem=24G
#SBATCH --cpus-per-task=2
#SBATCH --time=2:00:00
# One task per section, in the order of SECTIONS in prepare.py. Needs processed/cell_types.csv
# from celltypes.py.
set -euo pipefail
cd "$SLURM_SUBMIT_DIR"   # submit from this dataset's folder, with the environment active
SECTIONS=(Lung5_Rep1 Lung5_Rep2 Lung5_Rep3 Lung6 Lung9_Rep1 Lung9_Rep2 Lung12 Lung13)
python prepare.py "${SECTIONS[$((SLURM_ARRAY_TASK_ID - 1))]}"
