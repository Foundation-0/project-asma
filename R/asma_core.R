# Original reconstruction control flow. This module performs no input/output.
# Patient keys, folds and predictions are transient in-memory objects only.

asma_valid_keys <- function(keys) {
  is.character(keys) && length(keys) > 0L && !anyNA(keys) &&
    all(nzchar(keys)) && !anyDuplicated(keys) &&
    all(trimws(keys) == keys)
}

asma_preserve_rng <- function(action) {
  old_kind <- RNGkind()
  had_seed <- exists(".Random.seed", envir = .GlobalEnv, inherits = FALSE)
  if (had_seed) old_seed <- get(".Random.seed", envir = .GlobalEnv, inherits = FALSE)
  on.exit({
    suppressWarnings(do.call(RNGkind, as.list(old_kind)))
    if (had_seed) {
      assign(".Random.seed", old_seed, envir = .GlobalEnv)
    } else if (exists(".Random.seed", envir = .GlobalEnv, inherits = FALSE)) {
      rm(".Random.seed", envir = .GlobalEnv)
    }
  }, add = TRUE)
  action()
}

asma_silent_call <- function(action, code) {
  # Both streams use in-memory text connections, never persistent files. R's
  # message sink has no stack, so explicitly restore the caller's connection.
  message_output <- character()
  message_connection <- textConnection("message_output", "w", local = TRUE)
  previous_message <- getConnection(sink.number(type = "message"))
  message_closed <- FALSE
  restore_message <- function() {
    if (!message_closed) {
      sink(previous_message, type = "message")
      close(message_connection) # Flush even a final line without a newline.
      message_closed <<- TRUE
    }
  }
  on.exit(restore_message(), add = TRUE)
  sink(message_connection, type = "message")
  tryCatch({
    output <- capture.output(value <- withCallingHandlers(
      action(),
      warning = function(condition) asma_require(FALSE, code),
      message = function(condition) asma_require(FALSE, code)
    ))
    restore_message()
    asma_require(length(output) == 0L && length(message_output) == 0L, code)
    value
  }, error = function(condition) {
    restore_message()
    asma_require(FALSE, code)
  })
}

stratified_folds <- function(patient_ids, y, k, seed) {
  asma_require(asma_valid_keys(patient_ids), "fold_identity")
  asma_require(is.numeric(y) && !is.complex(y) && is.null(dim(y)) &&
                 length(y) == length(patient_ids) && all(is.finite(y)) &&
                 all(y %in% c(0L, 1L)) &&
                 identical(names(y), patient_ids), "fold_labels")
  asma_require(is.numeric(k) && !is.complex(k) && length(k) == 1L && is.finite(k) &&
                 k >= 2L && k <= length(patient_ids) && k == as.integer(k), "fold_count")
  k <- as.integer(k)
  asma_require(is.numeric(seed) && !is.complex(seed) && length(seed) == 1L && is.finite(seed) &&
                 seed >= 0 && seed <= .Machine$integer.max &&
                 seed == as.integer(seed), "fold_seed")
  asma_require(all(tabulate(as.integer(y) + 1L, nbins = 2L) >= k), "fold_classes")
  order <- byte_order(patient_ids)
  keys <- patient_ids[order]
  labels <- y[order]
  folds <- asma_preserve_rng(function() {
    RNGkind("Mersenne-Twister", "Inversion", "Rejection")
    set.seed(as.integer(seed))
    assigned <- integer(length(keys))
    offset <- 0L
    for (label in 0:1) {
      members <- which(labels == label)
      permuted <- members[sample.int(length(members))]
      assigned[permuted] <- (offset + seq_along(permuted) - 1L) %% k + 1L
      offset <- (offset + length(permuted)) %% k
    }
    stats::setNames(assigned, keys)
  })
  # Return in caller order, with identities explicit. The assignment itself is
  # independent of caller order and locale because canonical ordering came first.
  folds <- folds[patient_ids]
  asma_require(all(folds %in% seq_len(k)), "fold_coverage")
  for (fold in seq_len(k)) {
    asma_require(all(tabulate(as.integer(y[folds == fold]) + 1L,
                             nbins = 2L) > 0L), "fold_classes")
  }
  folds
}

checked_auc <- function(y, scores) {
  asma_require(is.numeric(y) && !is.complex(y) && is.null(dim(y)) &&
                 is.numeric(scores) && !is.complex(scores) && is.null(dim(scores)) &&
                 length(y) == length(scores) && length(y) > 1L &&
                 all(is.finite(y)) && all(is.finite(scores)) &&
                 all(y %in% c(0L, 1L)) && all(scores >= 0 & scores <= 1), "auc_input")
  if (!is.null(names(y)) || !is.null(names(scores))) {
    asma_require(asma_valid_keys(names(y)) &&
                   identical(names(y), names(scores)), "auc_identity")
  }
  positive <- scores[y == 1L]
  negative <- scores[y == 0L]
  asma_require(length(positive) > 0L && length(negative) > 0L, "auc_classes")
  concordant <- discordant <- tied <- 0L
  for (value in positive) {
    concordant <- concordant + sum(value > negative)
    discordant <- discordant + sum(value < negative)
    tied <- tied + sum(value == negative)
  }
  pairs <- length(positive) * length(negative)
  pair_auc <- (concordant + tied / 2) / pairs
  ranks <- rank(scores, ties.method = "average")
  rank_auc <- (sum(ranks[y == 1L]) - length(positive) *
                 (length(positive) + 1) / 2) / pairs
  asma_require(concordant + discordant + tied == pairs &&
                 is.finite(pair_auc) && identical(pair_auc, rank_auc), "auc_agreement")
  list(auc = pair_auc, rank_auc = rank_auc,
       positive_negative_pairs = pairs, concordant_pairs = concordant,
       discordant_pairs = discordant, tied_pairs = tied,
       pair_credit_twice = 2 * concordant + tied)
}

run_reconstruction <- function(assembled, fit_predict, repetitions = 100L,
                               observer = NULL) {
  asma_require(is.list(assembled) && all(c("x", "y") %in% names(assembled)), "run_input")
  x <- assembled$x
  y <- assembled$y
  asma_require(is.matrix(x) && is.numeric(x) && !is.complex(x) &&
                 identical(dim(x), c(135L, 64L)) && all(is.finite(x)), "run_shape")
  keys <- rownames(x)
  features <- colnames(x)
  asma_require(asma_valid_keys(keys) && asma_valid_keys(features) &&
                 identical(keys, keys[byte_order(keys)]), "run_identity")
  asma_require(is.integer(y) && is.null(dim(y)) && length(y) == 135L &&
                 identical(names(y), keys) && all(y %in% c(0L, 1L)) &&
                 identical(tabulate(y + 1L, nbins = 2L), c(83L, 52L)), "run_labels")
  asma_require(is.function(fit_predict) && (is.null(observer) || is.function(observer)), "run_adapter")
  asma_require(is.numeric(repetitions) && !is.complex(repetitions) && length(repetitions) == 1L &&
                 is.finite(repetitions) && repetitions >= 1L && repetitions <= 100L &&
                 repetitions == as.integer(repetitions), "run_repetitions")
  repetitions <- as.integer(repetitions)

  asma_preserve_rng(function() {
    # Every assignment is fixed before any model or observer can consume RNG.
    plans <- lapply(seq_len(repetitions), function(repetition) {
      outer <- stratified_folds(keys, y, 5L, repetition)
      asma_require(identical(as.integer(table(factor(outer, levels = 1:5))),
                             rep(27L, 5L)), "outer_geometry")
      lapply(1:5, function(fold) {
        training <- which(outer != fold)
        test <- which(outer == fold)
        inner <- stratified_folds(keys[training], y[training], 3L,
                                  10000L + 100L * repetition + fold)
        asma_require(identical(as.integer(table(factor(inner, levels = 1:3))),
                               rep(36L, 3L)), "inner_geometry")
        list(training = training, test = test, inner = inner)
      })
    })

    ensemble <- matrix(NA_real_, nrow = length(keys), ncol = repetitions,
                       dimnames = list(keys, paste0("repeat-", seq_len(repetitions))))
    prediction_count <- 0L
    fold_count <- 0L
    for (repetition in seq_len(repetitions)) {
      model_scores <- matrix(NA_real_, nrow = length(keys), ncol = 3L,
                             dimnames = list(keys, c("en", "xgb", "rf")))
      seen <- integer(length(keys))
      for (fold in 1:5) {
        plan <- plans[[repetition]][[fold]]
        training <- plan$training
        test <- plan$test
        train_ids <- keys[training]
        test_ids <- keys[test]
        x_train <- x[training, , drop = FALSE]
        x_test <- x[test, , drop = FALSE]
        y_train <- y[training]
        inner_foldid <- plan$inner
        asma_require(length(training) == 108L && length(test) == 27L &&
                       !anyDuplicated(c(train_ids, test_ids)) &&
                       setequal(c(train_ids, test_ids), keys) &&
                       identical(rownames(x_train), names(y_train)) &&
                       identical(rownames(x_train), names(inner_foldid)) &&
                       identical(colnames(x_train), features) &&
                       identical(colnames(x_test), features) && all(seen[test] == 0L),
                     "run_fold_identity")
        if (!is.null(observer)) {
          asma_silent_call(function() observer(list(
            repetition = repetition, fold = fold, train_ids = train_ids,
            test_ids = test_ids, inner_foldid = inner_foldid
          )), "observer_failure")
        }
        predictions <- asma_silent_call(function() fit_predict(
          x_train = x_train, y_train = y_train, x_test = x_test,
          inner_foldid = inner_foldid, repetition = repetition, fold = fold
        ), "model_failure")
        asma_require(is.list(predictions) &&
                       identical(names(predictions), c("en", "xgb", "rf")), "prediction_models")
        for (model in c("en", "xgb", "rf")) {
          probability <- predictions[[model]]
          asma_require(is.numeric(probability) && !is.complex(probability) && is.null(dim(probability)) &&
                         length(probability) == length(test_ids) &&
                         identical(names(probability), test_ids) &&
                         all(is.finite(probability)) &&
                         all(probability >= 0 & probability <= 1), "prediction_values")
          asma_require(all(is.na(model_scores[test, model])), "prediction_duplicate")
          model_scores[test, model] <- probability
          prediction_count <- prediction_count + length(probability)
        }
        seen[test] <- seen[test] + 1L
        fold_count <- fold_count + 1L
      }
      asma_require(all(seen == 1L) && all(is.finite(model_scores)), "prediction_coverage")
      # The specified ordering is explicit; there is no na.rm or partial mean.
      ensemble[, repetition] <- (model_scores[, "en"] + model_scores[, "xgb"] +
                                    model_scores[, "rf"]) / 3
    }
    asma_require(all(is.finite(ensemble)) &&
                   prediction_count == 135L * repetitions * 3L &&
                   fold_count == repetitions * 5L, "run_coverage")
    scores <- stats::setNames(vapply(seq_len(nrow(ensemble)), function(i) {
      mean(ensemble[i, seq_len(repetitions)])
    }, numeric(1)), keys)
    metric <- checked_auc(y, scores)
    asma_require(metric$positive_negative_pairs == 4316L, "run_metric_denominator")
    # Amendment 1: a descriptive secondary output. Each repetition's AUROC spans
    # all 135 held-out ensemble scores; it is not a fold AUROC or a pooled value.
    repetition_auc <- vapply(seq_len(repetitions), function(repetition) {
      checked_auc(y, ensemble[, repetition])$auc
    }, numeric(1))
    spread <- stats::quantile(repetition_auc, probs = c(0, .25, .5, .75, 1),
                              type = 7L, names = FALSE)
    list(scores = scores, repetition_scores = ensemble,
         summary = c(list(patients = 135L, features = 64L,
                          repetitions = repetitions, outer_folds = fold_count,
                          model_predictions = prediction_count,
                          ensemble_predictions = length(ensemble),
                          final_scores = length(scores),
                          complete_prediction_coverage = TRUE), metric,
                     list(repetition_auc = list(
                       count = repetitions, minimum = spread[1L],
                       lower_quartile = spread[2L], median = spread[3L],
                       upper_quartile = spread[4L], maximum = spread[5L],
                       mean = mean(repetition_auc)))))
  })
}
