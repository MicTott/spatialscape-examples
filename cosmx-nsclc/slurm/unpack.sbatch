#!/usr/bin/env bash
#SBATCH --job-name=cosmx-unpack
#SBATCH --output=logs/unpack-%j.log
#SBATCH --mem=4G
#SBATCH --cpus-per-task=2
#SBATCH --time=2:00:00
# Unpack the two archives beside themselves (flat/ and giotto/).
set -euo pipefail
cd "$SLURM_SUBMIT_DIR/raw"   # submit from this dataset's folder
mkdir -p flat giotto
tar -xzf All_SMI_Flat_data.tar.gz -C flat
tar -xzf All_SMI_Giotto_object.tar.gz -C giotto
echo "flat: $(ls flat | tr '\n' ' ')"; echo "giotto: $(ls giotto | tr '\n' ' ')"
