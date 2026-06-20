#!/usr/bin/env Rscript
# Export a ggseg cortical atlas to the shared polygon CSV format used by this skill.

parse_args <- function() {
  x <- commandArgs(trailingOnly = TRUE)
  out <- list(atlas = "dk", package = "ggseg", output = NULL, hemi = "left,right", view = "lateral,medial", position = "hemi~view", context = TRUE)
  i <- 1
  while (i <= length(x)) {
    key <- sub("^--", "", x[[i]])
    if (key == "no-context") { out$context <- FALSE; i <- i + 1; next }
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

main <- function() {
  args <- parse_args()
  if (!requireNamespace(args$package, quietly = TRUE)) stop("Install R package: ", args$package)
  if (!requireNamespace("ggseg", quietly = TRUE)) stop("Install ggseg")
  ns <- asNamespace(args$package)
  if (!exists(args$atlas, envir = ns, mode = "function")) stop("Atlas function not found: ", args$package, "::", args$atlas)
  atlas_obj <- get(args$atlas, envir = ns, mode = "function")()
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
  dir.create(dirname(args$output), recursive = TRUE, showWarnings = FALSE)
  write.csv(flat, args$output, row.names = FALSE)
  cat("Wrote ", args$output, "\n", sep = "")
  cat("Rows: ", nrow(flat), "\n", sep = "")
  cat("Features: ", length(unique(flat[[".feature_id"]])), "\n", sep = "")
  cat("Labels: ", length(unique(flat$label)), "\n", sep = "")
}

main()
