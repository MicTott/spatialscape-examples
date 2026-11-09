# Allen Brain Cell Atlas, whole mouse brain (MERFISH + 10x snRNA-seq)

The whole adult mouse brain atlas (Yao et al. 2023; Zhang et al. 2023): 4.0 M cells on 59 coronal MERFISH sections
with a 500-gene panel, and 4 M+ nuclei by 10x (v2 and v3 chemistries) mapped to the 5,322-cluster taxonomy, with
Allen's published UMAPs and CCF parcellations. Source: the public S3 bucket `allen-brain-cell-atlas` (release
20250531; https://alleninstitute.github.io/abc_atlas_access). Licence: CC BY-NC 4.0 for the 10x and MERFISH data.

What the app shows: every MERFISH section on one canvas with the taxonomy's own colours at four levels (class,
subclass, supertype, cluster) and the CCF parcellation; all 4.04 M 10x nuclei as one embedding on Allen's
whole-brain UMAP, the view the Allen site shows, with the same vocabulary; any of the 500 MERFISH genes on the
sections and all 32k genes on the nuclei.

| Step | Where | What | Cost |
|---|---|---|---|
| `tools/files_from_manifest.py` | anywhere | writes `files.tsv` from the release manifest | seconds |
| `download.sh` | transfer node | the files in `files.tsv` into `raw/` | ~160 GB, hours |
| `prepare_merfish.py` (array over sections) | compute | one h5ad per MERFISH section with cell metadata and CCF labels | per section: minutes |
| `slurm/prepare_10x_split.sbatch` (array over the 24 region matrices) | compute | cuts each `WMB-10Xv[23]-<region>-log2.h5ad` into per-neighbourhood pieces, with Allen's UMAP coordinates; skips matrices still downloading, so it can be rerun | 2–10 min per matrix, 48 GB |
| `slurm/prepare_10x_concat.sbatch` | compute | appends every piece into one `WholeBrain.h5ad` (4.04 M nuclei × 32,285 genes, 18.7 billion stored values, 140 GB) with gene symbols and Allen's whole-brain UMAP; refuses to run before every matrix is split | 1 to 2 h, <48 GB (one piece in memory at a time) |
| `slurm/build.sbatch` | compute | `spatialscape build dataset.yaml` → `bundles/abc-atlas/`; the MERFISH sections first, the nuclei once `WholeBrain.h5ad` exists | MERFISH 77 min at 16 GB; the whole-brain nuclei 8 h 59 min on the 192 GB, 2 CPU job (the sparse matrix alone is 139 GB; 23 GB of output) |

Order: `download.sh` (transfer node) → `sbatch slurm/prepare_merfish.sbatch` → `sbatch slurm/prepare_10x_split.sbatch`
(again if some matrices were still downloading) → `sbatch slurm/prepare_10x_concat.sbatch` →
`sbatch slurm/build.sbatch`. Cells whose label the 2024 metadata no longer lists (about 1,200 of 4.3 M) are left out;
labels are matched with and without the `-1` suffix the metadata adds to some of them.
