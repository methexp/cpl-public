
library(cplmodels)

readRDS("studies/cpl8/model_objects/phdm_200.rds") |>
  lapply(
    FUN = extend
    , add.monitor = c("pp_rt", "alpha", "delta", "tau", "beta")
    , adapt  = n_samples(1e3L)
    , sample = n_samples(8e2L, debug = 2e1L)
    , thin   = n_samples(2e1L, debug = 1e0L)
    , method = "rjparallel" # do not write to disk
  )|>
  saveRDS(file = "studies/cpl8/model_objects/phdm_200-pp.rds")

