#!/usr/bin/env Rscript
# Plot shared 2D cortical polygons from a ggseg-derived atlas CSV.
`%||%` <- function(a, b) if (!is.null(a)) a else b
if (nzchar(Sys.getenv("R_LIBS_USER"))) .libPaths(c(Sys.getenv("R_LIBS_USER"), .libPaths()))

script_file <- function() {
  ca <- commandArgs(FALSE)
  hit <- grep("^--file=", ca, value = TRUE)
  if (length(hit)) return(normalizePath(sub("^--file=", "", hit[[1]]), winslash = "/", mustWork = TRUE))
  normalizePath(sys.frames()[[1]]$ofile %||% getwd(), winslash = "/", mustWork = FALSE)
}
parse_args <- function() {
  x <- commandArgs(trailingOnly = TRUE)
  default_atlas <- file.path(dirname(dirname(script_file())), "assets", "atlases", "dk_polygons_chaikin.csv")
  out <- list(
    input = NULL,
    plot_data = NULL,
    atlas_csv = default_atlas,
    output_prefix = NULL,
    value_column = "value",
    match_column = "auto",
    strict = FALSE,
    write_plot_data = NULL,
    vmin = NA_real_,
    vmax = NA_real_,
    midpoint = 0,
    low = "#3B4CC0",
    mid = "#DDDDDD",
    high = "#B40426",
    na_fill = "#CCCCCC",
    background = "#FFFFFF",
    edgecolor = "#2E2E2E",
    linewidth = 0.55,
    font_family = "sans",
    title = "",
    title_size = 18,
    width = 12,
    height = 8,
    formats = "svg,pdf,png"
  )
  i <- 1
  while (i <= length(x)) {
    key <- sub("^--", "", x[[i]])
    if (key == "strict") {
      out$strict <- TRUE; i <- i + 1; next
    }
    if (i == length(x)) stop("Missing value for ", x[[i]])
    val <- x[[i + 1]]
    key <- gsub("-", "_", key)
    if (!key %in% names(out)) stop("Unknown argument --", key)
    if (key %in% c("vmin", "vmax", "midpoint", "linewidth", "title_size", "width", "height")) val <- as.numeric(val)
    out[[key]] <- val
    i <- i + 2
  }
  out
}

hex_to_rgb <- function(hex) {
  hex <- gsub("#", "", hex)
  c(strtoi(substr(hex, 1, 2), 16L), strtoi(substr(hex, 3, 4), 16L), strtoi(substr(hex, 5, 6), 16L))
}
lerp <- function(a, b, t) {
  t <- max(0, min(1, t))
  a + (b - a) * t
}
rgb_to_hex <- function(rgb) {
  rgb <- pmax(0, pmin(255, round(rgb)))
  sprintf("#%02X%02X%02X", rgb[[1]], rgb[[2]], rgb[[3]])
}
value_to_hex <- function(value, vmin, midpoint, vmax, low, mid, high, na_fill) {
  if (is.na(value)) return(toupper(na_fill))
  lo <- hex_to_rgb(low); mi <- hex_to_rgb(mid); hi <- hex_to_rgb(high)
  if (value <= midpoint) {
    denom <- midpoint - vmin
    t <- if (denom == 0) 0.5 else (value - vmin) / denom
    return(rgb_to_hex(lerp(lo, mi, t)))
  }
  denom <- vmax - midpoint
  t <- if (denom == 0) 0.5 else (value - midpoint) / denom
  rgb_to_hex(lerp(mi, hi, t))
}

choose_match_column <- function(table, atlas, requested) {
  if (requested != "auto") return(requested)
  if ("label" %in% names(table) && "label" %in% names(atlas)) return("label")
  if ("region" %in% names(table) && "region" %in% names(atlas)) return("region")
  stop("Could not choose match column automatically; provide --match-column label or region")
}

build_plot_rows <- function(args) {
  if (!is.null(args$plot_data)) {
    flat <- read.csv(args$plot_data, check.names = FALSE, stringsAsFactors = FALSE)
    if (!"fill_hex" %in% names(flat)) stop("--plot-data must contain fill_hex")
    return(flat)
  }
  if (is.null(args$input)) stop("Provide --input ROI table or --plot-data")
  atlas <- read.csv(args$atlas_csv, check.names = FALSE, stringsAsFactors = FALSE)
  table <- read.csv(args$input, check.names = FALSE, stringsAsFactors = FALSE)
  if (!args$value_column %in% names(table)) stop("Missing value column: ", args$value_column)
  match_col <- choose_match_column(table, atlas, args$match_column)
  vals <- suppressWarnings(as.numeric(table[[args$value_column]]))
  if (any(is.na(vals))) stop("Non-numeric or missing values in input column: ", args$value_column)
  names(vals) <- table[[match_col]]
  flat <- atlas
  flat$value <- vals[flat[[match_col]]]
  matched <- intersect(unique(table[[match_col]]), unique(atlas[[match_col]]))
  unmatched <- setdiff(unique(table[[match_col]]), unique(atlas[[match_col]]))
  if (length(unmatched) && isTRUE(args$strict)) stop("Unmatched input keys: ", paste(head(unmatched, 20), collapse = ", "))
  finite_vals <- vals[is.finite(vals)]
  vmin <- if (is.na(args$vmin)) min(finite_vals) else args$vmin
  vmax <- if (is.na(args$vmax)) max(finite_vals) else args$vmax
  flat$fill_hex <- vapply(flat$value, value_to_hex, character(1),
                          vmin = vmin, midpoint = args$midpoint, vmax = vmax,
                          low = args$low, mid = args$mid, high = args$high,
                          na_fill = args$na_fill)
  message("Stats: rows=", nrow(flat), ", matched=", length(matched), ", unmatched=", length(unmatched), ", vmin=", vmin, ", vmax=", vmax, ", midpoint=", args$midpoint)
  flat
}

main <- function() {
  args <- parse_args()
  if (is.null(args$output_prefix)) stop("--output-prefix is required")
  if (!requireNamespace("ggplot2", quietly = TRUE)) stop("Install ggplot2")
  flat <- build_plot_rows(args)
  if (!is.null(args$write_plot_data)) write.csv(flat, args$write_plot_data, row.names = FALSE)
  p <- ggplot2::ggplot(flat, ggplot2::aes(x = x, y = y, group = .data[[".feature_id"]], subgroup = subgroup)) +
    ggplot2::geom_polygon(ggplot2::aes(fill = fill_hex), colour = args$edgecolor, linewidth = args$linewidth) +
    ggplot2::scale_fill_identity() +
    ggplot2::coord_fixed() +
    ggplot2::labs(title = args$title) +
    ggplot2::theme_void(base_family = args$font_family) +
    ggplot2::theme(
      plot.background = ggplot2::element_rect(fill = args$background, colour = NA),
      panel.background = ggplot2::element_rect(fill = args$background, colour = NA),
      plot.title = ggplot2::element_text(hjust = 0.5, colour = args$edgecolor, size = args$title_size)
    )
  dir.create(dirname(args$output_prefix), recursive = TRUE, showWarnings = FALSE)
  for (fmt in strsplit(args$formats, ",")[[1]]) {
    fmt <- sub("^\\.", "", trimws(fmt))
    out <- paste0(args$output_prefix, ".", fmt)
    if (tolower(fmt) == "pdf") {
      ggplot2::ggsave(out, plot = p, width = args$width, height = args$height, bg = args$background, device = grDevices::cairo_pdf)
    } else {
      ggplot2::ggsave(out, plot = p, width = args$width, height = args$height, dpi = 300, bg = args$background)
    }
    message("Wrote ", out)
  }
}

main()

