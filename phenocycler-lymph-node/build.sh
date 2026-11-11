#!/usr/bin/env bash
# The whole app from nothing, on a laptop with the environment active (see ../setup_env.sh):
#   bash build.sh
# 1. download.sh fetches the three cores into raw/ (660 MB; a core that is there is skipped).
# 2. `spatialscape build` reads each spatialproteomics object as it is (no prepare step): intensities, annotations,
#    the 56-channel image and the cell outlines traced from the label mask; `validate` checks the result.
#    Then: spatialscape serve bundles --open
set -euo pipefail
cd "$(dirname "$0")"
bash download.sh
spatialscape build dataset.yaml
spatialscape validate bundles/phenocycler-lymph-node
