# Visium CytAssist, mouse brain FFPE (10x Genomics public dataset)

One FFPE coronal section of mouse brain on Visium CytAssist (6.5 mm capture area, Space Ranger 2.0.0), the
smallest sequencing-based case: spots, an H&E, graph clusters. Source: the `CytAssist_FFPE_Mouse_Brain_Rep1`
dataset on https://www.10xgenomics.com/datasets (CC BY).

| Step | Where, on a cluster | What | Cost |
|---|---|---|---|
| `download.sh` | transfer node | the filtered matrix, `spatial/`, the analysis folder and the full-resolution H&E (3.4 GB) | minutes |
| `prepare.py` | compute | matrix + tissue positions + graph clusters → `processed/sample/adata.h5ad`, with `spatial/` copied beside it so the H&E and scale are found on their own | 1 min |
| `slurm/build.sbatch` | compute | `spatialscape build dataset.yaml` → `bundles/visium-cytassist-mouse-brain/` | minutes |
