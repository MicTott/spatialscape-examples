#!/usr/bin/env bash
# Visium HD FFPE mouse brain (Space Ranger 3.0.0). Run it where large downloads are allowed (on a cluster, its transfer node).
set -euo pipefail
cd "$(dirname "$0")"
OUT=raw
B=https://cf.10xgenomics.com/samples/spatial-exp/3.0.0/Visium_HD_Mouse_Brain/Visium_HD_Mouse_Brain
mkdir -p "$OUT" && cd "$OUT"
for f in binned_outputs.tar.gz spatial.tar.gz tissue_image.tif; do
  [ -s "$f" ] || curl -sS -L -C - -o "$f" "${B}_$f"
done
tar -xzf binned_outputs.tar.gz; tar -xzf spatial.tar.gz
find . -maxdepth 3 -type d | sort; echo "done: $(du -sh . | cut -f1)"
