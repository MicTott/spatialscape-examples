# The spatialLIBD DLPFC SpatialExperiment (Maynard et al. 2021: 12 Visium sections, 3 donors, manual layer labels),
# fetched from ExperimentHub and saved as raw/spe_dlpfc.rds. This is the only step before `spatialscape build`:
# the yaml points at the .rds and the build reads it directly.
#   Rscript download.R
suppressMessages(library(spatialLIBD))
spe <- fetch_data("spe")   # about 400 MB, cached by ExperimentHub
dir.create("raw", showWarnings = FALSE)
saveRDS(spe, "raw/spe_dlpfc.rds")
cat(sprintf("raw/spe_dlpfc.rds: %d genes x %d spots, %d sections\n", nrow(spe), ncol(spe), length(unique(spe$sample_id))))
