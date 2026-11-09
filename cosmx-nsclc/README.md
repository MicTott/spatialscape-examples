# CosMx SMI non-small-cell lung cancer (NanoString, He et al. 2022)

The eight FFPE lung tumour sections of the CosMx SMI paper (He et al., *Nat. Biotechnol.* 2022: Lung5 in three
replicates, Lung6, Lung9 in two replicates, Lung12, Lung13), 960-plex RNA, about 800,000 cells. Source: NanoString's
public S3 bucket `nanostring-public-share` (`SMI-Compressed/`, listed and read without an account). Licence: as
stated in the bucket's `SMI-ReadMe.html` [to confirm before publishing the app].

What the app will show: eight sections on one canvas, cells with the paper's cell types, all 960 genes, every
transcript (with its nuclear / cytoplasmic / membrane compartment), and the per-FOV composite images stitched
into one picture per section.

| Step | Where, on a cluster | What | Cost |
|---|---|---|---|
| `download.sh` | transfer node | `All SMI Flat data.tar.gz` (11.3 GB) and the Giotto object (0.9 GB) | ~12 GB, under an hour |
| `slurm/unpack.sbatch` | compute | unpacks both archives | minutes |
| `celltypes.py` | compute (srun, 32 GB) | the paper's cell types and niches out of the Giotto object into `cell_types.csv` | 2 min |
| `prepare.py` (`sbatch slurm/prepare.sbatch`, array of 8) | compute | AnnData per section from `exprMat`, `metadata` and `cell_types.csv`; the FOV composites stitched into one image (2x reduced) from `fov_positions`; boundaries traced from the label masks; prints each composite's `translate` for `dataset.yaml` | 10–25 min per section, <24 GB |
| `slurm/build.sbatch` | compute | `spatialscape build dataset.yaml` → `bundles/cosmx-nsclc/` | tens of minutes |

Coordinates are global pixels at 0.18 µm per pixel (`x_global_px`, `y_global_px`); `dataset.yaml` sets
`microns: { microns_per_unit: 0.18 }`. A transcript with `cell_ID` 0 is unassigned; `CellComp` says whether it
sits in the nucleus, cytoplasm or membrane. Within a FOV, CosMx counts local y upwards from the bottom edge while
the images' rows count down from the top, so the label masks and composites are flipped into the coordinates'
orientation; `prepare.py` checks this by comparing mask centroids with the cell table (about 3 px apart).
