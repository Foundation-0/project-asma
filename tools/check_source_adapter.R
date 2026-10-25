#!/usr/bin/env Rscript
# Test-only stdin bridge. No research fetch, file path or execution option.
status <- tryCatch({
  stopifnot(length(commandArgs(trailingOnly = TRUE)) == 0L)
  source("R/asma_input.R")
  source("R/asma_core.R")
  source("R/asma_models.R")
  source("R/asma_source.R")
  source("tests/r/synthetic_fixture.R")
  source("tests/r/test_source.R")
  assertions <- run_source_tests()
  stream <- file("stdin", "rb")
  raw <- readBin(stream, what = "raw", n = 4L * 1024L * 1024L + 1L)
  close(stream)
  input <- assemble_source_payload(rawToChar(raw))
  # This test-only entry point rejects identities outside its known fixture.
  asma_require(identical(rownames(input$x), sprintf("fixture-patient-%03d", 1:135)) &&
                 identical(colnames(input$x), sprintf("fixture-feature-%04d", 1:64)), "fixture_identity")
  expected <- outer(1:135, 1:64, function(sample, feature) {
    sin(feature * sample * sqrt(2)) + cos((feature + 1) * sample * sqrt(3)) +
      sin((feature + 3) * (sample + 2) * sqrt(5)) / 3
  })
  asma_require(max(abs(input$x - expected)) < 1e-12 &&
                 identical(unname(input$y), c(rep(0L, 83L), rep(1L, 52L))), "fixture_oracle")
  result <- run_reconstruction(input, fit_models, repetitions = 1L)
  safe <- c("patients", "features", "repetitions", "outer_folds", "model_predictions",
            "ensemble_predictions", "final_scores", "complete_prediction_coverage",
            "positive_negative_pairs")
  cat(jsonlite::toJSON(list(scope = "Synthetic source-adapter integration only",
    bridge_assertions = assertions, source_value_oracle_passed = TRUE,
    integration = result$summary[safe],
    metric_formulations_agree = identical(result$summary$auc, result$summary$rank_auc),
    clinical_reference_comparison_performed = FALSE), auto_unbox = TRUE, digits = NA), "\n")
  0L
}, error = function(error) {
  cat("ERROR: source-adapter fixture failed; no row-level details emitted.\n", file = stderr())
  1L
})
quit(save = "no", status = status)
