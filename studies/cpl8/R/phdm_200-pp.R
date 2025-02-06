
library(cplmodels)
library(qs)

qread("studies/cpl8/model_objects/phdm_200.qs") |>
  lapply(
    FUN = extend
    , add.monitor = c("pp_rt", "alpha", "delta", "tau", "beta")
    , adapt  = n_samples(1e3L)
    , sample = n_samples(5e2L, debug = 2e1L)
    , thin   = n_samples(4e1L, debug = 1e0L)
    , method = "rjparallel" # do not write to disk
  ) |>
  qsave(file = "studies/cpl8/model_objects/phdm_200-pp.qs")
