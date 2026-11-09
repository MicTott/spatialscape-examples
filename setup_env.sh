#!/usr/bin/env bash
# One Python environment for every dataset here, in env/ at the repository root:
#   bash setup_env.sh            # then: source env/bin/activate
# Needs Python 3.11 or newer on PATH (on a cluster, load its module first, e.g. `module load python/3.14`).
# spatialscape is pinned to the release the apps were built with; the other packages are what the prepare
# scripts import (scanpy for the Leiden clustering, scikit-image for the CosMx masks).
set -euo pipefail
cd "$(dirname "$0")"
PY="${PYTHON:-python3}"
"$PY" --version
"$PY" -m venv env
env/bin/pip install --upgrade pip --quiet
env/bin/pip install --quiet -r requirements.txt
env/bin/spatialscape --version
echo "ready: source env/bin/activate"
