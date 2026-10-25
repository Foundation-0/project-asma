# Original local installer. The Python builder verifies all source archives.
stopifnot(as.character(getRversion()) == "4.4.3")
packages <- c("Rcpp_1.0.14", "RcppEigen_0.3.4.0.2", "iterators_1.0.14",
              "foreach_1.5.2", "shape_1.4.6.1", "data.table_1.17.0",
              "jsonlite_1.9.1", "glmnet_4.1-8", "randomForest_4.7-1.2",
              "xgboost_1.7.8.1")
for (item in packages) {
  archive <- file.path("/tmp/asma-packages", paste0(item, ".tar.gz"))
  status <- system2(file.path(R.home("bin"), "R"), c("CMD", "INSTALL", shQuote(archive)))
  if (!identical(status, 0L)) stop("Pinned package installation failed", call. = FALSE)
  name_version <- strsplit(item, "_", fixed = TRUE)[[1L]]
  stopifnot(packageVersion(name_version[[1L]]) == package_version(name_version[[2L]]))
}
