#!/usr/bin/env bash
# Download the Allen Brain Cell Atlas pieces listed in files.tsv (made by tools/files_from_manifest.py from the
# release-20250531 manifest). Run it where large downloads are allowed (on a cluster, its transfer node):
#   bash download.sh
# Resumable: a file whose size already matches is skipped; md5 is checked after each download.
set -euo pipefail
size() { wc -c < "$1" | tr -d ' '; }                                   # file size in bytes (GNU and macOS)
md5() { if command -v md5sum >/dev/null; then md5sum "$1" | cut -d' ' -f1; else command md5 -q "$1"; fi; }
cd "$(dirname "$0")"
OUT=raw
mkdir -p "$OUT"
tail -n +2 files.tsv | while IFS=$'\t' read -r dir rel size md5 url; do
  dest="$OUT/$rel"
  mkdir -p "$(dirname "$dest")"
  if [ -f "$dest" ] && [ "$(size "$dest")" -eq "$size" ]; then echo "have    $rel"; continue; fi
  echo "fetch   $rel ($((size / 1000000)) MB)"
  curl -sS -L -C - -o "$dest" "$url"
  got="$(md5 "$dest")"
  [ "$got" = "$md5" ] || { echo "md5 mismatch for $rel: $got != $md5"; exit 1; }
done
echo "done: $(du -sh "$OUT" | cut -f1) in $OUT"
