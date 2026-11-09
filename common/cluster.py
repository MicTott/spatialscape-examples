"""A quick Leiden clustering of a counts matrix, for datasets that come without one (so the viewer has an annotation
to colour by and the ATAC tracks have groups to pool). Standard scanpy steps, deliberately plain."""
import pandas as pd
import scanpy as sc


def leiden_clusters(adata, *, n_top_genes: int = 2000, resolution: float = 0.8, seed: int = 0) -> pd.Categorical:
    """Cluster labels ('cluster 0', 'cluster 1', ...) for the rows of `adata`, whose X holds raw counts."""
    work = adata.copy()
    sc.pp.filter_genes(work, min_cells=3)
    sc.pp.normalize_total(work, target_sum=1e4)
    sc.pp.log1p(work)
    sc.pp.highly_variable_genes(work, n_top_genes=min(n_top_genes, work.n_vars))
    sc.pp.pca(work, n_comps=min(30, work.n_vars - 1), mask_var="highly_variable", random_state=seed)
    sc.pp.neighbors(work, n_neighbors=15, random_state=seed)
    sc.tl.leiden(work, resolution=resolution, key_added="cluster", flavor="igraph", n_iterations=2, directed=False, random_state=seed)
    return pd.Categorical([f"cluster {c}" for c in work.obs["cluster"]])
