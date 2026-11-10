#!/usr/bin/env bash
# What goes into the Zenodo record for one dataset: <dataset>-processed.tar holding processed/ (or raw/ for a dataset
# with no prepare step, whose yaml reads the published object itself) and the dataset.yaml it was built with (as
# dataset.zenodo.yaml), plus its lines in MANIFEST.sha256. Run where the folder is complete:
#   bash pack_processed.sh xenium-mouse-brain          # -> zenodo/xenium-mouse-brain-processed.tar
# fetch_processed.sh is the inverse. abc-atlas is left out of the record (215 GB); see its README.
set -euo pipefail
cd "$(dirname "$0")"
ds="${1:?usage: bash pack_processed.sh <dataset folder>}"
if ls "$ds"/prepare*.py >/dev/null 2>&1; then data=processed; else data=raw; fi
[ -d "$ds/$data" ] || { echo "$ds/$data is missing: run its download / prepare step first"; exit 1; }
mkdir -p zenodo
cp "$ds/dataset.yaml" "$ds/dataset.zenodo.yaml"
tar -chf "zenodo/$ds-processed.tar" -C "$ds" --exclude="$data/tmp-*" "$data" dataset.zenodo.yaml   # -h: on a cluster, $data is a symbolic link
rm "$ds/dataset.zenodo.yaml"
(cd "$ds" && find "$data"/ -type f | sort | xargs shasum -a 256 | sed "s| $data/| $ds/$data/|") > "zenodo/$ds.sha256"
cat zenodo/*.sha256 > zenodo/MANIFEST.sha256
echo "zenodo/$ds-processed.tar: $(du -h "zenodo/$ds-processed.tar" | cut -f1), $(wc -l < "zenodo/$ds.sha256" | tr -d ' ') files listed in zenodo/MANIFEST.sha256"
