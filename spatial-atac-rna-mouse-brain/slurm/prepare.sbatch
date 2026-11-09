#!/usr/bin/env bash
#SBATCH --job-name=spatial-atac-rna-prepare
#SBATCH --output=logs/prepare-%j.log
#SBATCH --mem=16G
#SBATCH --cpus-per-task=4
#SBATCH --time=0:30:00
set -euo pipefail
cd "$SLURM_SUBMIT_DIR"   # submit from this dataset's folder, with the environment active
python prepare.py
