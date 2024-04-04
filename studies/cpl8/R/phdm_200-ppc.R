

library(cplmodels)

readRDS(file = "studies/cpl8/model_objects/phdm_200-pp.rds") |>
  lapply(FUN = function(x) {
    ppc(x, factors = c(unique(unlist(x$factors)), "sid"), breaks = seq(0.05, .95, .05))
  }) |>
  saveRDS(file = "studies/cpl8/model_objects/phdm_200-ppc.rds")

