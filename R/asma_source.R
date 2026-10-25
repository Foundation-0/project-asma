# Original in-memory bridge from the hash-checked Python source adapter.
# No file/network loading, console output or patient-level persistence.

source_strings <- function(values) {
  is.list(values) && length(values) > 0L &&
    all(vapply(values, function(value) {
      is.character(value) && length(value) == 1L && !is.na(value)
    }, logical(1)))
}

source_fields <- function(value, fields) {
  is.list(value) && !is.null(names(value)) && !anyDuplicated(names(value)) &&
    setequal(names(value), fields)
}

decode_source_payload <- function(text) {
  tryCatch({
    asma_require(is.character(text) && length(text) == 1L && !is.na(text) &&
                   nchar(text, type = "bytes") > 0L &&
                   nchar(text, type = "bytes") <= 4L * 1024L * 1024L,
                 "source_payload_size")
    # parse_json only parses text; fromJSON would read a short string naming a
    # file or URL from disk or the network.
    payload <- jsonlite::parse_json(text, simplifyVector = FALSE)
    asma_require(source_fields(payload, c("schema_version", "measurements",
                   "clinical", "panel", "published_keys", "provenance")) &&
                   identical(payload$schema_version, 1L), "source_payload_schema")
    matrix_data <- payload$measurements
    asma_require(source_fields(matrix_data, c("row_names", "column_names", "values")) &&
                   source_strings(matrix_data$row_names) &&
                   source_strings(matrix_data$column_names) &&
                   length(matrix_data$row_names) == 64L &&
                   length(matrix_data$column_names) == 168L &&
                   is.list(matrix_data$values) && length(matrix_data$values) == 64L,
                 "source_matrix_shape")
    values <- lapply(matrix_data$values, function(row) {
      asma_require(is.list(row) && length(row) == 168L, "source_matrix_row")
      vapply(row, function(value) {
        if (is.null(value)) return(NA_real_)
        asma_require(typeof(value) %in% c("integer", "double") &&
                       length(value) == 1L && is.finite(value), "source_numeric_value")
        as.numeric(value)
      }, numeric(1))
    })
    measurements <- matrix(unlist(values, use.names = FALSE), nrow = 64L,
                           byrow = TRUE,
                           dimnames = list(unlist(matrix_data$row_names, use.names = FALSE),
                                           unlist(matrix_data$column_names, use.names = FALSE)))
    clinical_data <- payload$clinical
    fields <- c(ASMA_LABEL_COLUMN, ASMA_CRITICAL_COLUMNS)
    asma_require(source_fields(clinical_data, c("columns", "rows")) &&
                   source_strings(clinical_data$columns) &&
                   identical(unlist(clinical_data$columns, use.names = FALSE), fields) &&
                   is.list(clinical_data$rows) && length(clinical_data$rows) >= 168L &&
                   length(clinical_data$rows) <= 1000L, "source_clinical_schema")
    rows <- lapply(clinical_data$rows, function(row) {
      asma_require(source_strings(row) && length(row) == length(fields), "source_clinical_row")
      unlist(row, use.names = FALSE)
    })
    clinical <- as.data.frame(do.call(rbind, rows), stringsAsFactors = FALSE,
                              check.names = FALSE)
    names(clinical) <- fields
    asma_require(source_strings(payload$panel) && length(payload$panel) == 64L &&
                   source_strings(payload$published_keys) &&
                   length(payload$published_keys) == 135L &&
                   is.list(payload$provenance), "source_panel_membership")
    list(measurements = measurements, clinical = clinical,
         panel = unlist(payload$panel, use.names = FALSE),
         published_keys = unlist(payload$published_keys, use.names = FALSE))
  }, error = function(error) asma_require(FALSE, "source_decode"),
     warning = function(warning) asma_require(FALSE, "source_decode"))
}

assemble_source_payload <- function(text) {
  do.call(assemble_input, decode_source_payload(text))
}
