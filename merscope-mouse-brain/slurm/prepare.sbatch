#!/usr/bin/env bash
#SBATCH --job-name=merscope-prepare
#SBATCH --output=logs/prepare-%A_%a.log
#SBATCH --array=1-3
#SBATCH --mem=16G
#SBATCH --cpus-per-task=4
#SBATCH --time=1:00:00
# One task per slice. Needs the slice's files from download.sh.
set -euo pipefail
cd "$SLURM_SUBMIT_DIR"   # submit from this dataset's folder, with the environment active
SLICES=(Slice1_Replicate1 Slice2_Replicate1 Slice3_Replicate1)
python prepare.py "${SLICES[$((SLURM_ARRAY_TASK_ID - 1))]}"
