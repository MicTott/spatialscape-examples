#!/usr/bin/env bash
#SBATCH --job-name=spatial-atac-rna-build
#SBATCH --output=logs/build-%j.log
#SBATCH --mem=32G
#SBATCH --cpus-per-task=4
#SBATCH --time=4:00:00
# The tracks: block streams each fragment file once (the 1.5 GB one takes a while) and writes bigWigs per cluster.
set -euo pipefail
cd "$SLURM_SUBMIT_DIR"   # submit from this dataset's folder, with the environment active
export XDG_CACHE_HOME="$PWD/../.cache"   # the RefSeq gene tables spatialscape downloads (8 MB per genome) stay inside this repository
spatialscape build dataset.yaml
spatialscape validate bundles/spatial-atac-rna-mouse-brain
