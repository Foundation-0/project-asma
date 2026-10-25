# Abstract-token software tests only. No research measurements or patient keys.

run_core_tests <- function() {
  count <- 0L
  check <- function(condition) {
    stopifnot(isTRUE(condition))
    count <<- count + 1L
  }
  fails <- function(action, forbidden = NULL) {
    error <- tryCatch({ action(); NULL }, error = identity)
    check(inherits(error, "error"))
    if (!is.null(forbidden)) check(!grepl(forbidden, conditionMessage(error), fixed = TRUE))
    invisible(error)
  }
  keys <- sprintf("fixture-patient-%03d", 1:135)
  y <- stats::setNames(c(rep(0L, 83L), rep(1L, 52L)), keys)
  x <- matrix(seq_len(135L * 64L) / 1000, 135L, 64L,
              dimnames = list(keys, sprintf("fixture-feature-%03d", 1:64)))
  assembled <- list(x = x, y = y)

  # Exact hand-check: 3 concordances, 1 tie, 2 discordances => 7/12.
  labels <- c(0L, 0L, 0L, 1L, 1L)
  metric <- checked_auc(labels, c(.1, .5, .9, .5, .8))
  check(identical(metric$auc, 7 / 12))
  check(metric$concordant_pairs == 3L && metric$tied_pairs == 1L &&
          metric$discordant_pairs == 2L && metric$positive_negative_pairs == 6L)
  check(checked_auc(c(0L, 1L), c(.5, .5))$auc == .5)
  check(checked_auc(c(0L, 1L), c(1, 0))$auc == 0)
  check(checked_auc(c(0L, 1L), c(0, 1))$auc == 1)
  fails(function() checked_auc(c(0L, 0L), c(.1, .2)))
  fails(function() checked_auc(c(0L, 1L), c(.1, NA_real_)))
  fails(function() checked_auc(c(0L, 1L), c(.1, 1.1)))
  fails(function() checked_auc(c(0L, 1L), c(.1, .2 + 1i)))
  fails(function() checked_auc(stats::setNames(c(0L, 1L), c("a", "b")),
                               stats::setNames(c(.1, .2), c("b", "a"))))

  # The assignment must not depend on input order, ambient RNG or previous fits.
  set.seed(9876)
  old_kind <- RNGkind()
  old_seed <- .Random.seed
  outer <- stratified_folds(keys, y, 5L, 1L)
  check(identical(.Random.seed, old_seed) && identical(RNGkind(), old_kind))
  reversed <- rev(seq_along(keys))
  shuffled <- stratified_folds(keys[reversed], y[reversed], 5L, 1L)
  check(identical(outer, shuffled[keys]))
  check(!identical(outer, stratified_folds(keys, y, 5L, 2L)))
  check(identical(as.integer(table(outer)), rep(27L, 5L)))
  check(identical(as.integer(table(outer[y == 0L])), c(17L, 17L, 17L, 16L, 16L)))
  check(identical(as.integer(table(outer[y == 1L])), c(10L, 10L, 10L, 11L, 11L)))
  for (fold in 1:5) {
    training <- outer != fold
    inner <- stratified_folds(keys[training], y[training], 3L, 10100L + fold)
    check(identical(as.integer(table(inner)), rep(36L, 3L)))
    check(all(table(inner, y[training]) > 0L))
    check(!any(names(inner) %in% keys[!training]))
  }
  fails(function() stratified_folds(c(keys[-1L], keys[2L]), y, 5L, 1L))
  fails(function() stratified_folds(keys, unname(y), 5L, 1L))
  fails(function() stratified_folds(keys, stats::setNames(rep(0L, 135L), keys), 5L, 1L))
  fails(function() stratified_folds(keys, y, 5.5, 1L))

  stub <- function(x_train, y_train, x_test, inner_foldid, repetition, fold) {
    ids <- rownames(x_test)
    list(en = stats::setNames(rep(.1 + repetition / 1000, nrow(x_test)), ids),
         xgb = stats::setNames(rep(.3, nrow(x_test)), ids),
         rf = stats::setNames(rep(.5, nrow(x_test)), ids))
  }
  observations <- 0L
  observed_pairs <- list()
  observer <- function(event) {
    stopifnot(length(event$train_ids) == 108L, length(event$test_ids) == 27L,
              !any(event$test_ids %in% event$train_ids),
              identical(names(event$inner_foldid), event$train_ids))
    observations <<- observations + 1L
    observed_pairs[[observations]] <<- c(event$train_ids, event$test_ids)
    invisible(NULL)
  }
  set.seed(125)
  saved_seed <- .Random.seed
  result <- run_reconstruction(assembled, stub, 100L, observer)
  check(identical(.Random.seed, saved_seed))
  check(observations == 500L && result$summary$outer_folds == 500L)
  check(result$summary$model_predictions == 40500L &&
          result$summary$ensemble_predictions == 13500L &&
          result$summary$final_scores == 135L)
  # Closed-form mean uses the arithmetic-series mean 50.5, not the pipeline loop.
  expected <- (.1 + 50.5 / 1000 + .3 + .5) / 3
  check(all(abs(result$scores - expected) < 1e-14))
  check(result$summary$auc == .5 && result$summary$tied_pairs == 4316L)
  check(identical(names(result$scores), keys) &&
          identical(dim(result$repetition_scores), c(135L, 100L)))

  noisy_rng_stub <- function(...) {
    runif(500L)
    stub(...)
  }
  replay_events <- list()
  replay <- run_reconstruction(assembled, noisy_rng_stub, 100L, function(event) {
    replay_events[[length(replay_events) + 1L]] <<- c(event$train_ids, event$test_ids)
    invisible(NULL)
  })
  check(identical(result$scores, replay$scores) && identical(observed_pairs, replay_events))

  changed <- assembled
  changed$x <- changed$x[rev(seq_len(135L)), , drop = FALSE]
  fails(function() run_reconstruction(changed, stub, 1L))
  changed <- assembled
  changed$y <- rev(changed$y)
  fails(function() run_reconstruction(changed, stub, 1L))
  changed <- assembled
  changed$x[1L, 1L] <- Inf
  fails(function() run_reconstruction(changed, stub, 1L))

  bad_predictions <- list(
    function(p) { p$en <- p$en[-1L]; p },
    function(p) { p$en <- rev(p$en); p },
    function(p) { names(p$en)[2L] <- names(p$en)[1L]; p },
    function(p) { p$en[1L] <- NA_real_; p },
    function(p) { p$en[1L] <- 1.01; p },
    function(p) { p$en <- unname(p$en); p },
    function(p) { p$rf <- NULL; p },
    function(p) { p[c("xgb", "en", "rf")] }
  )
  for (mutate in bad_predictions) {
    adapter <- local({ change <- mutate; function(...) change(stub(...)) })
    fails(function() run_reconstruction(assembled, adapter, 1L))
  }
  fails(function() run_reconstruction(assembled, function(...) {
    stop("private-marker", call. = FALSE)
  }, 1L), "private-marker")
  fails(function() run_reconstruction(assembled, function(...) {
    warning("private-marker")
    stub(...)
  }, 1L), "private-marker")
  fails(function() run_reconstruction(assembled, function(...) {
    message("private-marker")
    stub(...)
  }, 1L), "private-marker")
  printed <- capture.output(fails(function() run_reconstruction(assembled, function(...) {
    cat("private-marker\n")
    stub(...)
  }, 1L), "private-marker"))
  check(length(printed) == 0L)
  fails(function() run_reconstruction(assembled, stub, 1L, function(event) {
    stop("private-marker", call. = FALSE)
  }), "private-marker")

  # Direct stderr writes bypass R warning/message handlers. A caller-owned sink
  # must stay open and unchanged after both normal rejection and adapter errors.
  output_depth <- sink.number(type = "output")
  previous_message <- getConnection(sink.number(type = "message"))
  outer_error <- character()
  error_connection <- textConnection("outer_error", "w", local = TRUE)
  sink(error_connection, type = "message")
  caller_sink <- sink.number(type = "message")
  captured <- capture.output({
    fails(function() run_reconstruction(assembled, function(...) {
      cat("private-marker", file = stderr())
      stub(...)
    }, 1L), "private-marker")
    check(sink.number(type = "message") == caller_sink)
    fails(function() run_reconstruction(assembled, function(...) {
      cat("private-marker", file = stderr())
      stop("private-marker", call. = FALSE)
    }, 1L), "private-marker")
    check(sink.number(type = "message") == caller_sink)
    fails(function() run_reconstruction(assembled, stub, 1L, function(event) {
      cat("private-marker", file = stderr())
      invisible(NULL)
    }), "private-marker")
    check(sink.number(type = "message") == caller_sink)
  })
  sink(previous_message, type = "message")
  close(error_connection)
  check(length(captured) == 0L && length(outer_error) == 0L &&
          sink.number(type = "output") == output_depth)

  set.seed(8128)
  saved_seed <- .Random.seed
  fails(function() run_reconstruction(assembled, function(...) {
    runif(10L)
    stop("private-marker", call. = FALSE)
  }, 1L), "private-marker")
  check(identical(.Random.seed, saved_seed))
  count
}
