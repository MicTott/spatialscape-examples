"""The CytAssist mouse brain section as one AnnData, with its spatial/ folder beside it.

    python prepare.py
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent  # this dataset's folder
sys.path.insert(0, str(HERE.parent))  # for common/
from common.spaceranger import prepare  # noqa: E402

RAW = HERE / "raw"
DEST = HERE / "processed/section"

if __name__ == "__main__":
    analysis = RAW / "analysis" if (RAW / "analysis").exists() else None
    a = prepare(RAW / "filtered_feature_bc_matrix.h5", RAW / "spatial", analysis, DEST)
    print(f"wrote {DEST / 'adata.h5ad'}: {a.n_obs:,} spots x {a.n_vars:,} genes")
