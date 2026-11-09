"""Readers for 10x Genomics output files shared by the prepare scripts: the feature-barcode matrix (.h5) and
a Space Ranger `spatial/` folder. Used as `from common.tenx import ...` with the repository root on sys.path."""
from pathlib import Path

import h5py
import numpy as np
import pandas as pd
import scipy.sparse as sp


def read_10x_h5(path: Path) -> tuple[sp.csr_matrix, pd.DataFrame, np.ndarray]:
    """A 10x feature-barcode matrix as cells x features CSR, the feature table (id, name, feature_type) and
    the barcodes, in file order."""
    with h5py.File(path) as h:
        g = h["matrix"]
        shape = tuple(int(v) for v in g["shape"][:])  # (features, cells)
        m = sp.csc_matrix((g["data"][:], g["indices"][:], g["indptr"][:]), shape=shape)
        f = g["features"]
        features = pd.DataFrame({"id": f["id"][:].astype(str), "name": f["name"][:].astype(str), "feature_type": f["feature_type"][:].astype(str)})
        barcodes = g["barcodes"][:].astype(str)
    return m.T.tocsr(), features, barcodes


def genes_only(X: sp.csr_matrix, features: pd.DataFrame) -> tuple[sp.csr_matrix, pd.DataFrame]:
    """Keep the Gene Expression features; var is indexed by gene symbol (made unique) with the Ensembl id kept."""
    keep = (features["feature_type"] == "Gene Expression").to_numpy()
    names = features.loc[keep, "name"].to_numpy().astype(object)
    seen: dict[str, int] = {}
    for i, n in enumerate(names):  # a symbol used twice gets a suffix, as anndata's var_names_make_unique does
        if n in seen:
            seen[n] += 1
            names[i] = f"{n}-{seen[n]}"
        else:
            seen[n] = 0
    var = pd.DataFrame({"gene_id": features.loc[keep, "id"].to_numpy()}, index=pd.Index(names.astype(str)))
    return X[:, keep], var


def read_tissue_positions(spatial: Path) -> pd.DataFrame:
    """Space Ranger's tissue positions (csv with or without a header, or parquet for Visium HD) indexed by barcode,
    with full-resolution pixel columns pxl_col_in_fullres (x) and pxl_row_in_fullres (y) and in_tissue."""
    for name in ("tissue_positions.parquet", "tissue_positions.csv", "tissue_positions_list.csv"):
        p = spatial / name
        if p.exists():
            break
    else:
        raise FileNotFoundError(f"no tissue positions in {spatial}")
    if p.suffix == ".parquet":
        t = pd.read_parquet(p)
    else:
        cols = ["barcode", "in_tissue", "array_row", "array_col", "pxl_row_in_fullres", "pxl_col_in_fullres"]
        head = pd.read_csv(p, nrows=1, header=None)
        t = pd.read_csv(p) if str(head.iloc[0, 0]) == "barcode" else pd.read_csv(p, header=None, names=cols)
    return t.set_index("barcode")
