#!/usr/bin/env Rscript
# Checks the panel-name test tokens (tests/panel_name_tokens.json, also read by
# tests/test_panel_names.py) against R's own make.names. Abstract tokens only;
# prints counts, no tokens. Exits non-zero on any mismatch.
# Run from the repository root: Rscript --vanilla tools/check_panel_name_tokens.R
status <- tryCatch({
  stopifnot(length(commandArgs(trailingOnly = TRUE)) == 0L)
  table <- jsonlite::fromJSON("tests/panel_name_tokens.json", simplifyVector = FALSE)
  tokens <- function(key) {
    values <- table[[key]]
    stopifnot(is.list(values), length(values) > 0L,
              all(vapply(values, function(value) is.character(value) &&
                           length(value) == 1L && !is.na(value), logical(1))))
    unlist(values)
  }
  unchanged <- tokens("unchanged")
  altered <- tokens("altered")
  checks <- c(make.names(unchanged) == unchanged,
              make.names(altered) != altered,
              # Distinct tokens that make.names keeps get no suffix from unique = TRUE.
              identical(make.names(unchanged, unique = TRUE), unchanged))
  cat(sprintf("Checked %d expectations against make.names; %d mismatches.\n",
              length(checks), sum(!checks)))
  if (all(checks)) 0L else 1L
}, error = function(error) {
  cat("ERROR: panel-name token check failed.\n", file = stderr())
  1L
})
quit(save = "no", status = status)
