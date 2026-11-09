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
| `spatialscape build dataset.yaml` | laptop | reads the `.rds` once into `bundles/.cache/` (the H&E of each section is fetched from the URLs the object carries), then builds one sample per `sample_id` → `bundles/visium-human-dlpfc/` | about 2 min in all (conversion, then a 49 s build), 2.9 GB peak; 1.0 GB of output |

```bash
Rscript download.R
spatialscape build dataset.yaml
spatialscape serve bundles --open
```

Without R: `bash ../fetch_processed.sh visium-human-dlpfc` fetches the same `.rds` from the Zenodo record into
`raw/` (for this dataset the processed object is the raw one).

The object carries SpaceRanger's low-resolution H&E (600 px a side, about 16 µm per pixel), which is what the app
shows under the spots. The paper's bucket also serves the 2,000 px `tissue_hires_image.png` of each section; to use
those, download them into `raw/images/` and list them under `images:` in the yaml with their scale.
