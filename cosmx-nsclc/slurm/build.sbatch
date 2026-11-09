#!/usr/bin/env bash
#SBATCH --job-name=cosmx-build
#SBATCH --output=logs/build-%j.log
#SBATCH --mem=48G
#SBATCH --cpus-per-task=4
#SBATCH --time=12:00:00
# Builds bundles/cosmx-nsclc from the eight sections; the transcript tables (3 GB of CSV each) take most of the time.
set -euo pipefail
cd "$SLURM_SUBMIT_DIR"   # submit from this dataset's folder, with the environment active
spatialscape build dataset.yaml
spatialscape validate bundles/cosmx-nsclc
