#!/usr/bin/env bash
#SBATCH --job-name=atera-unzip
#SBATCH --output=logs/unzip-%A_%a.log
#SBATCH --array=1-2
#SBATCH --mem=4G
#SBATCH --cpus-per-task=2
#SBATCH --time=6:00:00
# One task per section (1 = breast, 2 = cervical): checksum the archive, unpack it beside itself into outs/.
# A task whose archive is still downloading (size short of the one in download.sh) stops with a message.
set -euo pipefail
cd "$SLURM_SUBMIT_DIR"   # submit from this dataset's folder, with the environment active
SECTIONS=(breast cervical)
SIZES=(55238489095 88844924511)
i=$((SLURM_ARRAY_TASK_ID - 1))
dir="raw/${SECTIONS[$i]}"
have=$(wc -c < "$dir/outs.zip" | tr -d " ")
if [ "$have" -ne "${SIZES[$i]}" ]; then echo "${SECTIONS[$i]}: outs.zip is $have of ${SIZES[$i]} bytes, still downloading"; exit 1; fi
cd "$dir"
shasum -a 256 outs.zip > outs.zip.sha256
mkdir -p outs
unzip -q -o outs.zip -d outs
echo "${SECTIONS[$i]}: $(ls outs | tr '\n' ' ')"
