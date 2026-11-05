#!/usr/bin/env Rscript
# Pilot 001 reconstruction runner for container execution.
# Emits allow-listed aggregate JSON only (Amendment 1 adopted paths).

main <- function(arguments) {
  source("R/asma_input.R", local = .GlobalEnv)
  source("R/asma_core.R", local = .GlobalEnv)
  source("R/asma_models.R", local = .GlobalEnv)
  dry <- "--dry-run" %in% arguments
  real <- "--real" %in% arguments
  asma_require(xor(dry, real), "run_mode")
  reps <- 5L
  for (arg in arguments) {
    if (grepl("^--repetitions=", arg, fixed = FALSE)) {
      reps <- as.integer(sub("^--repetitions=", "", arg))
      asma_require(reps >= 1L && reps <= 100L, "run_repetitions")
    }
  }

  asma_require(requireNamespace("jsonlite", quietly = TRUE), "runtime_json")
  check_model_versions()

  if (dry) {
    source("tests/r/synthetic_fixture.R", local = .GlobalEnv)
    input <- do.call(assemble_input, synthetic_fixture())
    input_mode <- "synthetic_fixture"
    real_executed <- FALSE
  } else {
    payload_path <- Sys.getenv("PILOT001_SOURCE_PAYLOAD_PATH", unset = "")
    asma_require(nzchar(payload_path), "real_payload_path")
    payload_path <- normalizePath(payload_path, winslash = "/", mustWork = TRUE)
    asma_require(grepl("^/tmp/", payload_path), "real_payload_tmpfs")
    payload_text <- readChar(payload_path, n = 4L * 1024L * 1024L + 1L, useBytes = TRUE)
    asma_require(nchar(payload_text, type = "bytes") <= 4L * 1024L * 1024L, "real_payload_size")
    source("R/asma_source.R", local = .GlobalEnv)
    input <- assemble_source_payload(payload_text)
    input_mode <- "pinned_real_sources"
    real_executed <- TRUE
  }

  fit_primary <- function(...) fit_models(..., xgb_tree_method = "exact")
  fit_hist <- function(...) fit_models(..., xgb_tree_method = "hist")

  run_block <- function(label, outer_seed_start, fit_fn) {
    result <- run_reconstruction(input, fit_fn, repetitions = reps,
                                 outer_seed_start = outer_seed_start)
    safe_summary <- result$summary[c(
      "patients", "features", "repetitions", "outer_folds", "model_predictions",
      "ensemble_predictions", "final_scores", "complete_prediction_coverage",
      "positive_negative_pairs", "auc", "rank_auc", "repetition_auc"
    )]
    list(
      label = label,
      outer_seed_start = outer_seed_start,
      xgb_tree_method = if (identical(fit_fn, fit_hist)) "hist" else "exact",
      summary = safe_summary,
      metric_formulations_agree = identical(result$summary$auc, result$summary$rank_auc)
    )
  }

  configurations <- list(
    run_block("primary", 1L, fit_primary),
    run_block("sensitivity_xgb_hist", 1L, fit_hist),
    run_block("sensitivity_seed_block_101_200", 101L, fit_primary)
  )

  git_sha <- Sys.getenv("PILOT001_GIT_SHA", unset = "unknown")
  image_id <- Sys.getenv("ASMA_RUNTIME_IMAGE_ID", unset = "unrecorded")
  platform <- Sys.getenv("PILOT001_IMAGE_PLATFORM", unset = "unknown")
  started <- format(Sys.time(), "%Y-%m-%dT%H:%M:%OS6Z", tz = "UTC")
  timer <- proc.time()[["elapsed"]]

  record <- list(
    schema_version = 1L,
    review_status = "exploratory_not_externally_reviewed",
    scope = "Pilot 001 first-run aggregate outputs; not externally reviewed",
    input_mode = input_mode,
    real_study_data_executed = real_executed,
    amendment_1 = list(A1 = TRUE, A2 = list(option_a = TRUE, option_b = TRUE), A3 = "strict"),
    started_at_utc = started,
    configurations = configurations,
    run_metadata = list(
      git_sha = git_sha,
      runtime_image_id = image_id,
      container_platform = platform,
      host_uname_m = Sys.getenv("PILOT001_UNAME_M", unset = "unknown"),
      r_version = as.character(getRversion())
    ),
    limitations = c(
      "Exploratory outputs only; not compared with published 0.83.",
      if (real_executed) "Real mode executed on pinned study bytes inside container tmpfs." else "Dry-run mode uses synthetic fixtures only.",
      "No row-level scores or patient keys are retained in this aggregate artifact."
    )
  )
  record$finished_at_utc <- format(Sys.time(), "%Y-%m-%dT%H:%M:%OS6Z", tz = "UTC")
  record$elapsed_seconds <- proc.time()[["elapsed"]] - timer
  cat(jsonlite::toJSON(record, auto_unbox = TRUE, pretty = TRUE, digits = NA), "\n")
  invisible(NULL)
}

status <- tryCatch({
  main(commandArgs(trailingOnly = TRUE))
  0L
}, error = function(error) {
  code <- conditionMessage(error)
  if (grepl("^P001-FAIL-", code)) {
    cat(code, "\n", sep = "")
  } else if (inherits(error, "asma_failure_code")) {
    cat(conditionMessage(error), "\n", sep = "")
  } else {
    cat("P001-FAIL-INTERNAL\n", sep = "")
  }
  1L
})
quit(save = "no", status = status)
