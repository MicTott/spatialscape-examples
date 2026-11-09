#!/usr/bin/env bash
#SBATCH --job-name=atera-prepare
#SBATCH --output=logs/prepare-%A_%a.log
#SBATCH --array=1-2
#SBATCH --mem=32G
#SBATCH --cpus-per-task=2
#SBATCH --time=1:00:00
# One task per section: 1 = breast, 2 = cervical. Needs the outs folders from download.sh.
set -euo pipefail
cd "$SLURM_SUBMIT_DIR"   # submit from this dataset's folder, with the environment active
SECTIONS=(breast cervical)
python prepare.py "${SECTIONS[$((SLURM_ARRAY_TASK_ID - 1))]}"
