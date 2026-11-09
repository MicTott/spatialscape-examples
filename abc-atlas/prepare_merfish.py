"""One AnnData per MERFISH section of the whole-brain atlas, from the 4.0 M-cell log2 matrix and the metadata.

    python prepare_merfish.py --list            # the 59 section labels, one per line
    python prepare_merfish.py <section label>   # e.g. C57BL6J-638850.37

Each section gets processed/merfish/<section>.h5ad: its cells (rows of the big matrix, read through
the file without loading it whole), coordinates in microns (the atlas stores millimetres), the taxonomy labels at
four levels with the neurotransmitter, and the CCF parcellation (division, structure) from the registered
coordinates. slurm/prepare_merfish.sbatch runs this as an array job, one task per section.
"""
import sys
from pathlib import Path

import anndata as ad
import h5py
import numpy as np
import pandas as pd
import scipy.sparse as sp

HERE = Path(__file__).resolve().parent  # this dataset's folder
RAW = HERE / "raw"
MATRIX = RAW / "expression_matrices/MERFISH-C57BL6J-638850/20230830/C57BL6J-638850-log2.h5ad"
CELLS = RAW / "metadata/MERFISH-C57BL6J-638850/20241115/views/cell_metadata_with_cluster_annotation.csv"
CCF = RAW / "metadata/MERFISH-C57BL6J-638850-CCF/20231215/views/cell_metadata_with_parcellation_annotation.csv"
DEST = HERE / "processed" / "merfish"
LABELS = ["neurotransmitter", "class", "subclass", "supertype", "cluster"]
PARCELLATION = ["parcellation_division", "parcellation_structure"]


def sections() -> list[str]:
    """The section labels, from the matrix's own obs (the metadata CSVs may still be downloading)."""
    with h5py.File(MATRIX) as h:
        labels = ad.io.read_elem(h["obs"])["brain_section_label"]
    return sorted(labels.astype(str).unique())


def aligned(meta: pd.DataFrame, matrix_index: pd.Index) -> pd.DataFrame:
    """The metadata rows for the cells in `matrix_index`, keyed the way the matrix spells the label.

    The 2024 metadata writes some cell labels with a '-1' suffix that the 2023 matrix does not carry, and a few
    cells exist in both spellings. A label matches exactly first; one that does not is tried without the suffix,
    unless that spelling already matched another row."""
    labels = meta.index.astype(str)
    exact = labels.isin(matrix_index)
    stripped = labels.str.replace(r"-1$", "", regex=True)
    use_stripped = ~exact & stripped.isin(matrix_index) & ~stripped.isin(labels[exact])
    out = meta[exact | use_stripped].copy()
    out.index = labels.where(exact, stripped)[exact | use_stripped]
    return out[~out.index.duplicated(keep="first")]


def read_rows(path: Path, rows: np.ndarray) -> tuple[sp.csr_matrix, pd.DataFrame]:
    """The rows (sorted indices) of an h5ad's CSR matrix and its var table, read through h5py without the rest."""
    with h5py.File(path) as h:
        x = h["X"]
        indptr = x["indptr"][:]
        starts, ends = indptr[rows], indptr[rows + 1]
        data = np.concatenate([x["data"][s:e] for s, e in zip(starts, ends, strict=True)])
        indices = np.concatenate([x["indices"][s:e] for s, e in zip(starts, ends, strict=True)])
        new_indptr = np.concatenate([[0], np.cumsum(ends - starts)])
        n_var = int(x.attrs["shape"][1])
        var = ad.io.read_elem(h["var"])
    return sp.csr_matrix((data, indices, new_indptr), shape=(len(rows), n_var)), var


def main() -> None:
    if sys.argv[1:] == ["--list"]:
        print("\n".join(sections()))
        return
    section = sys.argv[1]
    with h5py.File(MATRIX) as h:
        matrix_obs = ad.io.read_elem(h["obs"])
    matrix_obs.index = matrix_obs.index.astype(str)
    in_section = matrix_obs.index[matrix_obs["brain_section_label"].astype(str) == section]
    if in_section.empty:
        sys.exit(f"no cells in section {section!r}")
    cells = aligned(pd.read_csv(CELLS, index_col="cell_label"), in_section)
    ccf = aligned(pd.read_csv(CCF, index_col="cell_label", usecols=["cell_label", *PARCELLATION]), in_section)
    cells = cells.reindex(in_section).join(ccf, how="left")
    missing = cells["cluster_alias"].isna()
    if missing.any():  # cells the 2024 metadata no longer lists (dropped by the atlas's own QC): left out
        print(f"{section}: {int(missing.sum()):,} of {len(cells):,} matrix cells have no metadata row and are left out")
        cells = cells[~missing]
        in_section = cells.index

    position = pd.Series(np.arange(len(matrix_obs)), index=matrix_obs.index)
    rows = np.sort(position.loc[in_section].to_numpy())
    X, var = read_rows(MATRIX, rows)
    cells = cells.loc[matrix_obs.index[rows]]

    obs = pd.DataFrame(index=cells.index)
    for col in LABELS + PARCELLATION:
        obs[col] = pd.Categorical(cells[col].fillna("NA").astype(str))
    obs["section"] = section
    adata = ad.AnnData(X=X.astype(np.float32), obs=obs, var=var)
    adata.var_names = var["gene_symbol"].astype(str).to_numpy()
    adata = adata[:, ~adata.var_names.str.startswith("Blank")].copy()  # the 50 blank control barcodes
    adata.obsm["spatial"] = cells[["x", "y"]].to_numpy(dtype=np.float64) * 1000.0  # millimetres -> microns
    DEST.mkdir(parents=True, exist_ok=True)
    adata.write_h5ad(DEST / f"{section}.h5ad")
    print(f"{section}: {adata.n_obs:,} cells x {adata.n_vars} genes -> {DEST / f'{section}.h5ad'}")


if __name__ == "__main__":
    main()
