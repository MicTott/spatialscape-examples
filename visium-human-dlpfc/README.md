# Human DLPFC, Visium (Maynard et al. 2021, spatialLIBD)

Twelve Visium sections of human dorsolateral prefrontal cortex from three donors, two positions each in
duplicate, with the manual cortical layer annotation (L1–L6, WM) of Maynard et al., *Nature Neuroscience* 2021.
Source: the `spe` object of the [spatialLIBD](https://bioconductor.org/packages/spatialLIBD) Bioconductor
package (ExperimentHub), 33,538 genes × 47,681 spots, with the low-resolution H&E of each section. Licence: the
package's (Artistic-2.0); the data are the paper's.

This is the example to read first: it starts from an R object and has no prepare step. `spatialscape init` wrote
the first `dataset.yaml` as a menu of what the object holds; what is kept of it is in the file (the layer labels as
the domain, three QC columns, the donor and position metadata).

| Step | Where | What | Cost |
|---|---|---|---|
| `download.R` | anywhere with R and spatialLIBD | `fetch_data("spe")` → `raw/spe_dlpfc.rds` | 400 MB, minutes |
| `spatialscape build dataset.yaml` | laptop | reads the `.rds` (once, into `bundles/.cache/`), one sample per `sample_id`, the H&E and scale from the object → `bundles/visium-human-dlpfc/` | minutes, under 8 GB |

```bash
Rscript download.R
spatialscape build dataset.yaml
spatialscape serve bundles --open
```

Without R: `bash ../fetch_processed.sh visium-human-dlpfc` fetches the same `.rds` from the Zenodo record into
`raw/` (for this dataset the processed object is the raw one).
