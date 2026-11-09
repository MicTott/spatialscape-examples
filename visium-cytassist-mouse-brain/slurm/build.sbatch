#!/usr/bin/env bash
#SBATCH --job-name=visium-cytassist-mouse-brain-build
#SBATCH --output=logs/build-%j.log
#SBATCH --mem=12G
#SBATCH --cpus-per-task=4
#SBATCH --time=2:00:00
set -euo pipefail
cd "$SLURM_SUBMIT_DIR"   # submit from this dataset's folder, with the environment active
spatialscape build dataset.yaml
spatialscape validate bundles/visium-cytassist-mouse-brain
