"""One MERSCOPE slice as processed/<slice>/: adata.h5ad (cells x genes, counts, with the
centroids in microns, the cell volume and a Leiden clustering) and cell_boundaries.parquet (one row per vertex,
10x's column names, so dataset.yaml's `polygons:` needs no column mapping). The transcripts and the mosaic images
stay in raw/; dataset.yaml points at them. The micron-to-mosaic transform is printed, for the `images:` entries.

    python prepare.py Slice1_Replicate1
"""
import sys
from pathlib import Path

import anndata as ad
import h5py
import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import scipy.sparse as sp

HERE = Path(__file__).resolve().parent  # this dataset's folder
sys.path.insert(0, str(HERE.parent))  # for common/
from common.cluster import leiden_clusters  # noqa: E402

RAW = HERE / "raw"
DEST = HERE / "processed"
Z_PLANE = "zIndex_3"  # the middle of the seven z planes; the mosaics used are the z3 ones too


def boundaries(folder: Path, cell_ids: set[str]) -> pa.Table:
    """Every cell's outline at Z_PLANE as a long table: cell_id, vertex_x, vertex_y (microns). A cell segmented as
    several polygons on that plane keeps its largest; a cell with no polygon on that plane takes the nearest plane
    that has one; a cell with none anywhere is left out (the viewer draws its dot)."""
    ids, xs, ys = [], [], []
    want = int(Z_PLANE.removeprefix("zIndex_"))
    skipped = 0
    for path in sorted(folder.glob("feature_data_*.hdf5")):
        with h5py.File(path) as h:
            cells = h["featuredata"]
            for cid in cells:
                if cid not in cell_ids:
                    continue
                planes = sorted((k for k in cells[cid] if k.startswith("zIndex_")), key=lambda k: abs(int(k.removeprefix("zIndex_")) - want))
                ring = None
                for plane in planes:
                    polys = [cells[cid][plane][p]["coordinates"][0] for p in cells[cid][plane]]
                    if polys:
                        ring = max(polys, key=len)
                        break
                if ring is None:
                    skipped += 1
                    continue
                ids.append(np.full(len(ring), cid, dtype=object))
                xs.append(ring[:, 0])
                ys.append(ring[:, 1])
    if skipped:
        print(f"  {skipped:,} cells have no boundary polygon on any plane")
    return pa.table({"cell_id": np.concatenate(ids), "vertex_x": np.concatenate(xs), "vertex_y": np.concatenate(ys)})


def main() -> None:
    slice_ = sys.argv[1]
    src = RAW / slice_
    counts = pd.read_csv(src / "cell_by_gene.csv", index_col=0)
    counts.index = counts.index.astype(str)
    counts = counts.loc[:, ~counts.columns.str.startswith("Blank-")]  # the control barcodes
    cells = pd.read_csv(src / "cell_metadata.csv", index_col=0)
    cells.index = cells.index.astype(str)
    cells = cells.loc[counts.index]
    adata = ad.AnnData(X=sp.csr_matrix(counts.to_numpy(dtype=np.float32)), obs=pd.DataFrame(index=counts.index), var=pd.DataFrame(index=counts.columns))
    adata.obsm["spatial"] = cells[["center_x", "center_y"]].to_numpy(dtype=np.float64)  # microns
    adata.obs["volume"] = cells["volume"].to_numpy()
    adata.obs["total_counts"] = np.asarray(adata.X.sum(axis=1)).ravel()
    adata.obs["cluster"] = leiden_clusters(adata)
    out = DEST / slice_
    out.mkdir(parents=True, exist_ok=True)
    adata.write_h5ad(out / "adata.h5ad")
    table = boundaries(src / "cell_boundaries", set(adata.obs_names))
    pq.write_table(table, out / "cell_boundaries.parquet")
    t = np.loadtxt(src / "images" / "micron_to_mosaic_pixel_transform.csv")
    scale, ox, oy = t[0, 0], t[0, 2], t[1, 2]
    print(f"{slice_}: {adata.n_obs:,} cells x {adata.n_vars} genes, {adata.obs['cluster'].nunique()} clusters, {table.num_rows:,} boundary vertices")
    print(f"  images: pixel_size: {1 / scale:.6f}  translate: [{-ox / scale:.3f}, {-oy / scale:.3f}]   # from micron_to_mosaic_pixel_transform.csv")


if __name__ == "__main__":
    main()
