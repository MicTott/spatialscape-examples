# Visium HD, mouse brain FFPE (10x Genomics public dataset)

One FFPE coronal section of mouse brain on Visium HD (Space Ranger 3.0.0), at 8 µm bins: the sequencing-based
case at bin resolution, with an H&E. Source: the `Visium_HD_Mouse_Brain` dataset on
https://www.10xgenomics.com/datasets (CC BY).

| Step | Where, on a cluster | What | Cost |
|---|---|---|---|
| `download.sh` | transfer node | the binned outputs (4.6 GB: 2, 8 and 16 µm bins), `spatial/`, the H&E | ~10 min |
| `prepare.py` | compute | the 8 µm bins: matrix + positions + graph clusters → `processed/square_008um/adata.h5ad`, `spatial/` beside it (its `scalefactors_json.json` carries microns per pixel) | 2 min, 16 GB |
| `slurm/build.sbatch` | compute | `spatialscape build dataset.yaml` → `bundles/visium-hd-mouse-brain/` | minutes |

The 2 µm bins (several million) are left out of the app; 8 µm is what the viewer draws well at this scale.
