# spatialscape examples

Public spatial transcriptomics datasets built into [spatialscape](https://github.com/MicTott/spatialscape) apps:
one folder per dataset with the script that fetches the published files, the script (when one is needed) that
turns them into an AnnData, the `dataset.yaml` that describes the app, and a README with the source, the licence
and what each step costs. Nothing is edited by hand: every app rebuilds from these files. Start with `visium-human-dlpfc`, which
builds straight from an R object with no prepare step.

| Folder | Technology | Scale | Source | Prepare step |
|---|---|---|---|---|
| `visium-human-dlpfc` | Visium, H&E, manual layer labels | 12 sections, 47,681 spots | spatialLIBD (Maynard et al. 2021) | none: the yaml reads the SpatialExperiment `.rds` |
| `visium-cytassist-mouse-brain` | Visium CytAssist, H&E | 1 section, 2,310 spots | 10x Genomics (CC BY) | reshapes Space Ranger files |
| `visium-hd-mouse-brain` | Visium HD, 8 µm bins, H&E | 1 section, 394k bins | 10x Genomics (CC BY) | reshapes Space Ranger files |
| `xenium-mouse-brain` | Xenium Prime 5K: image, shapes, nuclei, transcripts | 1 section, 63k cells, 5,006 genes | 10x Genomics (CC BY) | reshapes the outs folder |
| `atera` | Atera whole-transcriptome in situ: 4-channel morphology, shapes, transcripts | 2 sections, 888k cells, 18k genes, 1.66 billion transcripts | 10x Genomics previews (CC BY) | reshapes the outs folders |
| `merscope-mouse-brain` | MERSCOPE: boundaries, transcripts, DAPI and polyT mosaics | 3 slices, 233k cells, 483 genes | Vizgen public bucket | boundaries from HDF5, a Leiden clustering, mosaics reduced |
| `cosmx-nsclc` | CosMx SMI: the paper's cell types and niches, boundaries, transcripts, composites | 8 sections, 800k cells, 960 genes | NanoString public bucket (He et al. 2022) | cell types from the Giotto object, composites stitched, boundaries traced |
| `spatial-atac-rna-mouse-brain` | spatial ATAC + RNA: RNA on 20 µm pixels, ATAC tracks per cluster | 3 sections, 14k pixels | GEO GSE205055 (Zhang et al. 2023) | tsv matrix to AnnData, a Leiden clustering |
| `abc-atlas` | whole mouse brain: 59 MERFISH sections and all 10x nuclei on Allen's UMAP | 4.0 M cells + 4.0 M nuclei | Allen Brain Cell Atlas (CC BY-NC) | per-section slices of a 4 M-cell matrix; a streamed concat of 106 GB |

## Reproduce an app

Three commands, from a clone of this repository with the environment active (`bash setup_env.sh`, then
`source env/bin/activate`):

```bash
bash fetch_processed.sh xenium-mouse-brain        # the processed objects from the Zenodo record
spatialscape build xenium-mouse-brain/dataset.yaml
spatialscape serve xenium-mouse-brain/bundles --open
```

`fetch_processed.sh` gives you what the prepare step would have made, so you skip the raw download. Images,
boundaries and transcripts that the yaml takes from the published files (`raw/`) are optional parts of a sample:
without them the app has the cells and the genes; with `download.sh` run as well, it has everything.

To go from the published files instead, each folder's README lists the steps; they are always the same shape:

```bash
cd xenium-mouse-brain
bash download.sh            # raw/        the files as published, sizes and checksums checked
python prepare.py           # processed/  an AnnData (and tables) the yaml points at
spatialscape build dataset.yaml
```

From an R object there is no prepare step: `visium-human-dlpfc/build.sh` downloads the SpatialExperiment, runs
`spatialscape init` on it (the menu of what it holds) and builds the committed yaml, in under two minutes.

Every dataset's `dataset.yaml` is written by hand and reads top to bottom: the dataset, its fields, then one
entry per sample pointing at `processed/` and `raw/` beside it. Edit it and run `build` again; only what changed
is rebuilt.

## All of them as one gallery

`site.yaml` lists every dataset. `spatialscape site build site.yaml` builds the ones that are missing or stale
and writes `site/`, a folder any static host serves; `spatialscape serve site` shows it locally.

## On a cluster

The `slurm/` folder in each dataset has the same steps as SLURM jobs, with the memory and time each one needed.
Submit them from the dataset's folder with the environment active:

```bash
cd atera && sbatch slurm/prepare.sbatch && sbatch --dependency=singleton slurm/build.sbatch
```

Downloads run wherever large transfers are allowed (a transfer node); everything else is a job. If the data has
to live elsewhere (a scratch file system), make `raw/` and `processed/` symbolic links to it; the scripts only ever
address those two folders.

## Layout

```
<dataset>/
  README.md        source, licence, what the scripts do, cost (time, memory, disk)
  download.sh      the published files -> raw/
  prepare.py       raw/ -> processed/ (absent where the yaml reads the published files directly)
  dataset.yaml     the app: paths relative to this folder
  slurm/           the same steps as SLURM jobs
  tools/           one-off helpers (file manifests, palettes, checks), not needed to reproduce
  raw/ processed/ bundles/ logs/     data and outputs, never committed
common/            readers shared by the prepare scripts: 10x matrices, Space Ranger spatial/, Xenium outs, Leiden
setup_env.sh       the Python environment (env/), pinned to the spatialscape release the apps were built with
site.yaml          the gallery of all of them
```

## Data

The processed objects of every dataset except `abc-atlas` are archived with this repository in one Zenodo record
(DOI to come), each as `<dataset>-processed.tar` with the `dataset.yaml` it was built with and a `MANIFEST.sha256`.
The Allen atlas is 215 GB of processed objects and rebuilds from its scripts in about a day of cluster time; its raw
data are Allen's own public S3 bucket. Each dataset's licence is the publisher's, stated in its README; the scripts
here are MIT.
