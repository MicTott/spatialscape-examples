"""The Xenium outs folder as processed/adata.h5ad (see common/xenium.py for what goes in).

    python prepare.py
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent  # this dataset's folder
sys.path.insert(0, str(HERE.parent))  # for common/
from common.xenium import prepare  # noqa: E402

prepare(HERE / "raw" / "outs", HERE / "processed" / "adata.h5ad")
