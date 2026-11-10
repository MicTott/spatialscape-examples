#!/usr/bin/env bash
# The processed objects of one dataset from the Zenodo record, into <dataset>/processed/, so an app builds without
# the raw download and the prepare step:
#   bash fetch_processed.sh xenium-mouse-brain
#   spatialscape build xenium-mouse-brain/dataset.yaml
# The record holds every dataset small enough to deposit. abc-atlas (215 GB of processed objects) is not in it:
# its folder's download.sh and prepare scripts rebuild the objects from Allen's public bucket.
set -euo pipefail
cd "$(dirname "$0")"
RECORD="${ZENODO_RECORD:-0000000}"    # the Zenodo record id, set once the deposit is published
NOT_DEPOSITED="abc-atlas"
ds="${1:?usage: bash fetch_processed.sh <dataset folder>}"
[ -f "$ds/dataset.yaml" ] || { echo "no dataset folder named $ds"; exit 1; }
case " $NOT_DEPOSITED " in *" $ds "*) echo "$ds is too large for the record: run $ds/download.sh and its prepare scripts (see $ds/README.md)"; exit 1;; esac
[ "$RECORD" != "0000000" ] || { echo "the Zenodo record is not published yet: build from raw data with $ds/download.sh and prepare.py"; exit 1; }
url="https://zenodo.org/records/$RECORD/files/$ds-processed.tar?download=1"
tmp="$ds/processed.partial.tar"
echo "fetch   $ds-processed.tar"
curl -sS -L -C - -o "$tmp" "$url"
echo "unpack  into $ds/"
tar -xf "$tmp" -C "$ds"      # processed/ (or raw/ for a dataset with no prepare step) and the yaml it was built with, as dataset.zenodo.yaml
rm -f "$tmp"
[ -f MANIFEST.sha256 ] || curl -sS -L -o MANIFEST.sha256 "https://zenodo.org/records/$RECORD/files/MANIFEST.sha256?download=1"
(cd "$ds" && grep "^[0-9a-f]* *$ds/" ../MANIFEST.sha256 | sed "s| $ds/| |" | shasum -a 256 -c --quiet) && echo "checksums ok"
echo "next: spatialscape build $ds/dataset.yaml"
