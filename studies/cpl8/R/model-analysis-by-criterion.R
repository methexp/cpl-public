
palette(wesanderson::wes_palette("Zissou1", n = 3))

library(cplmodels)
library(qs)
models <- qread(
  file.path(rprojroot::find_rstudio_root_file(), "studies", "cpl8", "model_objects", "phdm_200-by-interview.qs")
)
# models <- Filter(Negate(is.null), models)

# x <- models[[2L]]
library(runjags)


x <- models[[1]]

# models <- models[1]
model_summaries <- Map(
  nm = names(Filter(Negate(is.null), models))
  , x = Filter(Negate(is.null), models)
  , function(nm, x) {
    y <- summary(x$model, vars = ".mean") |>
      as.data.frame()
    y$parameter <- gsub(rownames(y), pattern = "^b\\.|\\.mean.*$", replacement = "")
    y$contrast  <- gsub(rownames(y), pattern = ".*mean|\\[|\\]", replacement = "")
    y$contrast[y$contrast == ""] <- 1
    y$contrast <- factor(as.integer(y$contrast), levels = 1:3, labels = c("Intercept", "nonregular vs. regular", "deterministic vs. random"))

    tmp_nm <- strsplit(nm, split = ".", fixed = TRUE)[[1L]]
    y$material <- tmp_nm[[1L]]
    y$instructions <- tmp_nm[[2L]]
    y$criterion <- tmp_nm[[3L]]
    rownames(y) <- NULL
    y
  }
) |>
  do.call(what = "rbind") |>
  within({
   material <- factor(material, levels = c("probabilistic", "mixed deterministic"))
   instructions <- factor(instructions, levels = c("sequence concealed", "sequence revealed"))
   criterion <- factor(criterion, levels = c("implicit", "intermediate", "explicit"))
  })


# model_summaries
# x <- subset(model_summaries, parameter == "beta" & contrast == "nonregular vs. regular")
# subset(model_summaries, parameter == "beta" & contrast == "deterministic vs. random")

library(papaja)



plot_points <- function(x, ylim = NULL) {

  if(is.null(ylim)) ylim <- c(min(x$Lower95), max(x$Upper95))

  int_x <- interaction(x$instructions, x$material, sep = "\n")



  x_coords <- as.numeric(int_x) + (as.numeric(x$criterion) - 1.5)  * .05
  x_coords


  plot.new()
  plot.window(xlim = c(.5, 4.5), ylim = ylim)


  arrows(y0 = x$Lower95, y1 = x$Upper95, x0 = x_coords, angle = 90, length = .02, code = 3)
  points(x = x_coords, y = x$Mean, bg = as.integer(x$criterion), pch = 21)
  axis(side = 1, at = 1:4, labels = levels(int_x))
  axis(side = 2)
  abline(h = 0, lty = "dashed", col = "grey60")
  title(
    main = unique(x$parameter)
   # , ylab = expression(paste(bquote(.(parse(text = unique(x$parameter))))))
  )
  legend(
    x = "top"
    , pch = 21
    , pt.bg = seq_len(nlevels(x$criterion))
    , legend = levels(x$criterion)
    , bty = "n"
    , ncol = 3L
    , inset = 0 # -.1
  )
}

# se2 <- function(x, na.rm = TRUE) sd(x, na.rm = na.rm) * 2
# par(mfrow = c(3, 4))
#
# for (i in c("alpha", "beta", "nu", "theta", "xi")) {
# out <- Map(
#   nm = names(models)
#   , x = models
#   , f = function(nm, x) {
#     if(is.null(x)) {
#       plot.new()
#       title(main = nm)
#     } else {
#       plot(
#         x
#         , pars = i
#         , ylim = list(alpha = c(.4, 1.1), beta = c(0, 1), nu = c(3, 6), theta = c(0, .4), xi = c(-.02, .02))[[i]]
#         # , args_points = list(bg = colors)
#         # , args_swarm = list(cex = .002, bg = colors, lwd = 0, pch = 21)
#         # , ylim = c(-0.040, 0.040)
#         # , args_y_axis = list(at = seq(-.04, .04, .01), labels = seq(-.04, .04, .01) * 1000)
#         , xlab = "Block pair"
#         # , ylab = expression("Response competition"~xi~ "[ms]")
#         , main = nm
#         , dispersion = se2
#         , args_error_bars = list(length = .02)
#         , plot = c("points", "error_bars", "lines")
#       )
#     }
#   }
# )
# }

