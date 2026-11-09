"""A Space Ranger sample (Visium, Visium HD bins) as one AnnData next to a copy of its `spatial/` folder, which is
the layout spatialscape's `images: auto` understands: the H&E and the scale come from `spatial/` on their own."""
import shutil
from pathlib import Path

import anndata as ad
import numpy as np
import pandas as pd

from common.tenx import genes_only, read_10x_h5, read_tissue_positions


def graph_clusters(analysis: Path) -> pd.Series | None:
    p = analysis / "clustering" / "gene_expression_graphclust" / "clusters.csv"
    if not p.exists():
        return None
    t = pd.read_csv(p).set_index("Barcode")
    return pd.Series([f"cluster {c}" for c in t["Cluster"]], index=t.index.astype(str), name="cluster")


def prepare(matrix_h5: Path, spatial: Path, analysis: Path | None, dest_dir: Path) -> ad.AnnData:
    """matrix + tissue positions (+ graph clusters) -> dest_dir/adata.h5ad, with spatial/ copied beside it."""
    X, features, barcodes = read_10x_h5(matrix_h5)
    X, var = genes_only(X, features)
    pos = read_tissue_positions(spatial).loc[barcodes]
    obs = pd.DataFrame(index=pd.Index(barcodes, name="barcode"))
    obs["in_tissue"] = pos["in_tissue"].to_numpy().astype(int)
    obs["array_row"] = pos["array_row"].to_numpy()
    obs["array_col"] = pos["array_col"].to_numpy()
    counts = np.asarray(X.sum(axis=1)).ravel()
    obs["total_counts"] = counts
    obs["detected_genes"] = np.diff(X.indptr)
    if analysis is not None:
        cl = graph_clusters(analysis)
        if cl is not None:
            obs["cluster"] = pd.Categorical(cl.reindex(obs.index).fillna("unassigned"))
    adata = ad.AnnData(X=X.astype(np.float32), obs=obs, var=var)
    adata.obsm["spatial"] = pos[["pxl_col_in_fullres", "pxl_row_in_fullres"]].to_numpy(dtype=np.float64)  # full-resolution pixels
    dest_dir.mkdir(parents=True, exist_ok=True)
    adata.write_h5ad(dest_dir / "adata.h5ad")
    if (dest_dir / "spatial").exists():
        shutil.rmtree(dest_dir / "spatial")
    shutil.copytree(spatial, dest_dir / "spatial")
    return adata
