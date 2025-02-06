library(cplmodels)
library(papaja)
library(qs)

data <- readRDS("studies/cpl8/data/data-excluded.rds")
data <- subset(
  data
  , !is.na(response_time) & response_time < 2 & response_time > .020 &
    tix > 4L & !previous_error & !previous_deadline_exceeded
)
data$stimulus_location_regularity <- factor(
  data$stimulus_location_regularity
  , levels = c(FALSE, TRUE)
  , labels = c("nonregular", "regular")
)

models <- split(data, f = data[, c("material", "instructions")]) |>
  lapply(FUN = function(x){

    is_probabilistic <- x$material[[1]] == "probabilistic"
    phdm_200(
      data = droplevels(tinylabels::unlabel(x))
      , id = "sid"
      , block = "block_pair"
      , stimulus_regularity = "three_levels"
      , response_regularity = "response_regularity"
      , rt = "response_time"
      , error = "error"
      , adapt  = n_samples(2e2L, debug = 1e2L)
      , burnin = n_samples(2e3L, debug = 1e2L)
      , sample = n_samples(2e3L, debug = 1e2L)
      , thin   = n_samples(5e0L, debug = 1e0L)
      , factors = list(
        alpha = if(is_probabilistic) NULL else c("block_pair", "context")
        , theta = c("block_pair", "three_levels")
        , xi = c("block_pair", "_identity") # if(is_probabilistic) c("block_pair", "_identity") else c("block_pair", "context")
      )
      # , model_file = "stretched-exponential.jags"
      , model_file = "ddm-full.jags"
      # , model_file = "hierarchical-shared.jags"
      , assign_values = list(
        # wiener_rt = rep(NA, nrow(x))
        # , b.beta.lower_limit = rep(0, 2)
        # , b.beta.upper_limit = rep(1, 2)
        # , b.beta.scale = rep(4, 2)
        # , b.beta.sqinv_shape = rep(1, 2)
        # , b.beta.shape = rep(1, 2)
        # , b.beta.scale = rep(4, 2)
        # , b.beta.mean = c(.1, 0)
        # , b.beta.lower_limit = c(.2, 0)
        # , b.beta.mean = c(0, .2)
        # , b.nu.lower_limit = rep(0, 2)
        # , b.nu.mean = rep(, 2)
        # , b.nu.shape = rep(1, 2)
        # , b.nu.scale = rep(4, 2)
        # , b.theta.lower_limit = c(.2, 0)
        # , b.theta.mean = c(-.5, .05)
        # , b.theta.scale = rep(4, 2)
        # , b.theta.shape = rep(1, 2)
      )
      , monitor = c(
        as.vector(outer(c("b.alpha.", "b.beta.", "b.xi.", "b.nu.", "b.theta."), c("mean", "scale", "shape", "upper_limit"), FUN = paste0))
        , "location_effect"
        , "sbeta"
      )
      # , debug = TRUE
      # , method = "rjparallel"
    )
  }
)

dir.create("studies/cpl8/model_objects", showWarnings = FALSE)
qsave(models, file = "studies/cpl8/model_objects/phdm_200.qs")
