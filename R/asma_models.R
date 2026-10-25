# Original adapters for the declared reconstruction; no source-study code reused.
# This module performs no file/network I/O. Fit objects remain local to a call.

check_model_versions <- function(version_reader = utils::packageVersion,
                                 r_version = getRversion()) {
  expected <- c(glmnet = "4.1-8", randomForest = "4.7-1.2", xgboost = "1.7.8.1")
  asma_require(identical(as.character(r_version), "4.4.3"), "model_version")
  wanted <- vapply(expected, function(version) as.character(package_version(version)),
                   character(1))
  observed <- model_operation(function() vapply(names(expected), function(package) {
    as.character(package_version(as.character(version_reader(package))))
  }, character(1)))
  asma_require(identical(observed, wanted), "model_version")
  invisible(TRUE)
}

model_operation <- function(operation) {
  tryCatch(withCallingHandlers(operation(),
    warning = function(warning) stop("Model operation failed.", call. = FALSE),
    message = function(message) invokeRestart("muffleMessage")),
    error = function(error) stop("Model operation failed.", call. = FALSE))
}

validate_model_input <- function(x_train, y_train, x_test, inner_foldid,
                                 repetition, fold) {
  valid_names <- function(keys, size) {
    is.character(keys) && length(keys) == size && !anyNA(keys) &&
      all(nzchar(keys)) && !anyDuplicated(keys) &&
      all(keys == trimws(keys))
  }
  asma_require(is.matrix(x_train) && typeof(x_train) %in% c("double", "integer") &&
                 identical(dim(x_train), c(108L, 64L)) &&
                 is.matrix(x_test) && typeof(x_test) %in% c("double", "integer") &&
                 identical(dim(x_test), c(27L, 64L)), "model_contract")
  asma_require(all(is.finite(x_train)) && all(is.finite(x_test)), "model_contract")
  asma_require(valid_names(rownames(x_train), 108L) &&
                 valid_names(rownames(x_test), 27L) &&
                 valid_names(colnames(x_train), 64L) &&
                 identical(colnames(x_train), colnames(x_test)) &&
                 !any(rownames(x_train) %in% rownames(x_test)), "model_contract")
  asma_require(typeof(y_train) %in% c("double", "integer") && is.null(dim(y_train)) &&
                 length(y_train) == 108L &&
                 !anyNA(y_train) && all(y_train %in% c(0L, 1L)) &&
                 identical(names(y_train), rownames(x_train)), "model_contract")
  class_sizes <- tabulate(as.integer(y_train) + 1L, nbins = 2L)
  asma_require(identical(class_sizes, c(66L, 42L)) ||
                 identical(class_sizes, c(67L, 41L)), "model_contract")
  asma_require(typeof(inner_foldid) %in% c("double", "integer") &&
                 is.null(dim(inner_foldid)) && length(inner_foldid) == 108L &&
                 !anyNA(inner_foldid) && all(inner_foldid %in% 1:3) &&
                 identical(names(inner_foldid), rownames(x_train)) &&
                 identical(tabulate(as.integer(inner_foldid), nbins = 3L),
                           rep(36L, 3L)), "model_contract")
  for (inner in 1:3) {
    counts <- tabulate(as.integer(y_train[inner_foldid == inner]) + 1L, nbins = 2L)
    asma_require(counts[1L] %in% 22:23 && counts[2L] %in% 13:14,
                 "model_contract")
  }
  asma_require(typeof(repetition) %in% c("double", "integer") &&
                 is.null(dim(repetition)) && length(repetition) == 1L &&
                 is.finite(repetition) && repetition %in% 1:100 &&
                 typeof(fold) %in% c("double", "integer") && is.null(dim(fold)) &&
                 length(fold) == 1L && is.finite(fold) &&
                 fold %in% 1:5, "model_contract")
  invisible(TRUE)
}

fit_models <- function(x_train, y_train, x_test, inner_foldid, repetition, fold,
                       xgb_tree_method = "exact") {
  validate_model_input(x_train, y_train, x_test, inner_foldid, repetition, fold)
  # "exact" is the declared primary setting. "hist" exists only for the proposed
  # amendment 1 (A2) sensitivity configuration, and runs only if that is adopted.
  asma_require(identical(xgb_tree_method, "exact") || identical(xgb_tree_method, "hist"),
               "model_contract")
  check_model_versions()

  # Restore both the RNG algorithm and stream, including an initially absent seed.
  previous_kind <- RNGkind()
  had_seed <- exists(".Random.seed", envir = .GlobalEnv, inherits = FALSE)
  previous_seed <- if (had_seed) get(".Random.seed", envir = .GlobalEnv) else NULL
  on.exit({
    do.call(RNGkind, as.list(previous_kind))
    if (had_seed) {
      assign(".Random.seed", previous_seed, envir = .GlobalEnv)
    } else if (exists(".Random.seed", envir = .GlobalEnv, inherits = FALSE)) {
      rm(".Random.seed", envir = .GlobalEnv)
    }
  }, add = TRUE)
  RNGkind("Mersenne-Twister", "Inversion", "Rejection")

  model_operation(function() {
    en_fit <- glmnet::cv.glmnet(
      x = x_train, y = unname(y_train), family = "binomial", alpha = 0.2,
      foldid = unname(as.integer(inner_foldid)), nfolds = 3L,
      type.measure = "deviance", standardize = TRUE, intercept = TRUE,
      nlambda = 100L, lambda.min.ratio = 1e-4, grouped = TRUE,
      alignment = "lambda", type.logistic = "Newton", thresh = 1e-7,
      maxit = 100000L, penalty.factor = rep(1, 64L), parallel = FALSE,
      keep = FALSE
    )
    asma_require(identical(en_fit$glmnet.fit$jerr, 0L) &&
                   length(en_fit$lambda.min) == 1L &&
                   is.finite(en_fit$lambda.min) && en_fit$lambda.min > 0 &&
                   all(is.finite(en_fit$cvm)), "model_fit")
    en_matrix <- stats::predict(en_fit, newx = x_test, s = "lambda.min",
                                type = "response")
    asma_require(is.matrix(en_matrix) && identical(dim(en_matrix), c(27L, 1L)),
                 "model_fit")
    if (!is.null(rownames(en_matrix))) {
      asma_require(identical(rownames(en_matrix), rownames(x_test)), "model_fit")
    }

    # xgboost 1.7.8.1's R interface ignores native seed parameters; use R's stream.
    set.seed(20000L + 100L * as.integer(repetition) + as.integer(fold))
    training <- xgboost::xgb.DMatrix(x_train, label = unname(y_train), nthread = 1L)
    testing <- xgboost::xgb.DMatrix(x_test, nthread = 1L)
    xgb_fit <- xgboost::xgb.train(
      params = list(objective = "binary:logistic", booster = "gbtree",
                    tree_method = xgb_tree_method, nthread = 1L, max_depth = 2L,
                    eta = 0.1, base_score = 0.5, min_child_weight = 1,
                    gamma = 0, subsample = 1, colsample_bytree = 1,
                    colsample_bylevel = 1, colsample_bynode = 1,
                    lambda = 1, alpha = 0, max_delta_step = 0, verbosity = 0L),
      data = training, nrounds = 100L, watchlist = list(), verbose = 0L,
      callbacks = list()
    )
    asma_require(inherits(xgb_fit, "xgb.Booster"), "model_fit")
    xgb_probability <- stats::predict(xgb_fit, testing)

    set.seed(1000000L)
    rf_fit <- randomForest::randomForest(
      x = x_train, y = factor(unname(y_train), levels = c(0L, 1L)),
      ntree = 100L, mtry = 8L, nodesize = 1L, replace = TRUE,
      sampsize = 108L, maxnodes = NULL, classwt = NULL,
      cutoff = c(0.5, 0.5), importance = TRUE, proximity = TRUE,
      norm.votes = TRUE, keep.forest = TRUE, do.trace = FALSE
    )
    asma_require(identical(rf_fit$classes, c("0", "1")) &&
                   rf_fit$ntree == 100L && !is.null(rf_fit$forest), "model_fit")
    rf_matrix <- stats::predict(rf_fit, newdata = x_test, type = "prob")
    asma_require(is.matrix(rf_matrix) && identical(dim(rf_matrix), c(27L, 2L)) &&
                   identical(rownames(rf_matrix), rownames(x_test)) &&
                   identical(colnames(rf_matrix), c("0", "1")), "model_fit")

    result <- list(en = as.numeric(en_matrix[, 1L]),
                   xgb = as.numeric(xgb_probability),
                   rf = as.numeric(rf_matrix[, "1"]))
    for (model in names(result)) {
      probability <- result[[model]]
      asma_require(length(probability) == 27L && all(is.finite(probability)) &&
                     all(probability >= 0 & probability <= 1), "model_fit")
      names(probability) <- rownames(x_test)
      result[[model]] <- probability
    }
    result
  })
}
