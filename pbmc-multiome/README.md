# Human PBMCs, 10x Multiome: RNA + ATAC in the same nuclei (10x Genomics public dataset)

Peripheral blood mononuclear cells of a healthy donor, granulocytes removed by cell sorting, profiled with
Chromium Single Cell Multiome ATAC + Gene Expression: every nucleus has a transcriptome and an accessibility
profile. Source: the `pbmc_granulocyte_sorted_10k` dataset (Cell Ranger ARC 2.0.0) on
https://www.10xgenomics.com/datasets (CC BY). 10x publishes no cell labels with it, so the clustering and the
cell types here are computed by `prepare.py`.

What the app shows: the one example that is not a tissue section. The RNA UMAP and the ATAC UMAP of the same
11,577 nuclei side by side, with one cell type legend for both; pseudobulk ATAC tracks per cell type in the genome
panel, built from the fragment file; and, beside the genes, three more kinds of feature in tabs of their own: gene
activity from the ATAC, marker-set scores, and the 20,000 most variable peaks.

## Reproduce the app

Needs the environment (`bash ../setup_env.sh`, then `source ../env/bin/activate`). Then, in this folder:

```bash
bash build.sh
spatialscape serve bundles --open
```

`build.sh` runs these four commands, which you can also run one at a time:

| Command | What it does | Cost on a laptop (M-series) |
|---|---|---|
| `bash download.sh` | the filtered matrix (genes and peaks), the peak annotation, the per-barcode metrics and the ATAC fragment file → `raw/` | 2.7 GB, 2 min on a fast line; a file that is there is skipped |
| `python prepare.py` | QC, the RNA UMAP and Leiden clusters, the ATAC UMAP (TF-IDF, LSI), cell types, gene activity, scores and peaks → `processed/pbmc.h5ad` | 1.5 min, 12.7 GB peak; 1.3 GB of output |
| `spatialscape build dataset.yaml` | the two samples, and the tracks: the fragment file is streamed once and pooled per cell type → `bundles/pbmc-multiome/` | 5.5 min, most of it the 209 million fragments; 1.3 GB of output |
| `spatialscape validate bundles/pbmc-multiome` | checks the bundle against the format | seconds |

`bash ../fetch_processed.sh pbmc-multiome` fetches `processed/pbmc.h5ad` from the Zenodo record, which replaces
the prepare step only: the yaml's `tracks:` block reads `raw/atac_fragments.tsv.gz` (2.4 GB of the download), so
run `download.sh` as well, or remove the `tracks:` line to build the two UMAPs without the genome panel.

## Notes

The cell types are a quick annotation, not a curated one: each Leiden cluster of the RNA takes the name of the
marker set (ten sets, listed at the top of `prepare.py`) with the highest mean score in it. The scores themselves
are in the app under "Marker-set scores", so the call for every cluster can be checked by eye.

The gene track is UCSC's RefSeq table for hg38, which `build` downloads once (8 MB, kept in
`~/.cache/spatialscape`). To draw the exact gene models the matrix was counted against, point `genes:` in the
yaml's `tracks:` block at `genes/genes.gtf.gz` of the Cell Ranger ARC reference (GRCh38-2020-A).
