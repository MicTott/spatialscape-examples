#!/usr/bin/env bash
# Visium CytAssist FFPE mouse brain (Space Ranger 2.0.0). Run it where large downloads are allowed (on a cluster, its transfer node).
set -euo pipefail
cd "$(dirname "$0")"
OUT=raw
B=https://cf.10xgenomics.com/samples/spatial-exp/2.0.0/CytAssist_FFPE_Mouse_Brain_Rep1/CytAssist_FFPE_Mouse_Brain_Rep1
mkdir -p "$OUT" && cd "$OUT"
for f in filtered_feature_bc_matrix.h5 spatial.tar.gz analysis.tar.gz tissue_image.tif; do
  [ -s "$f" ] || curl -sS -L -C - -o "$f" "${B}_$f" || { echo "no $f"; rm -f "$f"; }
done
for t in spatial analysis; do [ -s $t.tar.gz ] && tar -xzf $t.tar.gz; done
ls; echo "done: $(du -sh . | cut -f1)"
