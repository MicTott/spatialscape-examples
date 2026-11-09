#!/usr/bin/env bash
#SBATCH --job-name=merscope-mosaics
#SBATCH --output=logs/mosaics-%A_%a.log
#SBATCH --array=1-3
#SBATCH --mem=40G
#SBATCH --cpus-per-task=2
#SBATCH --time=2:00:00
# One task per slice: the two 10 GB mosaics reduced 4x into tiled TIFFs (one mosaic is held in memory at a time).
set -euo pipefail
cd "$SLURM_SUBMIT_DIR"   # submit from this dataset's folder, with the environment active
SLICES=(Slice1_Replicate1 Slice2_Replicate1 Slice3_Replicate1)
python mosaics.py "${SLICES[$((SLURM_ARRAY_TASK_ID - 1))]}"
