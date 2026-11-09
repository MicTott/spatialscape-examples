#!/usr/bin/env bash
# Zhang et al. 2023 spatial ATAC + RNA sections from GEO (series GSE205055). Run it where large downloads are allowed (on a cluster, its transfer node).
set -euo pipefail
cd "$(dirname "$0")"
OUT=raw
G=https://ftp.ncbi.nlm.nih.gov/geo/samples
mkdir -p "$OUT" && cd "$OUT"
get() {  # get <section> <GSM> <file>
  mkdir -p "$1"; local dest="$1/$3"
  [ -s "$dest" ] || curl -sS -L -C - -o "$dest" "$G/${2:0:7}nnn/$2/suppl/$3"
}
get MouseBrain_20um        GSM6204623 GSM6204623_MouseBrain_20um_fragments.tsv.gz
get MouseBrain_20um        GSM6204623 GSM6204623_MouseBrain_20um_spatial.tar.gz
get MouseBrain_20um        GSM6204636 GSM6204636_MouseBrain_20um_matrix.tsv.gz
get MouseBrain_20um_rep2   GSM6758284 GSM6758284_MouseBrain_20um_repATAC_fragments.tsv.gz
get MouseBrain_20um_rep2   GSM6753041 GSM6753041_MouseBrain_20um_repATAC_matrix.tsv.gz
get MouseBrain_20um_rep2   GSM6753041 GSM6753041_MouseBrain_20um_repATAC_spatial.tar.gz
get MouseBrain_20um_100bc  GSM6758285 GSM6758285_MouseBrain_20um_100barcodes_ATAC_fragments.tsv.gz
get MouseBrain_20um_100bc  GSM6753043 GSM6753043_MouseBrain_20um_100barcodes_ATAC_matrix.tsv.gz
get MouseBrain_20um_100bc  GSM6753043 GSM6753043_MouseBrain_20um_100barcodes_ATAC_spatial.tar.gz
get HumanBrain_50um        GSM6206884 GSM6206884_HumanBrain_50um_fragments.tsv.gz
get HumanBrain_50um        GSM6206884 GSM6206884_HumanBrain_50um_spatial.tar.gz
get HumanBrain_50um        GSM6206885 GSM6206885_HumanBrain_50um_matrix.tsv.gz
for d in */; do (cd "$d" && for t in *_spatial.tar.gz; do tar -xzf "$t"; done); done
find . -maxdepth 3 | sort; echo "done: $(du -sh . | cut -f1)"
