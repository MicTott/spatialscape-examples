#!/usr/bin/env bash
#SBATCH --job-name=atera-build
#SBATCH --output=logs/build-%j.log
#SBATCH --mem=128G
#SBATCH --cpus-per-task=8   # the image decode (JPEG 2000) and chunk compression use every CPU the job has; the transcript tiler is one thread
#SBATCH --time=24:00:00
# Builds bundles/atera from both sections. The morphology images at full resolution are the big part: a whole pyramid
# level of the four 16-bit channels is read at once (14 GB for cervical) and the build refuses a read above a sixth
# of the job's memory. The transcript tables are next (1.0 billion transcripts for cervical; the tiler keeps 7 bytes
# per transcript while it collects tiles, so about 7 GB). At the 0.425 um level 48 GB was enough (37 GB peak).
# Rerunning rebuilds only what changed.
set -euo pipefail
cd "$SLURM_SUBMIT_DIR"   # submit from this dataset's folder, with the environment active
spatialscape build dataset.yaml
spatialscape validate bundles/atera
