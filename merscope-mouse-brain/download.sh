#!/usr/bin/env bash
# Download the files in files.tsv from Vizgen's public bucket over HTTPS. Run it where large downloads are allowed (on a cluster, its transfer node):
#   bash download.sh
# Resumable: a file whose size already matches is skipped, so rerunning after an interruption finishes the rest.
# Each file is checked against the bucket's md5 after download.
set -euo pipefail
size() { wc -c < "$1" | tr -d ' '; }                                   # file size in bytes (GNU and macOS)
md5() { if command -v md5sum >/dev/null; then md5sum "$1" | cut -d' ' -f1; else command md5 -q "$1"; fi; }
cd "$(dirname "$0")"
OUT=raw
BASE=https://storage.googleapis.com/vizgen-mouse-brain-map
n=0
tail -n +2 files.tsv | while IFS=$'\t' read -r dataset path bytes md5; do
  dest="$OUT/$dataset/${path#BrainReceptorShowcase/*/*/}"
  mkdir -p "$(dirname "$dest")"
  if [ -f "$dest" ] && [ "$(size "$dest")" -eq "$bytes" ]; then continue; fi
  [ "$bytes" -gt 100000000 ] && echo "fetch   $dest ($((bytes / 1000000)) MB)"
  curl -sS -L -C - -o "$dest" "$BASE/$path"
  test "$(size "$dest")" -eq "$bytes" || { echo "$dest is $(size "$dest") bytes, expected $bytes"; exit 1; }
  have=$(openssl dgst -md5 -binary "$dest" | base64)
  [ "$have" = "$md5" ] || { echo "md5 mismatch: $dest"; exit 1; }
done
echo "done: $(du -sh "$OUT" | cut -f1) in $OUT"
