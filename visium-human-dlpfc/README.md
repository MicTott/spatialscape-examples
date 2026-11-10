# Human DLPFC, Visium (Maynard et al. 2021, spatialLIBD)

Twelve Visium sections of human dorsolateral prefrontal cortex from three donors, two positions each in
duplicate, with the manual cortical layer annotation (L1–L6, WM) of Maynard et al., *Nature Neuroscience* 2021.
Source: the `spe` object of the [spatialLIBD](https://bioconductor.org/packages/spatialLIBD) Bioconductor
package (ExperimentHub), 33,538 genes × 47,681 spots, with the low-resolution H&E of each section. Licence: the
package's (Artistic-2.0); the data are the paper's.

This is the example to read first: it starts from an R object and has no prepare step.

## Reproduce the app

Needs R with spatialLIBD installed, and spatialscape (`bash ../setup_env.sh` makes the environment; `source
../env/bin/activate` enters it). Then, in this folder:

```bash
bash build.sh
spatialscape serve bundles --open
```

`build.sh` runs these four commands, which you can also run one at a time:

| Command | What it does | Cost on a laptop (M-series) |
|---|---|---|
| `Rscript download.R` | `spatialLIBD::fetch_data("spe")` → `raw/spe_dlpfc.rds` | 400 MB, minutes; skipped when the file is there |
| `spatialscape init raw/spe_dlpfc.rds --id visium-human-dlpfc -o dataset.init.yaml` | writes the menu of what the object holds: every colData column with its type and levels, guessed field mappings, the metadata that is constant within each sample | seconds |
| `spatialscape build dataset.yaml` | reads the `.rds` once into `bundles/.cache/` (the H&E of each section is fetched from the URLs the object carries), then builds one sample per `sample_id` → `bundles/visium-human-dlpfc/` | 54 s, 4.2 GB peak; 1.0 GB of output |
| `spatialscape validate bundles/visium-human-dlpfc` | checks the bundle against the format | seconds |

`dataset.yaml` (committed, 34 lines) is what we kept of the 100-line menu `init` writes: the layer labels as the
domain, three QC columns, the donor / position / replicate metadata to split the view by, SNAP25 as the opening
gene, and a four-column grid so that each row is one donor. `diff dataset.init.yaml dataset.yaml` after a run
shows exactly those choices; everything else in the app is the object as it is.

Without R: `bash ../fetch_processed.sh visium-human-dlpfc` fetches the same `.rds` from the Zenodo record into
`raw/` (for this dataset the processed object is the raw one), then `bash build.sh` runs the other three steps.

## Notes

The object carries SpaceRanger's low-resolution H&E (600 px a side, about 16 µm per pixel), which is what the app
shows under the spots. The paper's bucket also serves the 2,000 px `tissue_hires_image.png` of each section; to use
those, download them into `raw/images/` and list them under `images:` in the yaml with their scale.
