"""The 10x nuclei of the whole-brain atlas as one AnnData on the atlas's own whole-brain UMAP, the view the Allen
site shows. The expression is published as one log2 matrix per dissection region and chemistry (WMB-10Xv2-<region>,
WMB-10Xv3-<region>, WMB-10XMulti), so this runs in two passes:

    python prepare_10x.py --list-files               # the region matrices present in raw/
    python prepare_10x.py split <region h5ad>        # that file's cells, one piece per neighbourhood
    python prepare_10x.py concat WholeBrain          # every piece -> processed/tenx/WholeBrain.h5ad
    python prepare_10x.py --list-groups              # the neighbourhoods
    python prepare_10x.py concat <neighbourhood>     # its pieces alone, on the neighbourhood's own UMAP (not used by the app)

The split goes by cell-type neighbourhood (a nucleus belongs to one through its cluster, cluster_group_membership.csv)
so that no step holds more than one region's cells; the pieces carry the neighbourhood UMAPs, and the whole-brain
concat swaps in the whole-brain coordinates. slurm/prepare_10x_split.sbatch runs the split as an array job,
slurm/prepare_10x_concat.sbatch the whole-brain concat.
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
META = RAW / "metadata/WMB-10X/20241115"
TAX = RAW / "metadata/WMB-neighborhoods/20231215"
GENES = META / "gene.csv"
OUT = HERE / "processed" / "tenx"
PIECES = OUT / "pieces"
LABELS = ["neurotransmitter", "class", "subclass", "supertype", "cluster"]


def region_files() -> list[Path]:
    return sorted(p for p in (RAW / "expression_matrices").glob("WMB-10X*/*/*-log2.h5ad"))


def groups() -> dict[str, str]:
    """neighbourhood name -> its UMAP file stem, from dimension_reduction.csv (WholeBrain left out)."""
    dr = pd.read_csv(TAX / "dimension_reduction.csv")
    return {row["name"]: row["label"] for _, row in dr.iterrows() if row["name"] != "WholeBrain"}


def membership() -> pd.Series:
    """cluster_alias -> neighbourhood name (every cluster is in exactly one besides WholeBrain)."""
    m = pd.read_csv(TAX / "cluster_group_membership.csv")
    m = m[m["cluster_group_name"] != "WholeBrain"]
    return m.drop_duplicates("cluster_alias").set_index("cluster_alias")["cluster_group_name"]


def read_rows(h: h5py.File, rows: np.ndarray) -> sp.csr_matrix:
    """The given rows (sorted) of the file's CSR matrix, reading only their slices."""
    x = h["X"]
    indptr = x["indptr"][:]
    starts, ends = indptr[rows], indptr[rows + 1]
    # contiguous runs of rows are read in one slice each
    breaks = np.flatnonzero(np.diff(rows) != 1) + 1
    data, indices = [], []
    for seg in np.split(np.arange(len(rows)), breaks):
        s, e = starts[seg[0]], ends[seg[-1]]
        data.append(x["data"][s:e])
        indices.append(x["indices"][s:e])
    new_indptr = np.concatenate([[0], np.cumsum(ends - starts)])
    return sp.csr_matrix((np.concatenate(data), np.concatenate(indices), new_indptr), shape=(len(rows), int(x.attrs["shape"][1])))


def complete(path: Path) -> bool:
    """Whether the download of a region matrix has finished (its size matches files.tsv)."""
    rel = str(path.relative_to(RAW))
    for line in (Path(__file__).with_name("files.tsv")).read_text().splitlines()[1:]:
        _d, relative_path, size, _md5, _url = line.split("\t")
        if relative_path == rel:
            return path.stat().st_size == int(size)
    return False


def split(path: Path) -> None:
    path = path.resolve()
    label = path.name.replace("-log2.h5ad", "")  # e.g. WMB-10Xv2-TH
    marker = PIECES / ".done" / label
    if marker.exists():
        print(f"{label}: already split")
        return
    if not complete(path):
        print(f"{label}: download not complete yet, skipped")
        return
    with h5py.File(path) as h:
        obs = ad.io.read_elem(h["obs"])
        var = ad.io.read_elem(h["var"])
        obs.index = obs.index.astype(str)
        cells = pd.read_csv(META / "views/cell_metadata_with_cluster_annotation.csv", index_col="cell_label", low_memory=False)
        cells = cells[cells["feature_matrix_label"] == label].reindex(obs.index)
        group_of = membership()
        cells["neighbourhood"] = cells["cluster_alias"].map(group_of)
        position = pd.Series(np.arange(len(obs)), index=obs.index)
        for name, stem in groups().items():
            idx = cells.index[cells["neighbourhood"] == name]
            if idx.empty:
                continue
            umap = pd.read_csv(TAX / f"{stem}.csv", index_col="cell_label")
            idx = idx[idx.isin(umap.index)]
            rows = np.sort(position.loc[idx].to_numpy())
            X = read_rows(h, rows)
            sub = cells.loc[obs.index[rows]]
            o = pd.DataFrame(index=sub.index)
            for col in LABELS:
                o[col] = pd.Categorical(sub[col].fillna("NA").astype(str))
            o["region"] = pd.Categorical(sub["region_of_interest_acronym"].astype(str))
            o["library_method"] = pd.Categorical(sub["library_method"].astype(str))
            o["donor_sex"] = pd.Categorical(sub["donor_sex"].astype(str))
            a = ad.AnnData(X=X.astype(np.float32), obs=o, var=var)
            a.obsm["X_umap"] = umap.loc[sub.index, ["x", "y"]].to_numpy(dtype=np.float64)
            dest = PIECES / name / f"{label}.h5ad"
            dest.parent.mkdir(parents=True, exist_ok=True)
            a.write_h5ad(dest)
            print(f"{label} -> {name}: {a.n_obs:,} cells")
    marker.parent.mkdir(parents=True, exist_ok=True)
    marker.touch()


def concat(name: str) -> None:
    """The pieces of one neighbourhood, or of every neighbourhood for `WholeBrain`, as one h5ad, appended row by row
    on disk so memory stays at one piece (the whole brain's pieces are 106 GB together). Every region matrix shares
    the same genes, which is checked. The whole-brain file takes its UMAP from Allen's whole-brain embedding."""
    pending = [f.name for f in region_files() if not (PIECES / ".done" / f.name.replace("-log2.h5ad", "")).exists()]
    if pending:
        sys.exit(f"{len(pending)} region matrices are not split yet (run the split array first): {', '.join(pending[:5])} ...")
    whole = name == "WholeBrain"
    pieces = sorted(PIECES.glob("*/*.h5ad")) if whole else sorted((PIECES / name).glob("*.h5ad"))
    if not pieces:
        sys.exit(f"no pieces for {name!r} under {PIECES / name}")

    n_obs = nnz = 0
    var = None
    for piece in pieces:  # sizes first, so the output arrays are made once
        with h5py.File(piece) as h:
            n_obs += int(h["X"].attrs["shape"][0])
            nnz += int(h["X"]["data"].shape[0])
            v = ad.io.read_elem(h["var"])
            if var is None:
                var = v
            elif not v.index.equals(var.index):
                sys.exit(f"{piece.name} has different genes from {pieces[0].name}")
    symbols = pd.read_csv(GENES, index_col="gene_identifier")["gene_symbol"]
    var["gene_id"] = var.index
    var.index = pd.Index(symbols.reindex(var.index).fillna(pd.Series(var.index, index=var.index)).astype(str))
    var.index = ad.utils.make_index_unique(var.index)  # a symbol shared by two Ensembl ids gets a -1 suffix; gene_id keeps the id
    var.index.name = None  # h5ad refuses an index named like a column (gene_symbol) whose values differ

    OUT.mkdir(parents=True, exist_ok=True)
    dest = OUT / f"{name}.h5ad"
    tmp = dest.with_name(f".{name}.partial.h5ad")
    obs_parts, umap_parts = [], []
    with h5py.File(tmp, "w") as out:
        out.attrs["encoding-type"] = "anndata"
        out.attrs["encoding-version"] = "0.1.0"
        x = out.create_group("X")
        x.attrs["encoding-type"] = "csr_matrix"
        x.attrs["encoding-version"] = "0.1.0"
        x.attrs["shape"] = np.array([n_obs, len(var)], dtype=np.int64)
        chunk = (min(1 << 20, nnz),)
        data = x.create_dataset("data", shape=(nnz,), dtype=np.float32, chunks=chunk)
        indices = x.create_dataset("indices", shape=(nnz,), dtype=np.int32, chunks=chunk)
        indptr = x.create_dataset("indptr", shape=(n_obs + 1,), dtype=np.int64)
        indptr[0] = 0
        at, row = 0, 0
        for piece in pieces:
            with h5py.File(piece) as h:
                px = h["X"]
                m, r = int(px["data"].shape[0]), int(px.attrs["shape"][0])
                data[at : at + m] = px["data"][:]
                indices[at : at + m] = px["indices"][:]
                indptr[row + 1 : row + r + 1] = px["indptr"][1:].astype(np.int64) + at  # a piece's indptr is int32; the panel passes 2^31 entries
                obs_parts.append(ad.io.read_elem(h["obs"]))
                umap_parts.append(ad.io.read_elem(h["obsm"])["X_umap"])
                at, row = at + m, row + r
            print(f"  {piece.stem}: {r:,} cells")
        obs = pd.concat(obs_parts)
        for col in obs.columns:  # categoricals with different levels come back as plain strings: make them categorical again
            if not isinstance(obs[col].dtype, pd.CategoricalDtype) and not pd.api.types.is_numeric_dtype(obs[col]):
                obs[col] = pd.Categorical(obs[col].astype(str))
        if whole:
            dr = pd.read_csv(TAX / "dimension_reduction.csv").set_index("name")["label"]
            umap = pd.read_csv(TAX / f"{dr['WholeBrain']}.csv", index_col="cell_label").reindex(obs.index)
            if umap["x"].isna().any():
                sys.exit(f"{int(umap['x'].isna().sum()):,} nuclei are missing from the whole-brain UMAP")
            X_umap = umap[["x", "y"]].to_numpy(dtype=np.float64)
        else:
            X_umap = np.vstack(umap_parts)
        ad.io.write_elem(out, "obs", obs)
        ad.io.write_elem(out, "var", var)
        ad.io.write_elem(out, "obsm", {"X_umap": X_umap})
    tmp.rename(dest)
    print(f"{name}: {n_obs:,} cells x {len(var):,} genes from {len(pieces)} region files -> {dest}")


if __name__ == "__main__":
    cmd = sys.argv[1:]
    if cmd == ["--list-files"]:
        print("\n".join(str(p) for p in region_files()))
    elif cmd == ["--list-groups"]:
        print("\n".join(groups()))
    elif cmd[:1] == ["split"]:
        split(Path(cmd[1]))
    elif cmd[:1] == ["concat"]:
        concat(cmd[1])
    else:
        sys.exit(__doc__)
