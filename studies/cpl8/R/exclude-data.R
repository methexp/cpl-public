
library(tinylabels)

study_folder <- file.path(rprojroot::find_rstudio_root_file(), "studies", "cpl8")

data <- readRDS(file.path(study_folder, "data", "data.rds"))

agg <- aggregate(
  cbind(
    error_rate = error
    , response_time = response_time
    , deadline_exceeded = deadline_exceeded
  ) ~ block_pair+ sid
  , data = data
  , FUN = mean
  , na.rm = TRUE
  , na.action = na.pass
)


hist(agg$deadline_exceeded)
plot.new()
plot.window(xlim = c(1, 7), ylim = c(0, 1))

out <- split(agg, agg$sid) |>
  lapply(function(x) {
    lines(x = x$block_pair, y = x$deadline_exceeded, col = x$sid[[1]])
  })
axis(side = 1)
axis(side = 2)
too_slow <- unique(subset(agg, (deadline_exceeded > .3) & block_pair > 1)$sid)
too_many_errors <- unique(subset(agg, error_rate > .5 & block_pair > 1)$sid)
incomplete_data <- c(6, 84)
lablog_excludes <- c(8, 21, 26, 34)

visual_inspection <- c(
  # Mixed deterministic, sequence concealed
  18, 61 # tried to use explicit knowledge in random blocks
  , 112 # catastrophe towards end of experiment
  # Mixed deterministic, sequence revealed
  , 84 # only two blocks
  # Probabilistic, sequence concealed
  , 8 # almost exclusively too-slow responses
  , 26, 30 # slow
  , 81 # lots of noise
  # Probabilistic, sequence revealed
  , 31, 33 # noisy
  , 68 # systematic errors
)

# setdiff(visual_inspection, c(too_slow, too_many_errors, incomplete_data))
# setdiff(too_many_errors, visual_inspection)

data <- subset(
  data
  , sid > 5 & # response times were rounded to whole seconds :(
    !(sid %in% too_slow) &
    !(sid %in% too_many_errors) &
    !(sid %in% incomplete_data) &
    !(sid %in% lablog_excludes)
    # !(sid %in% visual_inspection)
)

saveRDS(data, file = file.path(study_folder, "data", "data-excluded.rds"))

aggregate(sid ~ material + instructions, data = data, FUN = function(x) length(unique(x)))
