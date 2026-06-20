#!/usr/bin/env Rscript
# Export a ggseg cortical atlas to the shared polygon CSV format used by this skill.
# Supports atlas symbols that are functions (e.g. ggseg::dk) or atlas objects.

parse_args <- function() {
  x <- commandArgs(trailingOnly = TRUE)
  out <- list(
    atlas = "dk",
    package = "ggseg",
    output = NULL,
    hemi = "left,right",
    view = "lateral,medial",
    position = "hemi~view",
    context = TRUE,
    include_metadata = FALSE
  )
  i <- 1
  while (i <= length(x)) {
    key <- sub("^--", "", x[[i]])
    if (key == "no-context") { out$context <- FALSE; i <- i + 1; next }
    if (key == "include-metadata") { out$include_metadata <- TRUE; i <- i + 1; next }
    if (i == length(x)) stop("Missing value for ", x[[i]])
    val <- x[[i + 1]]
    key <- gsub("-", "_", key)
    if (!key %in% names(out)) stop("Unknown argument --", key)
    out[[key]] <- val
    i <- i + 2
  }
  if (is.null(out$output)) stop("--output is required")
  out
}

resolve_atlas <- function(pkg, atlas_name) {
  if (!requireNamespace(pkg, quietly = TRUE)) stop("Install R package: ", pkg)
  ns <- asNamespace(pkg)
  if (!exists(atlas_name, envir = ns, inherits = FALSE)) {
    stop("Atlas symbol not found: ", pkg, "::", atlas_name)
  }
  obj <- get(atlas_name, envir = ns, inherits = FALSE)
  if (is.function(obj)) obj <- obj()
  if (!inherits(obj, "ggseg_atlas")) {
    stop("Object is not a ggseg_atlas: ", pkg, "::", atlas_name,
         " (class: ", paste(class(obj), collapse = ","), ")")
  }
  obj
}

main <- function() {
  args <- parse_args()
  if (!requireNamespace("ggseg", quietly = TRUE)) stop("Install ggseg")

  atlas_obj <- resolve_atlas(args$package, args$atlas)
  if (!inherits(atlas_obj, "cortical_atlas")) {
    warning("Atlas does not inherit cortical_atlas; export may not be appropriate for cortex skill: ", args$package, "::", args$atlas)
  }

  hemi <- strsplit(args$hemi, ",")[[1]] |> trimws()
  view <- strsplit(args$view, ",")[[1]] |> trimws()
  pos <- switch(args$position,
                "hemi~view" = ggseg::position_brain(hemi ~ view),
                "view~hemi" = ggseg::position_brain(view ~ hemi),
                "horizontal" = ggseg::position_brain("horizontal"),
                stop("Unsupported --position: ", args$position))

  flat <- ggseg:::prepare_polygon_atlas(
    atlas = atlas_obj,
    hemi = hemi,
    view = view,
    position = pos,
    context = args$context,
    focus = NULL
  )

  keep <- c("label", "region", "hemi", "view", "x", "y", ".group", "subgroup", ".feature_id")
  missing <- setdiff(keep, names(flat))
  if (length(missing)) stop("Export missing columns: ", paste(missing, collapse = ", "))
  flat <- flat[, keep]
  if (isTRUE(args$include_metadata)) {
    flat$atlas <- args$atlas
    flat$source_package <- args$package
    flat$source_atlas <- paste(args$package, args$atlas, sep = "::")
  }

  dir.create(dirname(args$output), recursive = TRUE, showWarnings = FALSE)
  write.csv(flat, args$output, row.names = FALSE)
  cat("Wrote ", args$output, "\n", sep = "")
  cat("Atlas: ", args$package, "::", args$atlas, "\n", sep = "")
  cat("Rows: ", nrow(flat), "\n", sep = "")
  cat("Features: ", length(unique(flat[[".feature_id"]])), "\n", sep = "")
  cat("Labels: ", length(unique(flat$label)), "\n", sep = "")
}

main()
