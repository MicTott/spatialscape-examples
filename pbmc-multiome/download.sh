#!/usr/bin/env bash
# 10x Genomics PBMC multiome, "pbmc_granulocyte_sorted_10k" (Cell Ranger ARC 2.0.0): 2.7 GB, most of it the ATAC
# fragment file. Run it where large downloads are allowed (on a cluster, its transfer node).
set -euo pipefail
cd "$(dirname "$0")"
OUT=raw
B=https://cf.10xgenomics.com/samples/cell-arc/2.0.0/pbmc_granulocyte_sorted_10k/pbmc_granulocyte_sorted_10k
mkdir -p "$OUT" && cd "$OUT"
for f in filtered_feature_bc_matrix.h5 atac_peak_annotation.tsv per_barcode_metrics.csv atac_fragments.tsv.gz; do
  [ -s "$f" ] || { curl -sS -L -f -C - -o "$f.part" "${B}_$f" && mv "$f.part" "$f"; }   # .part: a cut-off download resumes
done
ls; echo "done: $(du -sh . | cut -f1)"
