"""The 8 um bins of the Visium HD mouse brain as one AnnData, with the square_008um spatial/ folder beside it.

    python prepare.py
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent  # this dataset's folder
sys.path.insert(0, str(HERE.parent))  # for common/
from common.spaceranger import prepare  # noqa: E402

BIN = HERE / "raw/binned_outputs/square_008um"
DEST = HERE / "processed/square_008um"

if __name__ == "__main__":
    a = prepare(BIN / "filtered_feature_bc_matrix.h5", BIN / "spatial", BIN / "analysis", DEST)
    print(f"wrote {DEST / 'adata.h5ad'}: {a.n_obs:,} bins x {a.n_vars:,} genes")
