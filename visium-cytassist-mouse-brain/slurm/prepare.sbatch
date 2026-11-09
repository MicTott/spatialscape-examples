#!/usr/bin/env bash
#SBATCH --job-name=visium-cytassist-mouse-brain-prepare
#SBATCH --output=logs/prepare-%j.log
#SBATCH --mem=12G
#SBATCH --cpus-per-task=2
#SBATCH --time=0:30:00
set -euo pipefail
cd "$SLURM_SUBMIT_DIR"   # submit from this dataset's folder, with the environment active
python prepare.py
