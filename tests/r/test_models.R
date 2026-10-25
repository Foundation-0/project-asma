# Abstract numeric fixtures exercise actual packages; no research records or genes.
run_model_tests <- function() {
  count <- 0L
  check <- function(condition) {
    if (!isTRUE(condition)) stop("Synthetic model test failed.", call. = FALSE)
    count <<- count + 1L
  }
  rejects <- function(expression) {
    message <- tryCatch({ force(expression); NULL }, error = conditionMessage)
    check(is.character(message) && length(message) == 1L &&
            !grepl("PRIVATE_TEST_SENTINEL", message, fixed = TRUE))
  }

  # Preserve the caller's stream, including when no seed existed before the test.
  old_kind <- RNGkind()
  had_seed <- exists(".Random.seed", envir = .GlobalEnv, inherits = FALSE)
  old_seed <- if (had_seed) get(".Random.seed", envir = .GlobalEnv) else NULL
  on.exit({
    do.call(RNGkind, as.list(old_kind))
    if (had_seed) assign(".Random.seed", old_seed, envir = .GlobalEnv)
    else if (exists(".Random.seed", envir = .GlobalEnv, inherits = FALSE))
      rm(".Random.seed", envir = .GlobalEnv)
  }, add = TRUE)
  RNGkind("Mersenne-Twister", "Inversion", "Rejection")
  set.seed(82631L)
  values <- matrix(rnorm(135L * 64L), nrow = 135L, ncol = 64L,
                   dimnames = list(sprintf("fixture-adapter-patient-%03d", 1:135),
                                   sprintf("fixture-feature-%03d", 1:64)))
  x_train <- values[1:108, , drop = FALSE]
  x_test <- values[109:135, , drop = FALSE]
  y_train <- setNames(c(rep(0L, 66L), rep(1L, 42L)), rownames(x_train))
  inner <- setNames(rep(1:3, length.out = 108L), rownames(x_train))
  original <- list(x_train, y_train, x_test, inner)

  expected <- c(glmnet = "4.1-8", randomForest = "4.7-1.2", xgboost = "1.7.8.1")
  check(isTRUE(check_model_versions(function(package) expected[[package]], "4.4.3")))
  rejects(check_model_versions(function(package) "0.0.0", "4.4.3"))
  rejects(check_model_versions(function(package) stop("PRIVATE_TEST_SENTINEL"), "4.4.3"))
  rejects(check_model_versions(function(package) warning("PRIVATE_TEST_SENTINEL"), "4.4.3"))
  rejects(check_model_versions(function(package) expected[[package]], "4.4.2"))
  rejects(model_operation(function() stop("PRIVATE_TEST_SENTINEL")))
  rejects(model_operation(function() warning("PRIVATE_TEST_SENTINEL")))
  check(identical(model_operation(function() { message("PRIVATE_TEST_SENTINEL"); 3L }), 3L))
  check(isTRUE(validate_model_input(x_train, y_train, x_test, inner, 1L, 1L)))
  other_labels <- setNames(c(rep(0L, 67L), rep(1L, 41L)), rownames(x_train))
  check(isTRUE(validate_model_input(x_train, other_labels, x_test, inner, 1L, 1L)))

  # Invalid calls must fail before any package fit; values cannot leak into errors.
  bad_test <- x_test[, 64:1, drop = FALSE]
  rejects(validate_model_input(x_train, y_train, bad_test, inner, 1L, 1L))
  bad_labels <- y_train[108:1]
  rejects(validate_model_input(x_train, bad_labels, x_test, inner, 1L, 1L))
  wrong_geometry <- setNames(c(rep(0L, 68L), rep(1L, 40L)), rownames(x_train))
  rejects(validate_model_input(x_train, wrong_geometry, x_test, inner, 1L, 1L))
  bad_test <- x_test
  rownames(bad_test)[1L] <- rownames(x_train)[1L]
  rejects(validate_model_input(x_train, y_train, bad_test, inner, 1L, 1L))
  bad_train <- x_train
  bad_train[1L, 1L] <- Inf
  rejects(validate_model_input(bad_train, y_train, x_test, inner, 1L, 1L))
  bad_inner <- inner
  bad_inner[1L] <- 2L
  rejects(validate_model_input(x_train, y_train, x_test, bad_inner, 1L, 1L))
  bad_names <- x_train
  rownames(bad_names)[1L] <- "PRIVATE_TEST_SENTINEL"
  rejects(validate_model_input(bad_names, y_train, x_test, inner, 1L, 1L))
  rejects(validate_model_input(x_train, y_train, x_test, inner, 0L, 1L))
  rejects(validate_model_input(x_train, y_train, x_test, inner, 1L, 6L))
  rejects(validate_model_input(x_train, y_train, x_test, inner, 1 + 0i, 1L))
  rejects(validate_model_input(x_train, y_train, x_test, inner, 1L, 1 + 0i))

  # Real pinned package calls: no expected scientific performance is asserted.
  set.seed(19261L)
  before_seed <- get(".Random.seed", envir = .GlobalEnv)
  output <- capture.output(first <- fit_models(x_train, y_train, x_test, inner, 1L, 1L))
  check(length(output) == 0L)
  check(identical(get(".Random.seed", envir = .GlobalEnv), before_seed))
  check(identical(original, list(x_train, y_train, x_test, inner)))
  check(identical(names(first), c("en", "xgb", "rf")))
  for (probability in first) {
    check(is.numeric(probability) && length(probability) == 27L &&
            identical(names(probability), rownames(x_test)) &&
            all(is.finite(probability)) && all(probability >= 0 & probability <= 1))
  }
  set.seed(47133L) # Ambient RNG changes must not alter model predictions.
  second <- fit_models(x_train, y_train, x_test, inner, 1L, 1L)
  check(identical(first, second))

  # Model APIs must preserve identity when held-out order changes.
  reversed <- fit_models(x_train, y_train, x_test[27:1, , drop = FALSE], inner, 1L, 1L)
  check(all(vapply(names(first), function(model) {
    identical(first[[model]], reversed[[model]][27:1])
  }, logical(1))))

  # Other held-out rows cannot influence the unchanged row through preprocessing.
  changed_test <- x_test
  changed_test[2:27, ] <- changed_test[2:27, ] * 10 + 50
  changed <- fit_models(x_train, y_train, changed_test, inner, 1L, 1L)
  check(all(vapply(names(first), function(model) {
    identical(first[[model]][1L], changed[[model]][1L])
  }, logical(1))))

  # Planted-signal direction check: a fixed shift on eight artificial features
  # for class 1. It shows each model scores class 1 (refractory) higher; it is
  # not simulated clinical evidence and asserts no expected performance.
  signal_y_test <- setNames(c(rep(0L, 17L), rep(1L, 10L)), rownames(x_test))
  signal_train <- x_train
  signal_test <- x_test
  signal_train[, 1:8] <- signal_train[, 1:8] + 1.5 * y_train
  signal_test[, 1:8] <- signal_test[, 1:8] + 1.5 * signal_y_test
  direction_holds <- function(probability, labels) {
    mean(probability[labels == 1L]) > mean(probability[labels == 0L]) &&
      checked_auc(labels, probability)$auc >= 0.8
  }
  signal <- fit_models(signal_train, y_train, signal_test, inner, 1L, 1L)
  for (model in c("en", "xgb", "rf")) {
    check(direction_holds(signal[[model]], signal_y_test))
    # The same check rejects a flipped probability, so it cannot pass by accident.
    check(!direction_holds(1 - signal[[model]], signal_y_test))
  }

  # With signal present the elastic net keeps predictors, so the order and
  # isolation checks are not satisfied trivially by a constant prediction.
  check(stats::sd(signal$en) > 0)
  signal_reversed <- fit_models(signal_train, y_train,
                                signal_test[27:1, , drop = FALSE], inner, 1L, 1L)
  check(all(vapply(names(signal), function(model) {
    identical(signal[[model]], signal_reversed[[model]][27:1])
  }, logical(1))))
  signal_changed_test <- signal_test
  signal_changed_test[2:27, ] <- signal_changed_test[2:27, ] * 10 + 50
  signal_changed <- fit_models(signal_train, y_train, signal_changed_test, inner, 1L, 1L)
  check(all(vapply(names(signal), function(model) {
    identical(signal[[model]][1L], signal_changed[[model]][1L])
  }, logical(1))))

  # The default is the declared "exact" method. The proposed sensitivity setting
  # ("hist") must give valid, correctly oriented probabilities, and only the
  # XGBoost component may change. It must change on this fixture, so the setting
  # cannot be silently ignored. Other values are rejected before any fit.
  check(identical(fit_models(signal_train, y_train, signal_test, inner, 1L, 1L,
                             xgb_tree_method = "exact"), signal))
  hist <- fit_models(signal_train, y_train, signal_test, inner, 1L, 1L,
                     xgb_tree_method = "hist")
  check(identical(hist$en, signal$en) && identical(hist$rf, signal$rf) &&
          !identical(hist$xgb, signal$xgb) && direction_holds(hist$xgb, signal_y_test))
  rejects(fit_models(signal_train, y_train, signal_test, inner, 1L, 1L,
                     xgb_tree_method = "approx"))

  count
}
