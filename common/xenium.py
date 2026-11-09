"""A Xenium-style outs folder (Xenium Onboard Analysis, and the Atera previews, which use the same layout) as one
AnnData: cells x genes from cell_feature_matrix.h5, the per-cell table from cells.parquet (centroids in microns,
transcript counts, areas) and 10x's graph clusters from analysis.zarr.zip. Boundaries, transcripts and the images
stay in the outs folder; a dataset.yaml points at them there."""
from pathlib import Path

import anndata as ad
import numpy as np
import pandas as pd
import zarr

from common.tenx import genes_only, read_10x_h5

PER_CELL = {  # obs column: cells.parquet column, kept when the table has it
    "transcript_counts": "transcript_counts",
    "cell_area": "cell_area",
    "nucleus_area": "nucleus_area",
}


def graph_clusters(path: Path, n_cells: int) -> np.ndarray:
    """10x's graph-based clusters from analysis.zarr.zip: cell_groups/<k> holds, per grouping, the cell indices of
    each cluster as a CSR-like indices/indptr pair; the grouping named gene_expression_graphclust is the one."""
    g = zarr.open_group(zarr.storage.ZipStore(path, mode="r"), mode="r")["cell_groups"]
    groupings = list(g.attrs["grouping_names"])
    k = groupings.index("gene_expression_graphclust")
    names = g.attrs["group_names"][k]
    indices = g[str(k)]["indices"][:]
    indptr = g[str(k)]["indptr"][:]
    labels = np.full(n_cells, "unassigned", dtype=object)
    for c in range(len(indptr) - 1):
        labels[indices[indptr[c] : indptr[c + 1]]] = names[c]
    return labels


def prepare(outs: Path, dest: Path) -> ad.AnnData:
    """Write `dest` (an .h5ad) from the outs folder and return what was written."""
    X, features, barcodes = read_10x_h5(outs / "cell_feature_matrix.h5")
    X, var = genes_only(X, features)
    cells = pd.read_parquet(outs / "cells.parquet")
    cells["cell_id"] = cells["cell_id"].astype(str)
    cells = cells.set_index("cell_id").loc[barcodes]  # the matrix's cell order
    obs = pd.DataFrame({"cluster": pd.Categorical(graph_clusters(outs / "analysis.zarr.zip", len(cells)))}, index=cells.index)
    for col, source in PER_CELL.items():
        if source in cells:
            obs[col] = cells[source].to_numpy()
    adata = ad.AnnData(X=X.astype(np.float32), obs=obs, var=var)
    adata.obsm["spatial"] = cells[["x_centroid", "y_centroid"]].to_numpy(dtype=np.float64)  # microns
    dest.parent.mkdir(parents=True, exist_ok=True)
    adata.write_h5ad(dest)
    print(f"wrote {dest}: {adata.n_obs:,} cells x {adata.n_vars:,} genes, {obs['cluster'].nunique()} clusters")
    return adata
