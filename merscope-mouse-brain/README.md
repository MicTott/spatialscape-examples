# MERSCOPE mouse brain receptor map (Vizgen)

Vizgen's open-access MERFISH Mouse Brain Receptor Map, run on the MERSCOPE platform: three coronal slices, three
replicates each, a 483-gene panel of receptors and markers, with cell segmentation, every detected transcript and
DAPI / polyT mosaic images. Source: the public Google Cloud bucket `vizgen-mouse-brain-map` (1.7 TB; listed and
read over plain HTTPS, no account), described at https://info.vizgen.com/mouse-brain-map. Licence: Vizgen's
open-access data terms [to confirm on that page before publishing the app].

What the app will show: three coronal slices side by side (one replicate each), cells by Vizgen's
segmentation with their boundaries, all 483 genes, every transcript, and the DAPI and polyT images at one z plane.

| Step | Where | What | Cost |
|---|---|---|---|
| `tools/files_from_bucket.py` | anywhere | lists the bucket and writes `files.tsv` (what to fetch) | seconds |
| `download.sh` | transfer node | per slice: `cell_by_gene.csv`, `cell_metadata.csv`, `detected_transcripts.csv` (3.6 GB), `cell_boundaries/*.hdf5` (5.3 GB), two 11 GB mosaics and the transform | ~95 GB, hours |
| `prepare.py` (`sbatch slurm/prepare.sbatch`, array of 3) | compute | AnnData per slice from the matrix and cell table; the boundaries from HDF5 into one Parquet table | ~15 min, 16 GB |
| `mosaics.py` (`sbatch slurm/mosaics.sbatch`, array of 3) | compute | the two 10 GB single-strip mosaics reduced 4x into tiled TIFFs | ~10 min, 40 GB |
| `slurm/build.sbatch` | compute | `spatialscape build dataset.yaml` → `bundles/merscope-mouse-brain/` | tens of minutes |

Coordinates are microns throughout (`global_x`, `global_y` in the transcripts, `center_x`/`center_y` in the cell
table); the mosaics are placed with `micron_to_mosaic_pixel_transform.csv` (about 9.2 px per µm, with an offset).
