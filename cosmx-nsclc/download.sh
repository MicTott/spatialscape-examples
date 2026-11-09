#!/usr/bin/env bash
# Download the CosMx SMI non-small-cell lung cancer data (He et al. 2022) from NanoString's public bucket.
# Run it where large downloads are allowed (on a cluster, its transfer node):  bash download.sh
# The "flat data" archive holds every section's cell table, cell-by-gene matrix, transcripts, FOV positions and
# per-FOV composite images and cell label masks; the Giotto object carries the paper's cell-type calls. The raw
# per-FOV morphology images (361 GB) are not needed. Resumable (curl -C -), checked against the bucket's md5sums.
set -euo pipefail
size() { wc -c < "$1" | tr -d ' '; }                                   # file size in bytes (GNU and macOS)
md5() { if command -v md5sum >/dev/null; then md5sum "$1" | cut -d' ' -f1; else command md5 -q "$1"; fi; }
cd "$(dirname "$0")"
OUT=raw
BASE="https://nanostring-public-share.s3.us-west-2.amazonaws.com/SMI-Compressed"
mkdir -p "$OUT"
fetch() {  # fetch <file name in the bucket> <expected md5>
  local dest="$OUT/${1// /_}"
  if [ -f "$dest" ] && [ "$(md5 "$dest")" = "$2" ]; then echo "have    $dest"; return; fi
  echo "fetch   $1"
  curl -sS -L -C - -o "$dest" "$BASE/${1// /+}"
  [ "$(md5 "$dest")" = "$2" ] || { echo "md5 mismatch: $dest"; exit 1; }
}
curl -sS -o "$OUT/SMI-ReadMe.html" "$BASE/SMI-ReadMe.html"
curl -sS -o "$OUT/md5sums.txt" "$BASE/md5sums.txt"
fetch "All SMI Flat data.tar.gz"     87286b0a1ded161de334b829a6da420a    # 11.3 GB
fetch "All SMI Giotto object.tar.gz" fbf64119ae8f86da2e292ebf7bed7e20    # 0.9 GB
echo "next: sbatch slurm/unpack.sbatch"
