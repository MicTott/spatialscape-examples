"""One CosMx section as processed/<section>/: adata.h5ad (cells x genes from the flat files, with
the paper's cell types from cell_types.csv), composite.tif (the per-FOV composite images stitched into one picture,
reduced 2x) and cell_boundaries.parquet (outlines traced from the per-FOV label masks). The transcripts stay in
raw/; dataset.yaml points at them.

Coordinates are global pixels (0.18 um each) throughout: cells and boundaries from the flat files, the composite
placed by the translate the script prints (the FOV bounding box's corner, in microns). Within a FOV, CosMx counts
local y upwards from the bottom edge while image rows count down from the top, so masks and composites are flipped
to the coordinates' orientation; the script checks this by comparing mask centroids with the cell table.

    python prepare.py Lung5_Rep1
"""
import sys
from pathlib import Path

import anndata as ad
import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import scipy.sparse as sp
import tifffile
from PIL import Image
from skimage.measure import find_contours, regionprops

HERE = Path(__file__).resolve().parent  # this dataset's folder
RAW = HERE / "raw" / "flat"
DEST = HERE / "processed"
SECTIONS = ["Lung5_Rep1", "Lung5_Rep2", "Lung5_Rep3", "Lung6", "Lung9_Rep1", "Lung9_Rep2", "Lung12", "Lung13"]
PX = 0.18  # microns per pixel
FOV_W, FOV_H = 5472, 3648  # pixels per field of view
REDUCE = 2  # the composite is written at 0.36 um per pixel
MAX_VERTICES = 64  # per outline here; the build keeps 24


def flat_dir(section: str) -> Path:
    return RAW / section / f"{section}-Flat_files_and_images"


def cells_and_counts(section: str, slide: int) -> ad.AnnData:
    d = flat_dir(section)
    expr = pd.read_csv(d / f"{section}_exprMat_file.csv")
    expr = expr[expr["cell_ID"] != 0]  # row 0 of each FOV sums the transcripts outside every cell
    genes = [c for c in expr.columns if c not in ("fov", "cell_ID") and not c.startswith(("NegPrb", "SystemControl", "FalseCode"))]
    meta = pd.read_csv(d / f"{section}_metadata_file.csv")
    ids = expr.apply(lambda r: f"c_{slide}_{int(r['fov'])}_{int(r['cell_ID'])}", axis=1)
    meta.index = [f"c_{slide}_{int(f)}_{int(c)}" for f, c in zip(meta["fov"], meta["cell_ID"])]
    meta = meta.loc[ids]
    obs = pd.DataFrame(index=ids.to_numpy())
    obs["fov"] = meta["fov"].to_numpy().astype(int)
    obs["area"] = meta["Area"].to_numpy() * PX * PX  # pixels -> square microns
    obs["total_counts"] = expr[genes].sum(axis=1).to_numpy()
    types = pd.read_csv(DEST / "cell_types.csv", index_col="cell_ID")
    types = types[types["section"] == section]
    for col in ("cell_type", "niche", "patient"):
        obs[col] = pd.Categorical(types[col].reindex(obs.index).fillna("not in the paper's set").astype(str))
    adata = ad.AnnData(X=sp.csr_matrix(expr[genes].to_numpy(dtype=np.float32)), obs=obs, var=pd.DataFrame(index=genes))
    adata.obsm["spatial"] = meta[["CenterX_global_px", "CenterY_global_px"]].to_numpy(dtype=np.float64)
    return adata


def fov_positions(section: str) -> pd.DataFrame:
    pos = pd.read_csv(flat_dir(section) / f"{section}_fov_positions_file.csv")
    pos["x"] = pos["x_global_px"].round().astype(int)
    pos["y"] = pos["y_global_px"].round().astype(int)
    return pos.set_index("fov")


def composite(section: str, pos: pd.DataFrame, out: Path) -> tuple[float, float]:
    """The FOV composites pasted onto one canvas (global pixels, cropped to the FOVs' bounding box) and written at
    REDUCE x; returns the canvas corner in microns, for `translate:` in dataset.yaml."""
    x0, y0 = int(pos["x"].min()), int(pos["y"].min())
    w, h = int(pos["x"].max()) - x0 + FOV_W, int(pos["y"].max()) - y0 + FOV_H
    canvas = np.zeros((h, w, 3), dtype=np.uint8)
    for fov, r in pos.iterrows():
        f = flat_dir(section) / "CellComposite" / f"CellComposite_F{int(fov):03d}.jpg"
        if not f.exists():
            continue
        img = np.asarray(Image.open(f).convert("RGB"))
        ox, oy = int(r["x"]) - x0, int(r["y"]) - y0  # a row of a mixed-type frame comes back as floats
        canvas[oy : oy + img.shape[0], ox : ox + img.shape[1]] = img[::-1]  # image rows run down, local y runs up (see boundaries)
    hh, ww = (h // REDUCE) * REDUCE, (w // REDUCE) * REDUCE
    small = canvas[:hh, :ww].reshape(hh // REDUCE, REDUCE, ww // REDUCE, REDUCE, 3).mean(axis=(1, 3)).astype(np.uint8)
    tifffile.imwrite(out, small, tile=(512, 512), compression="zlib", photometric="rgb")
    return x0 * PX, y0 * PX


def boundaries(section: str, pos: pd.DataFrame, slide: int, keep: set[str]) -> tuple[pa.Table, float]:
    """Every cell's outline from its FOV's label mask (uint16, the cell number within the FOV), as global pixels.
    Also returns the median distance between a mask's centroid and the cell table's centre, a check that the
    masks and the table use the same axes."""
    ids, xs, ys, offsets = [], [], [], []
    meta = pd.read_csv(flat_dir(section) / f"{section}_metadata_file.csv").set_index(["fov", "cell_ID"])
    for fov, r in pos.iterrows():
        f = flat_dir(section) / "CellLabels" / f"CellLabels_F{int(fov):03d}.tif"
        if not f.exists():
            continue
        labels = tifffile.imread(f)
        for region in regionprops(labels):
            cid = f"c_{slide}_{int(fov)}_{region.label}"
            if cid not in keep:
                continue
            r0, c0, r1, c1 = region.bbox
            crop = np.pad(labels[r0:r1, c0:c1] == region.label, 1)
            rings = find_contours(crop.astype(np.uint8), 0.5)
            if not rings:
                continue
            ring = max(rings, key=len)
            if len(ring) > MAX_VERTICES:
                ring = ring[np.linspace(0, len(ring) - 1, MAX_VERTICES).astype(int)]
            ids.append(np.full(len(ring), cid, dtype=object))
            # CosMx local coordinates count y upwards from the bottom of the FOV; image rows count down from the top
            xs.append(ring[:, 1] + c0 - 1 + int(r["x"]))
            ys.append(int(r["y"]) + FOV_H - (ring[:, 0] + r0 - 1))
            if (int(fov), region.label) in meta.index and len(offsets) < 2000:
                m = meta.loc[(int(fov), region.label)]
                offsets.append(np.hypot(region.centroid[1] - m["CenterX_local_px"], FOV_H - region.centroid[0] - m["CenterY_local_px"]))
    table = pa.table({"cell_id": np.concatenate(ids), "vertex_x": np.concatenate(xs), "vertex_y": np.concatenate(ys)})
    return table, float(np.median(offsets)) if offsets else float("nan")


def main() -> None:
    section = sys.argv[1]
    if section not in SECTIONS:
        sys.exit(f"section must be one of {SECTIONS}")
    types = pd.read_csv(DEST / "cell_types.csv")
    slide = int(types.loc[types["section"] == section, "slide_ID_numeric"].iloc[0])
    out = DEST / section
    out.mkdir(parents=True, exist_ok=True)
    adata = cells_and_counts(section, slide)
    adata.write_h5ad(out / "adata.h5ad")
    pos = fov_positions(section)
    tx, ty = composite(section, pos, out / "composite.tif")
    table, offset = boundaries(section, pos, slide, set(adata.obs_names))
    pq.write_table(table, out / "cell_boundaries.parquet")
    print(f"{section}: {adata.n_obs:,} cells x {adata.n_vars} genes, {adata.obs['cell_type'].nunique()} cell types, {len(pos)} FOVs, {table.num_rows:,} boundary vertices")
    print(f"  mask centroids sit {offset:.1f} px from the table's centres (should be a pixel or two)")
    print(f"  images: pixel_size: {PX * REDUCE:.2f}  translate: [{tx:.2f}, {ty:.2f}]   # the FOV bounding box's corner, microns")


if __name__ == "__main__":
    main()
