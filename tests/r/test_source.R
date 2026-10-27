# Abstract serialized-input tests; no research source material.
run_source_tests <- function() {
  count <- 0L
  check <- function(condition) {
    stopifnot(isTRUE(condition))
    count <<- count + 1L
  }
  fixture <- synthetic_fixture()
  columns <- fixture$clinical[[ASMA_LABEL_COLUMN]][1:168]
  measurements <- fixture$measurements[fixture$panel, columns, drop = FALSE]
  payload <- list(schema_version = 1L,
                  measurements = list(row_names = as.list(rownames(measurements)),
                    column_names = as.list(colnames(measurements)),
                    values = lapply(seq_len(nrow(measurements)), function(i) {
                      as.list(unname(measurements[i, ]))
                    })),
                  clinical = list(columns = as.list(names(fixture$clinical)),
                    rows = lapply(seq_len(nrow(fixture$clinical)), function(i) {
                      as.list(unname(as.character(fixture$clinical[i, ])))
                    })),
                  panel = as.list(fixture$panel),
                  published_keys = as.list(fixture$published_keys),
                  provenance = list(synthetic = TRUE))
  encode <- function(value) as.character(jsonlite::toJSON(value, auto_unbox = TRUE,
                                                         null = "null", digits = NA))
  rebuilt <- assemble_source_payload(encode(payload))
  expected <- do.call(assemble_input, fixture)
  same_input <- function(actual) {
    # jsonlite's R test serializer can round its text representation by a few
    # ULPs. Identity/order/labels remain exact; this tolerance concerns only
    # abstract fixture transport, never the scientific AUROC comparison.
    identical(dimnames(actual$x), dimnames(expected$x)) &&
      max(abs(actual$x - expected$x)) < 1e-13 && identical(actual$y, expected$y)
  }
  check(same_input(rebuilt))
  check(identical(dim(rebuilt$x), c(135L, 64L)))
  rejects <- function(text) {
    error <- tryCatch({assemble_source_payload(text); NULL}, error = identity)
    check(inherits(error, "asma_contract_error") &&
            identical(conditionMessage(error), "ASMA contract failed; no row-level details emitted."))
  }
  rejects("PRIVATE_TEST_SENTINEL")
  # A short string naming an existing file holding a valid abstract payload must
  # be rejected as non-JSON, never read. The temporary file is removed on exit.
  path <- tempfile(fileext = ".json")
  on.exit(unlink(path), add = TRUE)
  writeLines(encode(payload), path)
  rejects(path)
  rejects(paste0('{"private":"', strrep("x", 4L * 1024L * 1024L), '"}'))
  changed <- payload; changed$schema_version <- 2L; rejects(encode(changed))
  changed <- payload; changed$extra <- "PRIVATE_TEST_SENTINEL"; rejects(encode(changed))
  changed <- payload; changed$measurements$values[[1L]][[1L]] <- "PRIVATE_TEST_SENTINEL"; rejects(encode(changed))
  changed <- payload; changed$measurements$values[[1L]][[1L]] <- TRUE; rejects(encode(changed))
  changed <- payload; changed$measurements$values[[1L]][1L] <- list(NULL); rejects(encode(changed))
  changed <- payload; changed$measurements$values[[1L]] <- changed$measurements$values[[1L]][-1L]; rejects(encode(changed))
  changed <- payload; changed$measurements$column_names[[1L]] <- changed$measurements$column_names[[2L]]; rejects(encode(changed))
  changed <- payload; changed$measurements$row_names <- rev(changed$measurements$row_names)
  # Row identities control values; reversing both names and rows preserves input.
  changed$measurements$values <- rev(changed$measurements$values)
  check(same_input(assemble_source_payload(encode(changed))))
  changed <- payload; changed$clinical$columns <- rev(changed$clinical$columns); rejects(encode(changed))
  changed <- payload; changed$clinical$rows[[1L]][[1L]] <- 1L; rejects(encode(changed))
  changed <- payload; changed$clinical$rows[[1L]] <- changed$clinical$rows[[1L]][-1L]; rejects(encode(changed))
  changed <- payload; changed$published_keys[[1L]] <- "PRIVATE_TEST_SENTINEL"; rejects(encode(changed))
  changed <- payload; changed$panel[[1L]] <- changed$panel[[2L]]; rejects(encode(changed))
  changed <- payload
  excluded <- which(columns == "fixture-measurement-136-1")
  changed$measurements$values[[1L]][excluded] <- list(NULL)
  check(same_input(assemble_source_payload(encode(changed))))
  count
}
