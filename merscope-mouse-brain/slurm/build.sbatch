#!/usr/bin/env bash
#SBATCH --job-name=merscope-build
#SBATCH --output=logs/build-%j.log
#SBATCH --mem=48G
#SBATCH --cpus-per-task=4
#SBATCH --time=6:00:00
# Builds bundles/merscope-mouse-brain. Each 11 GB mosaic is read whole before it is reduced, hence the memory.
set -euo pipefail
cd "$SLURM_SUBMIT_DIR"   # submit from this dataset's folder, with the environment active
spatialscape build dataset.yaml
spatialscape validate bundles/merscope-mouse-brain
