"""A reduced, tiled copy of each slice's DAPI and polyT mosaic, for the build to read.

Vizgen writes a mosaic as one 89,000 x 61,000 pixel plane in a single strip (10 GB each), which spatialscape
refuses to read whole. This averages 4 x 4 pixel blocks (0.109 -> 0.435 um per pixel, still finer than the
0.85 um the viewer keeps) and writes a tiled TIFF of about 650 MB per channel. The top-left corner stays where it
was, so `translate` in dataset.yaml is unchanged and `pixel_size` is four times the transform's.

    python mosaics.py Slice1_Replicate1
"""
import sys
from pathlib import Path

import numpy as np
import tifffile

HERE = Path(__file__).resolve().parent  # this dataset's folder
RAW = HERE / "raw"
DEST = HERE / "processed"
FACTOR = 4
CHANNELS = ["DAPI", "polyT"]


def reduce(src: Path, dst: Path) -> None:
    plane = tifffile.imread(src)  # the whole strip; about 11 GB of uint16
    h, w = (plane.shape[0] // FACTOR) * FACTOR, (plane.shape[1] // FACTOR) * FACTOR
    small = plane[:h, :w].reshape(h // FACTOR, FACTOR, w // FACTOR, FACTOR).mean(axis=(1, 3)).astype(np.uint16)
    del plane
    tifffile.imwrite(dst, small, tile=(512, 512), compression="zlib", photometric="minisblack")
    print(f"  {src.name}: {small.shape[1]} x {small.shape[0]} px -> {dst}")


def main() -> None:
    slice_ = sys.argv[1]
    out = DEST / slice_
    out.mkdir(parents=True, exist_ok=True)
    for ch in CHANNELS:
        reduce(RAW / slice_ / "images" / f"mosaic_{ch}_z3.tif", out / f"mosaic_{ch}_z3_4x.tif")


if __name__ == "__main__":
    main()
