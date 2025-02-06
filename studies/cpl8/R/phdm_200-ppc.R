
library(cplmodels)
library(qs)
library(parallel)

cl <- makeForkCluster(nnodes = 4L)

qread(file = "studies/cpl8/model_objects/phdm_200-pp.qs") |>
  parLapply(cl = cl, fun = function(x) {
    ppc(x, factors = c(unique(unlist(x$factors)), "sid"), breaks = seq(0.05, .95, .05))
  }) |>
  qsave(file = "studies/cpl8/model_objects/phdm_200-ppc.qs")

stopCluster(cl)
