#!/usr/bin/env bash
#SBATCH --job-name=abc-10x-split
#SBATCH --output=logs/10x-split-%A_%a.log
#SBATCH --array=1-24
#SBATCH --mem=48G
#SBATCH --cpus-per-task=1
#SBATCH --time=3:00:00
# One task per region matrix: task N splits the N-th file of `prepare_10x.py --list-files` into neighbourhood pieces.
# Set --array to the number of files that line prints once the download is complete.
set -euo pipefail
cd "$SLURM_SUBMIT_DIR"   # submit from this dataset's folder, with the environment active
file="$(python prepare_10x.py --list-files | sed -n "${SLURM_ARRAY_TASK_ID}p")"
[ -n "$file" ] || { echo "no file for task $SLURM_ARRAY_TASK_ID"; exit 0; }
python prepare_10x.py split "$file"
