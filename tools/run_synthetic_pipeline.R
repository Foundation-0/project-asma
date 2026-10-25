#!/usr/bin/env Rscript
# Synthetic-only entry point: no file/URL argument or research-data loader.
# Run from the repository root with Rscript --vanilla.

main <- function(arguments) {
  if (length(arguments) != 1L || !arguments %in% c("--tests", "--full")) {
    stop("Expected --tests or --full", call. = FALSE)
  }
  started <- format(Sys.time(), "%Y-%m-%dT%H:%M:%OS6Z", tz = "UTC")
  timer <- proc.time()[["elapsed"]]
  source("R/asma_input.R", local = .GlobalEnv)
  source("R/asma_core.R", local = .GlobalEnv)
  source("R/asma_models.R", local = .GlobalEnv)
  source("tests/r/synthetic_fixture.R", local = .GlobalEnv)
  source("tests/r/test_input.R", local = .GlobalEnv)
  source("tests/r/test_core.R", local = .GlobalEnv)
  source("tests/r/test_models.R", local = .GlobalEnv)
  check_model_versions()
  asma_require(requireNamespace("jsonlite", quietly = TRUE), "runtime_json")

  checks <- list(input = run_input_tests(), core = run_core_tests(),
                 models = run_model_tests())
  input <- do.call(assemble_input, synthetic_fixture())
  integration <- list(executed = FALSE)
  if (identical(arguments, "--full")) {
    result <- run_reconstruction(input, fit_models, repetitions = 100L)
    # Preserve coverage evidence, not artificial AUROC or per-fixture scores.
    safe <- c("patients", "features", "repetitions", "outer_folds",
              "model_predictions", "ensemble_predictions", "final_scores",
              "complete_prediction_coverage", "positive_negative_pairs")
    integration <- c(list(executed = TRUE, model_backend = "pinned_R_packages"),
                     result$summary[safe],
                     list(metric_formulations_agree = identical(result$summary$auc,
                                                                 result$summary$rank_auc),
                          clinical_reference_comparison_performed = FALSE))
    rm(result)
  }

  package_data <- as.data.frame(installed.packages()[, c("Package", "Version", "License")],
                                stringsAsFactors = FALSE, row.names = NULL)
  package_data <- package_data[order(package_data$Package, method = "radix"), ]
  files <- c("R/asma_input.R", "R/asma_core.R", "R/asma_models.R",
             "tests/r/synthetic_fixture.R", "tests/r/test_input.R",
             "tests/r/test_core.R", "tests/r/test_models.R",
             "tools/run_synthetic_pipeline.R", "tools/run_synthetic_pipeline.py",
             "tools/build_synthetic_runtime.py", "tests/test_synthetic_runtime.py",
             "runtime/synthetic-packages.json",
             "runtime/Dockerfile.synthetic", "runtime/install.R",
             "protocols/pilot-001-reconstruction-decisions.md")
  sha256 <- function(path) {
    text <- system2("sha256sum", shQuote(path), stdout = TRUE, stderr = FALSE)
    asma_require(length(text) == 1L && grepl("^[0-9a-f]{64} ", text), "software_hash")
    substr(text, 1L, 64L)
  }
  info <- sessionInfo()
  release <- readLines("/etc/os-release", warn = FALSE)
  record <- list(
    schema_version = 1L,
    scope = "Synthetic fixtures only; no source-study data or clinical performance result",
    started_at_utc = started,
    finished_at_utc = format(Sys.time(), "%Y-%m-%dT%H:%M:%OS6Z", tz = "UTC"),
    elapsed_seconds = proc.time()[["elapsed"]] - timer,
    assertions = c(checks, list(total = sum(unlist(checks)))),
    synthetic_input = input$metadata,
    integration = integration,
    environment = list(
      r_version = as.character(getRversion()), platform = R.version$platform,
      os_release = release[grepl("^(ID|VERSION_ID|PRETTY_NAME)=", release)],
      runtime_image_id = Sys.getenv("ASMA_RUNTIME_IMAGE_ID", unset = "unrecorded"),
      BLAS = info$BLAS, LAPACK = info$LAPACK,
      compiler = system2("g++", "--version", stdout = TRUE)[1L],
      fortran = system2("gfortran", "--version", stdout = TRUE)[1L],
      thread_settings = as.list(Sys.getenv(c("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS",
                                             "MKL_NUM_THREADS", "RCPP_PARALLEL_NUM_THREADS"))),
      installed_packages = package_data),
    implementation_sha256 = as.list(stats::setNames(vapply(files, sha256, character(1)), files)),
    limitations = c(
      "All identities, feature names and numeric values are artificial fixtures, not simulated clinical evidence.",
      "Synthetic fitting verifies implementation behavior, not source-file ingestion, historical equivalence or clinical validity.",
      "No research data loader or research-execution CLI is enabled by this entry point.",
      "The Canadian execution-context and research data-use conditions remain unverified by these tests.",
      "The image pins the tested package/OS/toolchain inputs; bit-identical rebuilds or cross-platform scores are not asserted.",
      "This process emits only software provenance and aggregate test/coverage evidence; no fixture-level scores or fitted models are retained."
    )
  )
  cat(jsonlite::toJSON(record, auto_unbox = TRUE, pretty = TRUE, digits = NA), "\n")
  invisible(NULL)
}

status <- tryCatch({
  main(commandArgs(trailingOnly = TRUE))
  0L
}, error = function(error) {
  cat("ERROR: synthetic pipeline checks failed; no row-level details emitted.\n", file = stderr())
  1L
})
quit(save = "no", status = status)
