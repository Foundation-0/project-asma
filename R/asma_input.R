# Original reconstruction input contracts. No files or network are read here.
# Caller-supplied keys and values remain in memory; failures omit row details.

ASMA_LABEL_COLUMN <- paste0(
  "Data Label 2 <data set>_<TMTplex>_<sample source>_<patient ID>_sample ID>"
)
ASMA_CRITICAL_COLUMNS <- c("Patient ID", "Sample ID", "Neo-adjuvant",
                           "Tumor response", "Tumor Location Group", "Sample type")
ASMA_INPUT_EXPECTED <- list(
  measurements = 168L, samples = 158L, patients = 158L, selected = 135L,
  negative = 83L, positive = 52L, features = 64L, triplicate_groups = 5L,
  singletons = 153L, retained_missing_location = 1L
)

asma_require <- function(condition, code = "contract") {
  # code is a call-site label only; never include it or a failed value in output.
  if (!isTRUE(condition)) {
    stop(structure(
      list(message = "ASMA contract failed; no row-level details emitted.", call = NULL),
      class = c("asma_contract_error", "error", "condition")
    ))
  }
  invisible(TRUE)
}

asma_strings <- function(values, allow_literal_na = FALSE) {
  is.character(values) && !anyNA(values) &&
    all(Encoding(values) != "bytes") && all(validUTF8(enc2utf8(values))) &&
    all(nzchar(values)) && all(values == trimws(values)) &&
    (allow_literal_na || all(values != "NA"))
}

byte_order <- function(keys) {
  asma_require(asma_strings(keys, allow_literal_na = TRUE), "byte_order_keys")
  # Encoding each byte as two ASCII hex digits preserves unsigned byte order,
  # including prefix order; radix then avoids locale-dependent collation.
  encoded <- vapply(enc2utf8(keys), function(key) {
    paste(sprintf("%02x", as.integer(charToRaw(key))), collapse = "")
  }, character(1), USE.NAMES = FALSE)
  order(encoded, method = "radix")
}

assemble_input <- function(measurements, clinical, panel, published_keys,
                           expected = ASMA_INPUT_EXPECTED) {
  # Protect callers from accidental values in low-level parser/type errors.
  tryCatch(
    asma_assemble_checked(measurements, clinical, panel, published_keys, expected),
    error = function(error) {
      if (inherits(error, "asma_contract_error")) stop(error)
      asma_require(FALSE, "input_error")
    },
    warning = function(warning) asma_require(FALSE, "input_warning")
  )
}

asma_assemble_checked <- function(measurements, clinical, panel, published_keys,
                                  expected) {
  asma_require(is.list(expected) && !anyDuplicated(names(expected)) &&
                 setequal(names(expected), names(ASMA_INPUT_EXPECTED)), "expected_schema")
  asma_require(all(vapply(expected, function(value) {
    is.numeric(value) && length(value) == 1L && is.finite(value) &&
      value >= 0 && value == floor(value)
  }, logical(1))), "expected_counts")
  asma_require(expected$selected > 0 && expected$features > 0 &&
                 expected$negative > 0 && expected$positive > 0 &&
                 expected$selected == expected$negative + expected$positive &&
                 expected$samples == expected$triplicate_groups + expected$singletons &&
                 expected$measurements == 3L * expected$triplicate_groups + expected$singletons,
               "expected_geometry")

  asma_require(is.matrix(measurements) && typeof(measurements) %in% c("integer", "double") &&
                 nrow(measurements) > 0 && ncol(measurements) > 0, "matrix_type")
  asma_require(asma_strings(rownames(measurements)) &&
                 length(rownames(measurements)) == nrow(measurements) &&
                 !anyDuplicated(rownames(measurements)), "matrix_feature_keys")
  asma_require(asma_strings(colnames(measurements), allow_literal_na = TRUE) &&
                 length(colnames(measurements)) == ncol(measurements) &&
                 !anyDuplicated(colnames(measurements)), "matrix_measurement_keys")
  asma_require(asma_strings(panel) && !anyDuplicated(panel) &&
                 length(panel) == expected$features &&
                 all(panel %in% rownames(measurements)), "panel_keys")
  asma_require(asma_strings(published_keys) && !anyDuplicated(published_keys) &&
                 length(published_keys) == expected$selected, "published_keys")

  required <- c(ASMA_LABEL_COLUMN, ASMA_CRITICAL_COLUMNS)
  asma_require(is.data.frame(clinical) && nrow(clinical) > 0 &&
                 !anyDuplicated(names(clinical)) && all(required %in% names(clinical)),
               "clinical_schema")
  asma_require(all(vapply(clinical[required], function(values) {
    asma_strings(values, allow_literal_na = TRUE)
  }, logical(1))), "clinical_fields")
  labels <- clinical[[ASMA_LABEL_COLUMN]]
  asma_require(!anyDuplicated(labels), "clinical_label_duplicates")
  asma_require(all(clinical[["Tumor response"]] %in% c("sensitive", "refractory", "NA")) &&
                 all(clinical[["Neo-adjuvant"]] %in% c("yes", "no", "NA")) &&
                 all(clinical[["Tumor Location Group"]] %in%
                       c("OM", "OV", "PT", "NA", "GI", "Mix", "LN", "UT", "GIOM")),
               "clinical_categories")
  missing <- clinical[["Tumor response"]] == "NA"
  na_fields <- c("Patient ID", "Sample ID", "Neo-adjuvant", "Sample type")
  asma_require(all(vapply(clinical[missing, na_fields, drop = FALSE], function(values) {
    all(values == "NA")
  }, logical(1))), "clinical_na_rows")
  biological <- clinical[!missing, required, drop = FALSE]
  asma_require(nrow(biological) == expected$measurements, "biological_count")
  asma_require(all(vapply(biological[c(ASMA_LABEL_COLUMN, "Patient ID", "Sample ID", "Sample type")],
                          asma_strings, logical(1))) &&
                 all(biological[["Neo-adjuvant"]] %in% c("yes", "no")), "biological_identity")
  biological_labels <- biological[[ASMA_LABEL_COLUMN]]
  asma_require(all(biological_labels %in% colnames(measurements)), "measurement_completeness")

  samples <- unique(biological[["Sample ID"]])
  samples <- samples[byte_order(samples)]
  groups <- lapply(samples, function(sample) which(biological[["Sample ID"]] == sample))
  sizes <- lengths(groups)
  asma_require(length(samples) == expected$samples &&
                 length(unique(biological[["Patient ID"]])) == expected$patients &&
                 all(sizes %in% c(1L, 3L)) &&
                 sum(sizes == 3L) == expected$triplicate_groups &&
                 sum(sizes == 1L) == expected$singletons, "replicate_geometry")
  asma_require(all(vapply(groups, function(indices) {
    all(vapply(biological[indices, ASMA_CRITICAL_COLUMNS, drop = FALSE],
               function(values) length(unique(values)) == 1L, logical(1)))
  }, logical(1))), "replicate_consistency")
  representatives <- biological[vapply(groups, `[`, integer(1), 1L), , drop = FALSE]

  published_indices <- match(published_keys, labels)
  asma_require(!anyNA(published_indices) && !any(missing[published_indices]), "published_exact_join")
  published <- clinical[published_indices, required, drop = FALSE]
  asma_require(!anyDuplicated(published[["Sample ID"]]) &&
                 !anyDuplicated(published[["Patient ID"]]), "published_unique_identity")
  eligible <- representatives[["Neo-adjuvant"]] == "no" &
    representatives[["Tumor Location Group"]] != "Mix"
  asma_require(sum(eligible) == expected$selected &&
                 setequal(published[["Sample ID"]], representatives[["Sample ID"]][eligible]) &&
                 setequal(published[["Patient ID"]], representatives[["Patient ID"]][eligible]),
               "membership_matches_exclusions")

  selected <- representatives[eligible, , drop = FALSE]
  asma_require(!anyDuplicated(selected[["Patient ID"]]), "one_sample_per_patient")
  selected <- selected[byte_order(selected[["Patient ID"]]), , drop = FALSE]
  patients <- selected[["Patient ID"]]
  response <- selected[["Tumor response"]]
  asma_require(sum(response == "sensitive") == expected$negative &&
                 sum(response == "refractory") == expected$positive &&
                 sum(selected[["Tumor Location Group"]] == "NA") == expected$retained_missing_location,
               "selected_counts")

  x <- matrix(NA_real_, nrow = expected$selected, ncol = expected$features,
              dimnames = list(patients, panel))
  selected_measurements <- 0L
  feature_indices <- match(panel, rownames(measurements))
  for (index in seq_len(nrow(selected))) {
    group <- groups[[match(selected[["Sample ID"]][index], samples)]]
    group_labels <- biological_labels[group]
    group_labels <- group_labels[byte_order(group_labels)]
    values <- measurements[feature_indices, match(group_labels, colnames(measurements)), drop = FALSE]
    asma_require(all(is.finite(values)), "finite_selected_measurements")
    x[index, ] <- vapply(seq_along(panel), function(feature) mean(values[feature, ]), numeric(1))
    selected_measurements <- selected_measurements + length(group)
  }
  asma_require(all(is.finite(x)) && identical(colnames(x), panel) &&
                 identical(rownames(x), patients), "assembled_identity")
  y <- setNames(as.integer(response == "refractory"), patients)
  metadata <- list(
    measurements = nrow(biological), samples = length(samples),
    patients = length(unique(biological[["Patient ID"]])), selected = nrow(x),
    negative = sum(y == 0L), positive = sum(y == 1L), features = ncol(x),
    triplicate_groups = sum(sizes == 3L), singletons = sum(sizes == 1L),
    retained_missing_location = sum(selected[["Tumor Location Group"]] == "NA"),
    clinical_NA_rows = sum(missing),
    ignored_measurement_columns = sum(!colnames(measurements) %in% biological_labels),
    selected_measurements = selected_measurements
  )
  list(x = x, y = y, metadata = metadata)
}
