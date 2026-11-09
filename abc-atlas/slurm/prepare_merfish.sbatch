#!/usr/bin/env bash
#SBATCH --job-name=abc-merfish-prepare
#SBATCH --output=logs/merfish-prepare-%A_%a.log
#SBATCH --array=1-59
#SBATCH --mem=24G
#SBATCH --cpus-per-task=1
#SBATCH --time=1:00:00
# One task per MERFISH section: task N prepares the N-th label of `prepare_merfish.py --list`.
set -euo pipefail
cd "$SLURM_SUBMIT_DIR"   # submit from this dataset's folder, with the environment active
section="$(python prepare_merfish.py --list | sed -n "${SLURM_ARRAY_TASK_ID}p")"
python prepare_merfish.py "$section"
