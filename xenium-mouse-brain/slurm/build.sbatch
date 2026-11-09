#!/usr/bin/env bash
#SBATCH --job-name=xenium-mouse-brain-build
#SBATCH --output=logs/build-%j.log
#SBATCH --mem=24G
#SBATCH --cpus-per-task=4
#SBATCH --time=2:00:00
# Builds the app into bundles/xenium-mouse-brain. Rerunning after an edit to dataset.yaml rebuilds only what changed.
set -euo pipefail
cd "$SLURM_SUBMIT_DIR"   # submit from this dataset's folder, with the environment active
spatialscape build dataset.yaml
spatialscape validate bundles/xenium-mouse-brain
