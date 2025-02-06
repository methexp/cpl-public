
study_folder <- file.path(rprojroot::find_rstudio_root_file(), "studies", "cpl8")

data_files <- list.files(path = file.path(study_folder, "data-raw"), pattern = "^[[:digit:]]*\\.csv", full.names = TRUE)

data_files <- data_files[file.size(data_files)>0]

data <- do.call("rbind", lapply(data_files, read.csv))

data$error <- as.logical(data$error)

data$tix <- (data$tid - 1L) %% 144L + 1L
data$block_number <- data$bid

data$deadline_exceeded <- data$response_time > data$response_deadline


x <- subset(data, sid == 1)

data <- split(data, data$sid) |>
  lapply(function(x) {
    cross_table <- table(x$tid)
    x$multiple_responses <- x$tid %in% as.integer(names(cross_table[cross_table > 1L]))
    x$first_response <- !duplicated(x$tid)
    x
  }) |>
  do.call(what = "rbind")

data <- subset(data, first_response)

# table(data$error, useNA = "ifany")

data$previous_error[seq_len(nrow(data) - 1L) + 1L] <- data$error[seq_len(nrow(data) - 1L)]
data$previous_error[data$tix == 1L] <- NA

data$previous_deadline_exceeded <- NA
data$previous_deadline_exceeded[seq_len(nrow(data) - 1L) + 1L] <- data$deadline_exceeded[seq_len(nrow(data) - 1L)]
data$previous_deadline_exceeded[data$tix == 1L] <- NA

data$previous_response_location[seq_len(nrow(data) - 1L) + 1L] <- data$response_location[seq_len(nrow(data) - 1L)]
data$previous_response_location[data$tix == 1L] <- NA

data$previous_stimulus_location[seq_len(nrow(data) - 1L) + 1L] <- data$stimulus_location[seq_len(nrow(data) - 1L)]
data$previous_stimulus_location[data$tix == 1L] <- NA

data$response_repetition <- data$response_location == data$previous_response_location

data <- split(data, data$sid) |>
  lapply(FUN = function(x) {
    regular_stimulus_location <-
      table(x$previous_stimulus_location, x$stimulus_location) |>
      apply(MARGIN = 1L, which.max)

    # x$color_regularity <- regular_color[x$previous_stimulus_color] == x$stimulus_color
    x$stimulus_location_regularity <- regular_stimulus_location[x$previous_stimulus_location] == x$stimulus_location
    x$response_regularity <- regular_stimulus_location[x$previous_response_location] == x$response_location
    x
  }) |>
  do.call(what = "rbind")

data <- split(data, data[, c("sid", "previous_stimulus_location")]) |>
  lapply(FUN = function(x) {
    x$previous_presentation_regular <- NA
    idx <- seq_len(nrow(x) - 1L)
    x$previous_presentation_regular[idx + 1] <- x$stimulus_location_regularity[idx]
    x$transition_repetition <- NA
    x$transition <- paste0(x$previous_stimulus_location, x$stimulus_location)
    x$transition_repetition[idx + 1L] <- x$transition[idx + 1L] == x$transition[idx]
    x
  }) |>
  do.call(what = "rbind")

data$block_pair <- floor((data$block_number -1L) / 2) + 1
table(data$block_number, data$block_pair)

data$context <- "random"
data$context[
  (data$material_order == "regular first" & data$block_number %% 2 == 1) |
    (data$material_order == "random first" & data$block_number %% 2 == 0)
] <- "deterministic"
data$context[data$material == "probabilistic"] <- "probabilistic"

data$three_levels <- ifelse(
  data$context == "deterministic"
  , 3L
  , as.integer(data$stimulus_location_regularity) + 1L
)
table(data$material, data$three_levels)
data$three_levels <- factor(data$three_levels, levels = 1:3, c("nonregular", "regular", "deterministic"))

library(tinylabels)

variable_labels(data) <- c(
  sid = "Subject identifier"
  , tid = "Trial identifier"
  , tix = "Trial number"
  , response_location = "Response location"
  , stimulus_location = "Stimulus location"
  , response_time = "Response time [s]"
  , block_number = "Block number"
  , block_pair = "Block Pair"
  , error = "Erroneous response"
  , previous_error = "Post-error trial"
  , stimulus_location_regularity = "Stimulus-location regularity"
  , response_regularity = "Response regularity"
  , deadline_exceeded = "Response deadline exceeded"
  , previous_deadline_exceeded = "Post-deadline-exceeded trial"
  , previous_presentation_regular = "Previous presentation regular"
  , transition_repetition = "Transition repetition"
)



dir.create(file.path(study_folder, "data"), showWarnings = FALSE)
saveRDS(data, file = file.path(study_folder, "data", "data.rds"))
