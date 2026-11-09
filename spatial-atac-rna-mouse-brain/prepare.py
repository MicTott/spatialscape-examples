"""Each co-profiled section as one AnnData: the RNA counts (genes x pixels, tsv) transposed to pixels x genes,
the pixel positions from the Space Ranger-style spatial/ folder (copied beside the h5ad so the image and the
scale are found on their own), and a clustering of the RNA (scanpy: normalise, log, PCA, neighbours, Leiden at
resolution 0.8), because GEO carries no labels for these sections. The ATAC fragments stay in raw/; the
yaml's tracks: block points at them, and the pixel barcodes get the "-1" suffix the fragment file uses.

    python prepare.py            # every section
    python prepare.py MouseBrain_20um
"""
import shutil
import sys
from pathlib import Path

import anndata as ad
import numpy as np
import pandas as pd
import scipy.sparse as sp

HERE = Path(__file__).resolve().parent  # this dataset's folder
sys.path.insert(0, str(HERE.parent))  # for common/
from common.cluster import leiden_clusters  # noqa: E402
from common.tenx import read_tissue_positions  # noqa: E402

RAW = HERE / "raw"
DEST = HERE / "processed"
SECTIONS = {  # folder: (RNA matrix, spatial folder, fragments)
    "MouseBrain_20um": ("GSM6204636_MouseBrain_20um_matrix.tsv.gz", "MouseBrain_20um_spatial", "GSM6204623_MouseBrain_20um_fragments.tsv.gz"),
    "MouseBrain_20um_rep2": ("GSM6753041_MouseBrain_20um_repATAC_matrix.tsv.gz", "MouseBrain_20um_repATAC_spatial", "GSM6758284_MouseBrain_20um_repATAC_fragments.tsv.gz"),
    "MouseBrain_20um_100bc": ("GSM6753043_MouseBrain_20um_100barcodes_ATAC_matrix.tsv.gz", "MouseBrain_20um_100barcodes_ATAC_spatial", "GSM6758285_MouseBrain_20um_100barcodes_ATAC_fragments.tsv.gz"),
    "HumanBrain_50um": ("GSM6206885_HumanBrain_50um_matrix.tsv.gz", "HumanBrain_50um_spatial", "GSM6206884_HumanBrain_50um_fragments.tsv.gz"),
}


def prepare(section: str) -> None:
    matrix, spatial, _fragments = SECTIONS[section]
    counts = pd.read_csv(RAW / section / matrix, sep="\t", index_col=0)  # genes x pixels
    adata = ad.AnnData(X=sp.csr_matrix(counts.to_numpy().T.astype(np.float32)), obs=pd.DataFrame(index=counts.columns.astype(str)), var=pd.DataFrame(index=counts.index.astype(str)))
    adata.var_names_make_unique()
    pos = read_tissue_positions(RAW / section / spatial)
    pos.index = pos.index.astype(str)
    adata = adata[adata.obs_names.isin(pos.index)].copy()
    pos = pos.loc[adata.obs_names]
    adata.obsm["spatial"] = pos[["pxl_col_in_fullres", "pxl_row_in_fullres"]].to_numpy(dtype=np.float64)
    adata.obs["in_tissue"] = pos["in_tissue"].to_numpy().astype(int)
    adata.obs["barcode"] = [f"{b}-1" for b in adata.obs_names]  # as the fragment file spells them
    adata.obs["total_counts"] = np.asarray(adata.X.sum(axis=1)).ravel()
    adata.obs["detected_genes"] = np.diff(adata.X.indptr)

    adata.obs["cluster"] = leiden_clusters(adata)  # a clustering of the RNA, so the ATAC tracks have groups to be pooled by

    out = DEST / section
    out.mkdir(parents=True, exist_ok=True)
    adata.write_h5ad(out / "adata.h5ad")
    if (out / "spatial").exists():
        shutil.rmtree(out / "spatial")
    shutil.copytree(RAW / section / spatial, out / "spatial")
    print(f"{section}: {adata.n_obs:,} pixels x {adata.n_vars:,} genes, {adata.obs['cluster'].nunique()} clusters -> {out}")


if __name__ == "__main__":
    for section in sys.argv[1:] or SECTIONS:
        prepare(section)
