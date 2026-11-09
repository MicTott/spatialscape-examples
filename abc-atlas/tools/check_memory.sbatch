#!/usr/bin/env bash
#SBATCH --job-name=abc-memory-check
#SBATCH --output=logs/memory-check-%j.log
#SBATCH --mem=100G
#SBATCH --cpus-per-task=4
#SBATCH --time=4:00:00
set -euo pipefail
cd "$SLURM_SUBMIT_DIR"   # submit from this dataset's folder, with the environment active
python check_memory.py Pallium-Glut
