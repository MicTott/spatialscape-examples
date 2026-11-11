# Human lymph node, PhenoCycler: spatial proteomics (Meyer-Bender et al., BioImage Archive S-BIAD2100)

Three tissue-microarray cores of reactive human lymph node, imaged with a 56-antibody panel on the Akoya
PhenoCycler and analysed with the [spatialproteomics](https://sagar87.github.io/spatialproteomics) package: per
core a 56-channel image (3,000 × 3,000 px at 0.5 µm), a segmentation mask, each marker's intensity per cell, and
the authors' gated cell types and cellular neighbourhoods. Source: "Spatial profiling of reactive lymph nodes and
various B cell Non-Hodgkin lymphomas", BioImage Archive [S-BIAD2100](https://doi.org/10.6019/S-BIAD2100) (CC0),
which holds 250 such cores and five whole slides; these three (`LN_11_1`, `LN_13_1`, `LN_24_1`) are the ones the
package's tutorials use.

What the app shows: the one example with proteins instead of transcripts. 46,671 cells with their outlines, coloured
by cell type, neighbourhood or any of the 56 markers (the markers take the place of genes), over the stains: every
channel is listed and any six draw at once.

## Reproduce the app

Needs the environment (`bash ../setup_env.sh`, then `source ../env/bin/activate`). Then, in this folder:

```bash
bash build.sh
spatialscape serve bundles --open
```

`build.sh` runs these three commands, which you can also run one at a time. There is no prepare step: the yaml
reads each spatialproteomics object as it is.

| Command | What it does | Cost on a laptop (M-series) |
|---|---|---|
| `bash download.sh` | the three cores, one zipped Zarr object each → `raw/LN_*.zarr` | 660 MB down, 1.0 GB unpacked, under a minute; a core that is there is skipped |
| `spatialscape build dataset.yaml` | per core: intensities and annotations, cell outlines traced from the label mask, the 56-channel image as a pyramid → `bundles/phenocycler-lymph-node/` | 22 s, 2.2 GB peak; 331 MB of output |
| `spatialscape validate bundles/phenocycler-lymph-node` | checks the bundle against the format | seconds |

## Notes

`download.sh` takes the cores from the example-data share of the spatialproteomics package, which is fast. The
archive serves the same cores under `data_for_publication/tmas/` of S-BIAD2100, more slowly; any of its other
cores (lymphoma entities are listed in `derived_data/tma_metadata.csv`) drops into `raw/` and is picked up by the
yaml's glob, as long as it carries the columns named under `fields:`.

The image is the scan (`_image_raw`). The viewer opens with the first six channels of the panel; pick others in
the Image group, for example DAPI, CD20, CD3, CD68, Ki-67 and CD31 (`&ch=DAPI|CD20|CD3|CD68|Ki-67|CD31` in the
address).
