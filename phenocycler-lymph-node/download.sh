#!/usr/bin/env bash
# Three reactive lymph node cores from the PhenoCycler tissue microarrays of Meyer-Bender et al.: one spatialproteomics
# object per core, 660 MB of zip files, 1.1 GB unpacked. They come from the example-data share of the spatialproteomics
# package, which is fast; the same cores are archived in BioImage Archive S-BIAD2100 (CC0) under
# data_for_publication/tmas/. A core that is there is skipped.
set -euo pipefail
cd "$(dirname "$0")"
OUT=raw
B="https://oc.embl.de/index.php/s/XzEa9po1tjiDzzJ/download?path=%2F&files="
mkdir -p "$OUT" && cd "$OUT"
for core in LN_11_1 LN_13_1 LN_24_1; do
  [ -d "$core.zarr" ] && continue
  curl -sS -L -f -o "$core.zarr.zip" "$B$core.zarr.zip"
  unzip -q -o "$core.zarr.zip" -d "$core.unzip" && mv "$core.unzip"/*.zarr "$core.zarr" && rm -r "$core.unzip" "$core.zarr.zip"
done
ls; echo "done: $(du -sh . | cut -f1)"
