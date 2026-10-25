# Base-R contract tests on abstract fixtures only. Source input/fixtures first.

run_input_tests <- function() {
  count <- 0L
  check <- function(condition) {
    stopifnot(isTRUE(condition))
    count <<- count + 1L
  }
  rejected <- function(arguments) {
    caught <- tryCatch({do.call(assemble_input, arguments); NULL}, error = identity)
    check(inherits(caught, "asma_contract_error") &&
            identical(conditionMessage(caught), "ASMA contract failed; no row-level details emitted.") &&
            is.null(conditionCall(caught)))
  }

  small <- small_input_fixture()
  assembled <- do.call(assemble_input, small)
  check(identical(unname(assembled$x), matrix(c(2, -3, 6, 9), nrow = 2L)))
  check(identical(colnames(assembled$x), small$panel) &&
          identical(rownames(assembled$x), c("abstract-patient-A", "abstract-patient-B")) &&
          identical(unname(assembled$y), c(0L, 1L)))
  check(identical(byte_order(c("z", "a", "aa", "A", "\u00e9")), c(4L, 2L, 3L, 1L, 5L)))
  check(identical(byte_order(character()), integer()))

  fixture <- synthetic_fixture()
  full <- do.call(assemble_input, fixture)
  check(identical(dim(full$x), c(135L, 64L)) && identical(names(full$y), rownames(full$x)))
  check(sum(full$y == 0L) == 83L && sum(full$y == 1L) == 52L &&
          full$metadata$measurements == 168L && full$metadata$samples == 158L &&
          full$metadata$triplicate_groups == 5L && full$metadata$singletons == 153L &&
          full$metadata$selected_measurements == 145L && full$metadata$clinical_NA_rows == 1L &&
          full$metadata$ignored_measurement_columns == 2L &&
          full$metadata$retained_missing_location == 1L)
  check(all(vapply(full$metadata, function(value) is.numeric(value) && length(value) == 1L,
                   logical(1))))
  shuffled <- fixture
  shuffled$measurements <- fixture$measurements[rev(seq_len(nrow(fixture$measurements))),
                                                rev(seq_len(ncol(fixture$measurements))), drop = FALSE]
  shuffled$clinical <- fixture$clinical[rev(seq_len(nrow(fixture$clinical))), , drop = FALSE]
  shuffled$published_keys <- rev(fixture$published_keys)
  check(identical(do.call(assemble_input, shuffled), full))

  # A different exact score label for the same triplicate must still average
  # every measurement, rather than using only the label named in the score sheet.
  alternate <- small
  alternate$published_keys[2L] <- "abstract-m"
  check(identical(do.call(assemble_input, alternate), assembled))

  bad <- small; bad$measurements <- bad$measurements[, -2L, drop = FALSE]; rejected(bad)
  bad <- small; colnames(bad$measurements)[2L] <- colnames(bad$measurements)[1L]; rejected(bad)
  bad <- small; rownames(bad$measurements)[2L] <- rownames(bad$measurements)[1L]; rejected(bad)
  bad <- small; bad$panel[2L] <- "absent-feature"; rejected(bad)
  bad <- small; bad$panel[2L] <- bad$panel[1L]; rejected(bad)
  bad <- small; bad$panel[1L] <- paste0(" ", bad$panel[1L]); rejected(bad)
  bad <- small; bad$measurements[1L, 2L] <- NA_real_; rejected(bad)
  bad <- small; bad$measurements[1L, 2L] <- Inf; rejected(bad)
  bad <- small; bad$measurements[1L, 2L] <- NaN; rejected(bad)
  bad <- small; bad$measurements <- bad$measurements + 0i; rejected(bad)
  bad <- small; bad$clinical[["Tumor response"]][2L] <- "refractory"; rejected(bad)
  bad <- small; bad$clinical[["Patient ID"]][2L] <- "different-patient"; rejected(bad)
  bad <- small; bad$clinical[["Sample type"]][2L] <- "different-type"; rejected(bad)
  bad <- small; bad$clinical[["Neo-adjuvant"]][2L] <- "yes"; rejected(bad)
  bad <- small; bad$clinical[["Tumor Location Group"]][2L] <- "Mix"; rejected(bad)
  bad <- small; bad$clinical[[ASMA_LABEL_COLUMN]][2L] <- bad$clinical[[ASMA_LABEL_COLUMN]][1L]; rejected(bad)
  bad <- small; bad$clinical[["Patient ID"]][4L] <- "abstract-patient-A"; rejected(bad)
  bad <- small; bad$published_keys[1L] <- bad$published_keys[2L]; rejected(bad)
  bad <- small; bad$published_keys[1L] <- "nonmatching-published-key"; rejected(bad)
  bad <- small; bad$clinical[["Neo-adjuvant"]][4L] <- "yes"; rejected(bad)
  bad <- small; bad$clinical[["Tumor response"]][4L] <- "unknown-outcome"; rejected(bad)
  bad <- small; bad$clinical[["Tumor response"]][4L] <- "sensitive"; rejected(bad)
  bad <- small; bad$clinical[["Tumor Location Group"]][4L] <- NA_character_; rejected(bad)
  bad <- fixture; bad$clinical[["Patient ID"]][nrow(bad$clinical)] <- "not-explicit-NA"; rejected(bad)
  bad <- fixture; bad$published_keys[1L] <- "fixture-control-001"; rejected(bad)
  bad <- fixture; bad$clinical[["Tumor Location Group"]][bad$clinical[["Sample ID"]] ==
                                                        "fixture-sample-135"] <- "OV"; rejected(bad)
  bad <- fixture; bad$published_keys[1L] <- "fixture-measurement-136-1"; rejected(bad)
  bad <- small; names(bad$clinical)[2L] <- ASMA_LABEL_COLUMN; rejected(bad)
  bad <- small; bad$clinical[["Sample ID"]] <- factor(bad$clinical[["Sample ID"]]); rejected(bad)
  bad <- small; bad$expected$selected <- 2.5; rejected(bad)
  bad <- small; bad$expected$extra <- 1L; rejected(bad)

  # The finite-value rule applies to the selected input, not excluded samples
  # or unrelated matrix fields that must never affect the selected cohort.
  excluded <- fixture
  excluded$measurements[, "fixture-measurement-136-1"] <- Inf
  check(identical(do.call(assemble_input, excluded), full))
  count
}
