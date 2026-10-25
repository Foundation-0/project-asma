# Abstract, deterministic test data. These are not simulated clinical observations
# and do not contain any source-study identities, protein symbols or measurements.

synthetic_fixture <- function() {
  panel <- sprintf("fixture-feature-%03d", seq_len(64L))
  sample_numbers <- rep(seq_len(158L), times = c(rep(3L, 5L), rep(1L, 153L)))
  replicate_numbers <- sequence(c(rep(3L, 5L), rep(1L, 153L)))
  measurement_labels <- sprintf("fixture-measurement-%03d-%d", sample_numbers, replicate_numbers)
  samples <- sprintf("fixture-sample-%03d", sample_numbers)
  patients <- sprintf("fixture-patient-%03d", sample_numbers)
  responses <- ifelse(sample_numbers <= 83L, "sensitive", "refractory")
  neoadjuvant <- ifelse(sample_numbers %in% 136:148, "yes", "no")
  locations <- ifelse(sample_numbers %in% 149:158, "Mix", "OV")
  locations[sample_numbers == 135L] <- "NA"
  # Match the order of the exact required fields explicitly rather than relying
  # on the CRITICAL constant to infer the values' meaning.
  clinical <- data.frame(stringsAsFactors = FALSE, check.names = FALSE,
                         label = measurement_labels,
                         patient = patients, sample = samples, neo = neoadjuvant,
                         response = responses, location = locations,
                         type = rep("fixture-type", length(samples)))
  names(clinical) <- c(ASMA_LABEL_COLUMN, "Patient ID", "Sample ID", "Neo-adjuvant",
                       "Tumor response", "Tumor Location Group", "Sample type")
  control <- as.list(setNames(rep("NA", ncol(clinical)), names(clinical)))
  control[[ASMA_LABEL_COLUMN]] <- "fixture-control-001"
  clinical <- rbind(clinical, as.data.frame(control, stringsAsFactors = FALSE,
                                           check.names = FALSE))

  values <- outer(seq_len(64L), sample_numbers, function(feature, sample) {
    sin(feature * sample * sqrt(2)) + cos((feature + 1) * sample * sqrt(3)) +
      sin((feature + 3) * (sample + 2) * sqrt(5)) / 3
  })
  offsets <- ifelse(sample_numbers <= 5L, (replicate_numbers - 2L) / 4, 0)
  values <- sweep(values, 2L, offsets, "+")
  rownames(values) <- panel
  colnames(values) <- measurement_labels
  # Extra nonpatient columns and one unused feature test explicit selection.
  values <- cbind(values, "fixture-control-001" = NA_real_,
                  "fixture-unmapped-column" = Inf)
  values <- rbind(values, "fixture-unused-feature" = rep(NA_real_, ncol(values)))
  published_keys <- sprintf("fixture-measurement-%03d-1", seq_len(135L))
  list(measurements = values, clinical = clinical, panel = panel,
       published_keys = published_keys)
}

small_input_fixture <- function() {
  measurement_labels <- c("abstract-z", "abstract-a", "abstract-m", "abstract-single")
  clinical <- data.frame(
    label = measurement_labels, patient = c(rep("abstract-patient-A", 3L), "abstract-patient-B"),
    sample = c(rep("abstract-sample-A", 3L), "abstract-sample-B"),
    neo = rep("no", 4L), response = c(rep("sensitive", 3L), "refractory"),
    location = rep("OV", 4L), type = rep("abstract-type", 4L),
    stringsAsFactors = FALSE, check.names = FALSE
  )
  names(clinical) <- c(ASMA_LABEL_COLUMN, "Patient ID", "Sample ID", "Neo-adjuvant",
                       "Tumor response", "Tumor Location Group", "Sample type")
  values <- matrix(c(2, 6, 10, 9, 12, 0, -6, -3), nrow = 2L, byrow = TRUE,
                   dimnames = list(c("abstract-feature-B", "abstract-feature-A"), measurement_labels))
  list(
    measurements = values, clinical = clinical,
    panel = c("abstract-feature-A", "abstract-feature-B"),
    published_keys = c("abstract-single", "abstract-z"),
    expected = list(measurements = 4L, samples = 2L, patients = 2L, selected = 2L,
                    negative = 1L, positive = 1L, features = 2L, triplicate_groups = 1L,
                    singletons = 1L, retained_missing_location = 0L)
  )
}
