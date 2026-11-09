# Xenium Prime 5K, mouse brain, coronal (10x Genomics public dataset)

One fresh-frozen coronal section run on Xenium Prime 5K (5,006 genes), Xenium Onboard Analysis 3.0.0.
Source: https://www.10xgenomics.com/datasets/xenium-prime-ffpe-mouse-brain (the `Xenium_Prime_Mouse_Brain_Coronal_FF`
bundle). Licence: Creative Commons Attribution, as 10x publishes its datasets.

What the app shows: 63k cells coloured by 10x's graph clusters and 5,006 genes; the 4-channel morphology image
(DAPI, boundary, interior RNA, interior protein) at 0.85 µm per pixel with per-channel switches; cell shapes, the
nucleus boundaries as a second segmentation, and every decoded transcript once zoomed in.

| Step | Where, on a cluster | What | Cost |
|---|---|---|---|
| `download.sh` | transfer node | the `_outs.zip` (13.3 GB), unzipped into `raw/outs/` | ~15 min, 27 GB |
| `prepare.py` (`sbatch slurm/prepare.sbatch`) | compute | `cell_feature_matrix.h5` + `cells.parquet` + the graph clusters → `processed/adata.h5ad` | 2 min, 8 GB |
| `slurm/build.sbatch` | compute | `spatialscape build dataset.yaml` → `bundles/xenium-mouse-brain/` | ~5 min, <16 GB |

`dataset.yaml` points at the outs folder for the image, boundaries and transcripts, and at the h5ad for the cells.
