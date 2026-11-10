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
# a release from PyPI carries the viewer; an install straight from the git repository (the pin before the 1.0.0 tag)
# builds and validates apps but cannot show them: `serve` needs the viewer built with Node, which a wheel ships
if ! env/bin/python -c "import importlib.resources as r, spatialscape; (r.files(spatialscape) / '_app' / 'index.html').read_bytes()" 2>/dev/null; then
  echo "note: this install has no packaged viewer, so \`spatialscape serve\` cannot open the apps here; \`build\` and \`validate\` work."
  echo "      The viewer comes with the PyPI release (requirements.txt pins it once v1.0.0 is tagged)."
fi
echo "ready: source env/bin/activate"
