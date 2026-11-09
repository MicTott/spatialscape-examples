# Spatial ATAC + RNA co-profiling, mouse brain (Zhang et al. 2023, Nature)

Spatial epigenome–transcriptome co-profiling (Zhang, Deng, ... Fan 2023): chromatin accessibility and gene
expression measured in the same 20 µm pixels of mouse brain sections, plus a 50 µm human brain section.
GEO superseries GSE205055 (ATAC subseries GSE205052, RNA subseries GSE205054, CUT&Tag GSE205051). Per section:
an ATAC fragment file, an RNA count matrix (genes x pixels, tsv) and a Space Ranger-style `spatial/` folder
(pixel positions and the tissue image).

What the app will show: the first spatial multiome case for spatialscape: RNA on the pixels, pseudobulk ATAC
tracks per cluster in the genome panel from the fragment files, and (once the second-matrix feature lands)
the ATAC peaks as features next to the genes.

| Sample | ATAC fragments | RNA matrix | pixels |
|---|---|---|---|
| MouseBrain_20um (50 x 50 barcodes) | GSM6204623 (345 MB) | GSM6204636 | 2,500 |
| MouseBrain_20um rep2 | GSM6758284 (486 MB) | GSM6753041 | 2,500 |
| MouseBrain_20um, 100 x 100 barcodes | GSM6758285 (1.5 GB) | GSM6753043 | 10,000 |
| HumanBrain_50um | GSM6206884 (456 MB) | GSM6206885 | 2,500 |

| Step | Where | What | Cost |
|---|---|---|---|
| `download.sh` | transfer node | the files above from GEO's FTP (over HTTPS), ~2.9 GB | minutes |
| `prepare.py` | compute | RNA matrix + positions → one h5ad per section; clusters for the tracks | minutes |
| `slurm/build.sbatch` | compute | `spatialscape build dataset.yaml` with `tracks:` from the fragments → `bundles/spatial-atac-rna-mouse-brain/` | tens of minutes |
