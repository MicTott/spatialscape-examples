#!/usr/bin/env bash
# Download the two Atera preview bundles from 10x. Run it where large downloads are allowed (on a cluster, its transfer node):
#   bash download.sh
# Resumable (curl -C -); sizes as served on 2026-10-29. The archives stay as published and are unzipped beside
# themselves. The outs archives are on 10x's S3 host; the H&E and the cell groups on its CDN.
set -euo pipefail
size() { wc -c < "$1" | tr -d ' '; }                                   # file size in bytes (GNU and macOS)
md5() { if command -v md5sum >/dev/null; then md5sum "$1" | cut -d' ' -f1; else command md5 -q "$1"; fi; }
cd "$(dirname "$0")"
OUT=raw
S3=https://s3-us-west-2.amazonaws.com/10x.files/samples/atera/dev
CDN=https://cf.10xgenomics.com/samples/atera/dev
fetch() {  # fetch <section> <file name> <url> <expected bytes>
  local dest="$OUT/$1/$2"
  mkdir -p "$(dirname "$dest")"
  if [ -f "$dest" ] && [ "$(size "$dest")" -eq "$4" ]; then echo "have    $1/$2"; return; fi
  echo "fetch   $1/$2 ($(($4 / 1000000000)) GB)"
  curl -sS -L -C - -o "$dest" "$3"
  test "$(size "$dest")" -eq "$4" || { echo "$dest is $(size "$dest") bytes, expected $4"; exit 1; }
}
fetch breast   cell_groups.csv  "$CDN/WTA_Preview_FFPE_Breast_Cancer/WTA_Preview_FFPE_Breast_Cancer_cell_groups.csv"     "$(curl -sI "$CDN/WTA_Preview_FFPE_Breast_Cancer/WTA_Preview_FFPE_Breast_Cancer_cell_groups.csv" | awk 'tolower($1)=="content-length:"{print $2+0}')"
fetch cervical cell_groups.csv  "$CDN/WTA_Preview_FFPE_Cervical_Cancer/WTA_Preview_FFPE_Cervical_Cancer_cell_groups.csv" "$(curl -sI "$CDN/WTA_Preview_FFPE_Cervical_Cancer/WTA_Preview_FFPE_Cervical_Cancer_cell_groups.csv" | awk 'tolower($1)=="content-length:"{print $2+0}')"
fetch breast   outs.zip         "$S3/WTA_Preview_FFPE_Breast_Cancer/WTA_Preview_FFPE_Breast_Cancer_outs.zip"              55238489095
fetch breast   he_image.ome.tif "$CDN/WTA_Preview_FFPE_Breast_Cancer/WTA_Preview_FFPE_Breast_Cancer_he_image.ome.tif"     17732417252
fetch cervical outs.zip         "$S3/WTA_Preview_FFPE_Cervical_Cancer/WTA_Preview_FFPE_Cervical_Cancer_outs.zip"          88844924511
# Unpacking 55 and 89 GB is a compute job, not a transfer: slurm/unzip.sbatch, one array task per section.
echo "next: sbatch slurm/unzip.sbatch"
echo "done: $(du -sh "$OUT" | cut -f1) in $OUT"
