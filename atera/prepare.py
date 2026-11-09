"""One AnnData per Atera preview section from its outs folder, which has the Xenium layout (cell_feature_matrix.h5,
cells.parquet, analysis.zarr.zip, boundaries, transcripts.parquet, morphology_focus/); see common/xenium.py.

    python prepare.py breast      # -> processed/breast/adata.h5ad
    python prepare.py cervical
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent  # this dataset's folder
sys.path.insert(0, str(HERE.parent))  # for common/
from common.xenium import prepare  # noqa: E402

SECTIONS = ["breast", "cervical"]

section = sys.argv[1]
if section not in SECTIONS:
    sys.exit(f"section must be one of {SECTIONS}")
prepare(HERE / "raw" / section / "outs", HERE / "processed" / section / "adata.h5ad")
