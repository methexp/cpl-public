
stimulus_files <- list.files(
  file.path("studies", "cpl8", "experimental-software", "stimuli")
  , pattern = "^acquisition"
  , full.names = TRUE
)

x <- do.call("rbind", lapply(stimulus_files, read.csv))
x$tix <- (x$tid - 1) %% 144 + 1



x$previous_stimulus_location[2:nrow(x)] <- x$stimulus_location[seq_len(nrow(x) - 1L)]
x$previous_stimulus_location[x$tix == 1L] <- NA


table(x$response_deadline)



x$block_number <- floor((x$tid-1)/144) + 1

xtabs( ~ block_number+ block_scheme + material, x)

x <- split(x, x$sid) |>
  lapply(FUN = function(x) {
    regular_stimulus_location <-
      table(x$previous_stimulus_location, x$stimulus_location) |>
      apply(MARGIN = 1L, which.max)
    # regular_response <-
    #   table(x$previous_response_location, x$response_location) |>
    #   apply(MARGIN = 1L, which.max)

    x$stimulus_location_regularity <- regular_stimulus_location[x$previous_stimulus_location] == x$stimulus_location
    x
  }) |>
  do.call(what = "rbind")


xtabs( ~ stimulus_location_regularity + block_scheme + material, x)
xtabs( ~ stimulus_location_regularity + material, x)
