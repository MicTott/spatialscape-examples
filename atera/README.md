# Atera whole-transcriptome previews (10x Genomics)

Two FFPE sections from the preview datasets 10x published with the Atera instrument (launched April 2026):
human breast cancer and human cervical cancer, run with the preproduction whole-transcriptome assay (about
18,000 genes per cell in situ). Sources: https://www.10xgenomics.com/datasets/atera-wta-ffpe-human-breast-cancer
and https://www.10xgenomics.com/datasets/atera-wta-ffpe-human-cervical-cancer (CC BY 4.0). 10x labels both as
preview data that the final workflow may replace. The `_outs.zip` archives have the Xenium Onboard Analysis layout
(`cell_feature_matrix.h5`, `cells.parquet`, `analysis.zarr.zip`, `cell_boundaries.parquet`, `transcripts.parquet`,
`morphology_focus/` as a four-channel OME-TIFF), so the same `common/xenium.py` prepares them; only the scale differs
(the breast transcripts table alone is 10 GB of Parquet).

What the app shows: two sections at whole-transcriptome depth, the four-channel morphology image at the scan's full
resolution (0.2125 µm per pixel; `max_size:` in `dataset.yaml` would keep a coarser level, the H&E waits for an
alignment), cell and nucleus shapes, every transcript, and 10x's cell groups; the dataset that tests the molecule
tiler and the image pyramid an order of magnitude past Xenium.

| Step | Where, on a cluster | What | Cost |
|---|---|---|---|
| `download.sh` | transfer node | `_outs.zip` of each section (55 GB + 89 GB), the breast H&E (18 GB), the cell-group tables | ~170 GB, hours |
| `slurm/unzip.sbatch` (array of 2) | compute | checksum and unpack each archive into `outs/` | ~1 h, 160 GB more disk |
| `prepare.py` (`sbatch slurm/prepare.sbatch`, array of 2) | compute | `cell_feature_matrix.h5` + `cells.parquet` + the graph clusters → `processed/<section>/adata.h5ad` | minutes, <32 GB |
| `slurm/build.sbatch` | compute | `spatialscape build dataset.yaml` → `bundles/atera/` | 50 min on 8 CPUs, 62 GB peak of the 128 GB requested (the full-resolution image read); 25 GB of output, 17 GB of it the two image pyramids |
