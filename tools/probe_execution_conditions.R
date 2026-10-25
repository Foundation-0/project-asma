#!/usr/bin/env Rscript
# Observe only runtime controls; no source data, network calls or patient records.

probe_execution_conditions <- function() {
  read_safe <- function(path) {
    tryCatch(readLines(path, warn = FALSE), error = function(error) NULL)
  }
  scalar <- function(path) {
    value <- read_safe(path)
    if (length(value) == 1L) value else NULL
  }
  numeric_limit <- function(path) {
    value <- scalar(path)
    if (is.null(value)) return(NULL)
    if (identical(value, "max")) return("max")
    if (!grepl("^[0-9]+$", value)) return(NULL)
    as.numeric(value)
  }
  status <- read_safe("/proc/self/status")
  status_field <- function(name) {
    value <- status[startsWith(status, paste0(name, ":"))]
    if (length(value) != 1L) return(NULL)
    trimws(sub("^[^:]+:", "", value))
  }
  caps <- lapply(c("CapInh", "CapPrm", "CapEff", "CapBnd", "CapAmb"), status_field)
  zero_caps <- if (any(vapply(caps, is.null, logical(1)))) NULL else
    all(vapply(caps, function(value) grepl("^0+$", value), logical(1)))
  uid <- status_field("Uid")
  owner <- if (is.null(uid)) NULL else
    identical(strsplit(uid, "[[:space:]]+")[[1L]][2L], Sys.getenv("ASMA_PROBE_UID"))

  mounts <- read_safe("/proc/self/mountinfo")
  mount <- function(target) {
    if (is.null(mounts)) return(NULL)
    matched <- lapply(mounts, function(line) {
      pieces <- strsplit(line, " - ", fixed = TRUE)[[1L]]
      if (length(pieces) != 2L) return(NULL)
      left <- strsplit(pieces[1L], " ", fixed = TRUE)[[1L]]
      right <- strsplit(pieces[2L], " ", fixed = TRUE)[[1L]]
      if (length(left) < 6L || length(right) < 3L || left[5L] != target) return(NULL)
      list(type = right[1L], options = strsplit(left[6L], ",", fixed = TRUE)[[1L]],
           super_options = strsplit(right[3L], ",", fixed = TRUE)[[1L]])
    })
    matched <- Filter(Negate(is.null), matched)
    if (length(matched) == 1L) matched[[1L]] else NULL
  }
  mounted_readonly <- function(target) {
    value <- mount(target)
    if (is.null(value)) NULL else "ro" %in% value$options
  }
  tmp <- mount("/tmp")
  tmp_guard <- if (is.null(tmp)) NULL else identical(tmp$type, "tmpfs") &&
    all(c("rw", "noexec", "nosuid") %in% tmp$options)
  tmp_size <- if (is.null(tmp)) NULL else {
    value <- tmp$super_options[startsWith(tmp$super_options, "size=")]
    if (length(value) == 1L) identical(value, "size=262144k") else NULL
  }
  temp_under_tmp <- startsWith(normalizePath(tempdir()), "/tmp/")
  marker <- tempfile("abstract-execution-probe-", tmpdir = tempdir())
  on.exit(unlink(marker), add = TRUE)
  write_ok <- tryCatch({
    writeLines("abstract-runtime-marker", marker)
    identical(readLines(marker, warn = FALSE), "abstract-runtime-marker")
  }, error = function(error) FALSE)
  unlink(marker)
  write_ok <- write_ok && !file.exists(marker)

  limits <- read_safe("/proc/self/limits")
  core_line <- limits[startsWith(limits, "Max core file size")]
  core_zero <- if (length(core_line) != 1L) NULL else {
    fields <- strsplit(trimws(sub("^Max core file size", "", core_line)), "[[:space:]]+")[[1L]]
    length(fields) >= 2L && identical(fields[1:2], c("0", "0"))
  }
  cpu <- scalar("/sys/fs/cgroup/cpu.max")
  cpu_limit <- if (is.null(cpu)) NULL else {
    parts <- strsplit(cpu, " ", fixed = TRUE)[[1L]]
    if (length(parts) == 2L && all(grepl("^[0-9]+$", parts)) && as.numeric(parts[2L]) > 0)
      as.numeric(parts[1L]) / as.numeric(parts[2L]) else NULL
  }
  interfaces <- tryCatch(list.files("/sys/class/net"), error = function(error) character())
  routes <- read_safe("/proc/net/route")
  arguments <- commandArgs()
  # Capture the child observations in memory and emit only equality checks for
  # namespace/cgroup identities, never their underlying paths or identifiers.
  python_code <- paste0(
    "import json,os,sys; print(json.dumps({",
    "'version':'.'.join(map(str,sys.version_info[:3])),",
    "'isolated':bool(sys.flags.isolated),'no_user_site':bool(sys.flags.no_user_site),",
    "'no_bytecode':bool(sys.dont_write_bytecode),",
    "'cgroup':open('/proc/self/cgroup').read().splitlines(),",
    "'mount':os.readlink('/proc/self/ns/mnt'),'network':os.readlink('/proc/self/ns/net')",
    "}))"
  )
  python <- tryCatch({
    output <- system2("/opt/python/bin/python3", c("-I", "-B", "-c", shQuote(python_code)),
                      stdout = TRUE, stderr = FALSE)
    if (!is.null(attr(output, "status"))) NULL else jsonlite::fromJSON(paste(output, collapse = "\n"))
  }, error = function(error) NULL, warning = function(warning) NULL)
  same_namespace <- function(name, path) {
    if (is.null(python) || is.null(python[[name]])) return(NULL)
    own <- Sys.readlink(path)
    if (length(own) != 1L || is.na(own) || !nzchar(own)) return(NULL)
    identical(python[[name]], unname(own))
  }
  list(
    schema_version = 1L,
    root_read_only = mounted_readonly("/"), checkout_read_only = mounted_readonly("/work"),
    network_interfaces_loopback_only = if (!length(interfaces)) NULL else setequal(interfaces, "lo"),
    ipv4_route_table_empty = if (is.null(routes)) NULL else length(routes) <= 1L,
    capabilities_all_zero = zero_caps,
    no_new_privileges = if (is.null(status_field("NoNewPrivs"))) NULL else identical(status_field("NoNewPrivs"), "1"),
    runs_as_checkout_owner = owner, core_dump_soft_and_hard_zero = core_zero,
    cgroup_v2 = file.exists("/sys/fs/cgroup/cgroup.controllers"),
    memory_limit_bytes = numeric_limit("/sys/fs/cgroup/memory.max"),
    swap_limit_bytes = numeric_limit("/sys/fs/cgroup/memory.swap.max"),
    cpu_limit = cpu_limit, pids_limit = numeric_limit("/sys/fs/cgroup/pids.max"),
    tmpfs_noexec_nosuid = tmp_guard, tmpfs_limit_256_mib = tmp_size,
    r_tempdir_on_tmpfs = temp_under_tmp && isTRUE(tmp_guard),
    artificial_tmpfs_write_removed = write_ok,
    vanilla_startup = "--vanilla" %in% arguments,
    workspace_save_restore_disabled = all(c("--no-save", "--no-restore") %in% arguments),
    history_disabled = identical(Sys.getenv("R_HISTFILE"), "/dev/null"),
    cache_destinations_on_tmpfs = all(Sys.getenv(c("XDG_CACHE_HOME", "R_USER_CACHE_DIR")) == "/tmp/asma-cache"),
    python_version = python$version, python_isolated_mode = python$isolated,
    python_user_site_disabled = python$no_user_site, python_bytecode_writes_disabled = python$no_bytecode,
    python_shares_cgroup = if (is.null(python$cgroup)) NULL else
      identical(python$cgroup, read_safe("/proc/self/cgroup")),
    python_shares_mount_namespace = same_namespace("mount", "/proc/self/ns/mnt"),
    python_shares_network_namespace = same_namespace("network", "/proc/self/ns/net")
  )
}

status <- tryCatch({
  cat(jsonlite::toJSON(probe_execution_conditions(), auto_unbox = TRUE, null = "null"), "\n")
  0L
}, error = function(error) {
  cat("ERROR: execution-condition probe failed; no environment details emitted.\n", file = stderr())
  1L
})
quit(save = "no", status = status)
