#!/usr/bin/env bash
# Download the Xenium Prime 5K mouse brain bundle from 10x. Run it where large downloads are allowed (on a cluster, its transfer node):
#   bash download.sh
# Resumable (curl -C -); the zip is kept next to its extraction, exactly as published.
set -euo pipefail
size() { wc -c < "$1" | tr -d ' '; }                                   # file size in bytes (GNU and macOS)
md5() { if command -v md5sum >/dev/null; then md5sum "$1" | cut -d' ' -f1; else command md5 -q "$1"; fi; }
cd "$(dirname "$0")"
OUT=raw
URL=https://cf.10xgenomics.com/samples/xenium/3.0.0/Xenium_Prime_Mouse_Brain_Coronal_FF/Xenium_Prime_Mouse_Brain_Coronal_FF_outs.zip
SIZE=13315451681   # bytes, as served on 2026-10-29
mkdir -p "$OUT"
cd "$OUT"
curl -sS -L -C - -o outs.zip "$URL"
test "$(size outs.zip)" -eq "$SIZE" || { echo "outs.zip is $(size outs.zip) bytes, expected $SIZE"; exit 1; }
shasum -a 256 outs.zip > outs.zip.sha256
mkdir -p outs && unzip -q -o outs.zip -d outs
ls outs
echo "done: $(du -sh . | cut -f1) in $PWD"
