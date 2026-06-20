# Proposal: interoperable R ggseg polygon atlas support for python-ggseg

## Executive summary

This proposal adds a small interoperability layer to `python-ggseg`: the ability to load, validate, join, and render cortical atlas polygon tables exported from R `ggseg`. The goal is not to replace the native Python atlas workflow, but to provide a reproducible bridge between the larger R `ggseg` atlas ecosystem and Python-based neuroimaging pipelines.

The key idea is simple: use a shared polygon atlas file as the source of truth for geometry, and optionally use a precomputed `fill_hex` column as the source of truth for colors. This makes Python and R outputs comparable at the data and figure level.

```text
R ggseg atlas object
  -> canonical polygon CSV / JSON
      -> python-ggseg render
      -> R ggseg / ggplot render
```

## Background

R `ggseg` and `ggseg3d` provide a mature ecosystem for visualizing region-level brain statistics on predefined atlas segmentations. Many neuroimaging workflows, however, are Python-first. At present, Python and R ggseg-style plots may differ because each backend can use different atlas objects, geometry preparation steps, plotting defaults, or color-mapping logic.

For mixed Python/R projects, this creates a reproducibility gap: even when the same values and nominal atlas are used, the final figures may not be guaranteed to share the same geometry and color assignments.

## Problem statement

A Python user should be able to render an atlas exported from R `ggseg` without manually rewriting polygon handling code or accepting silent geometry differences. A project that supports both Python and R should be able to produce matched figures from the same atlas geometry and, when required, the same assigned colors.

## Goals

- Support R `ggseg`-exported polygon atlas files as a first-class input path in `python-ggseg`.
- Provide a documented canonical schema for 2D polygon atlas interchange.
- Allow users to join region-level data by an explicit key such as `label` or `region`.
- Allow exact cross-backend color parity when `fill_hex` is supplied.
- Preserve raw atlas topology by default so adjacent parcel boundaries continue to fit.
- Add validation and tests for schema, joins, missing regions, and deterministic rendering.

## Non-goals

- Do not replace native `python-ggseg` atlas APIs.
- Do not require Python users to install R for normal plotting once an atlas CSV/JSON has been exported.
- Do not make independent per-parcel smoothing a default rendering step.
- Do not attempt to solve 3D mesh interoperability; this proposal is for 2D polygon atlases.

## Proposed canonical polygon schema

A minimal 2D atlas polygon table should include:

| Column | Type | Required | Description |
|---|---:|---:|---|
| `label` | string | yes | Stable parcel label; preferred join key. |
| `region` | string | yes | Human-readable region name. |
| `hemi` | string | yes | Hemisphere, e.g. `left`, `right`. |
| `view` | string | yes | Display view, e.g. `lateral`, `medial`. |
| `x` | numeric | yes | Positioned 2D x coordinate. |
| `y` | numeric | yes | Positioned 2D y coordinate. |
| `.group` | string/int | yes | Polygon group identifier from the ggseg-prepared object. |
| `subgroup` | string/int | yes | Ring/subpolygon identifier for multipart features. |
| `.feature_id` | string/int | yes | Unique displayed polygon feature identifier. |

Optional columns:

| Column | Type | Description |
|---|---:|---|
| `value` | numeric | Region-level statistic after joining user data. |
| `fill_hex` | string | Precomputed color, e.g. `#3B4CC0`; if present, plotting should not remap colors unless explicitly requested. |
| `atlas` | string | Atlas name, e.g. `dk`. |
| `source_package` | string | Source R package, e.g. `ggseg`. |
| `source_version` | string | Source package version. |
| `export_date` | string | Export date or timestamp. |

## Proposed Python API

A minimal API could look like this:

```python
import ggseg

atlas = ggseg.read_polygon_atlas("dk_polygons.csv")

fig = ggseg.plot_polygons(
    atlas,
    data=values_df,
    match_column="label",
    value_column="value",
    palette="diverging",
    vmin=-1,
    midpoint=0,
    vmax=1,
    edgecolor="#2E2E2E",
    linewidth=0.55,
)
fig.savefig("dk_python.svg")
```

For exact color parity with R or another backend:

```python
plot_data = ggseg.join_values(
    atlas,
    values_df,
    match_column="label",
    value_column="value",
)
plot_data = ggseg.assign_fill_hex(
    plot_data,
    palette="diverging",
    vmin=-1,
    midpoint=0,
    vmax=1,
)

ggseg.plot_polygons(plot_data, fill_column="fill_hex")
```

If a table already contains `fill_hex`, the renderer should treat it as an identity color column by default.

## Suggested R export recipe

This could be implemented in documentation, a helper script, or an R-side convenience function:

```r
export_ggseg_polygon_atlas <- function(atlas, file) {
  flat <- ggseg:::prepare_polygon_atlas(
    atlas = atlas,
    hemi = c("left", "right"),
    view = c("lateral", "medial"),
    position = ggseg::position_brain(hemi ~ view),
    context = TRUE,
    focus = NULL
  )

  keep <- c("label", "region", "hemi", "view", "x", "y", ".group", "subgroup", ".feature_id")
  utils::write.csv(flat[, keep], file, row.names = FALSE)
}

export_ggseg_polygon_atlas(ggseg::dk(), "dk_polygons.csv")
```

The exact implementation may need to follow `ggseg` maintainers' preferred public API boundaries. If relying on an internal function is not desirable, this proposal can instead document a supported export path or request a small R-side public export helper.

## Boundary and smoothing policy

Raw ggseg cortex polygons can look angular. However, smoothing each parcel independently changes shared borders separately and can introduce visible gaps or overlaps between adjacent parcels. Therefore, this proposal recommends preserving raw polygon topology by default.

If smoothing is added later, it should be topology-preserving:

1. identify shared boundary segments;
2. smooth each shared segment once;
3. rebuild adjacent parcel polygons from the same smoothed segment;
4. test for gaps, overlaps, and invalid polygons.

Until that exists, recommended output quality improvements are vector export, high-DPI PNG previews, anti-aliasing, reasonable line width, and round line joins.

## Validation and tests

A minimal test set for an upstream PR could include:

1. Load an R-exported DK atlas polygon CSV.
2. Assert required columns are present.
3. Assert expected row, label, and feature counts for the fixture.
4. Join a small values table by `label`.
5. Report unmatched input regions and missing atlas regions.
6. Render SVG/PDF/PNG without errors.
7. Verify that `fill_hex` is treated as an identity color column.
8. Confirm that no smoothing is applied unless explicitly requested.

Optional visual regression testing can compare a rendered SVG/PNG against a stored reference, but schema-level and join-level tests should be the required base.

## Backward compatibility

This can be added as an optional input path without changing existing `python-ggseg` behavior. Native Python atlas rendering remains supported. Users who do not need R interop do not need to change their workflow.

## Documentation additions

Recommended docs/vignette topics:

- "Rendering an R ggseg atlas export in Python"
- "Matching Python and R ggseg-style figures"
- "Using `fill_hex` for exact cross-backend colors"
- "Why per-parcel smoothing is not topology-safe by default"

## Suggested contribution strategy

The GitHub operation for submitting this upstream is a **Pull Request (PR)**. A careful sequence would be:

1. Open an upstream **Issue** or **Discussion/RFC** first, because this is an interoperability/API proposal.
2. Fork the upstream repository.
3. Create a feature branch, for example `feature/r-ggseg-polygon-interop`.
4. Implement the smallest useful slice: reader + validator + identity `fill_hex` plotting + tests.
5. Push the branch to the fork.
6. Open a **Pull Request** from the fork branch to the upstream repository.

## Draft issue / discussion title

```text
Proposal: support R ggseg-exported polygon atlas files for cross-language reproducibility
```

## Draft issue / discussion body

```markdown
Hi, thank you for maintaining python-ggseg. We are building a Python/R dual-backend cortical visualization workflow and found that exact cross-language parity is easiest when both backends render the same polygon geometry.

Would you be open to supporting R ggseg-exported 2D polygon atlas tables as an optional input path in python-ggseg?

The proposed minimum schema is:

label, region, hemi, view, x, y, .group, subgroup, .feature_id

Optional columns such as value and fill_hex would allow joined data and exact identity-color rendering. This would not replace native python-ggseg atlases; it would add an interoperability bridge for users who want to render R ggseg atlas exports in Python.

I would be happy to prepare a small PR with:

- a polygon atlas CSV reader and schema validator;
- explicit join-by-label / join-by-region behavior;
- identity fill_hex rendering;
- a small R-exported DK fixture;
- tests for schema, joins, unmatched labels, and rendering.

One design point: I would not propose per-parcel smoothing as a default, because independent smoothing can break shared boundaries between adjacent parcels. Raw polygons plus vector/high-DPI export are safer by default.
```

## Draft PR title

```text
Add support for R ggseg-exported polygon atlas tables
```

## Draft PR summary

```markdown
This PR adds an optional interoperability path for rendering polygon atlas tables exported from R ggseg. It includes:

- a reader for canonical polygon atlas CSV files;
- schema validation for required ggseg-style columns;
- explicit data joining by label or region;
- identity color rendering via fill_hex;
- tests covering schema validation, joins, unmatched labels, and rendering.

The feature is additive and does not change existing native python-ggseg atlas behavior.
```

## Local evidence from this repository

In the local cortex-visualization skill, a shared DK polygon export was rendered by both Python and R. The shared plot-data table contained:

```text
rows = 3233
labels = 70
features = 204
fill_hex colors = 63
```

The practical lesson is that cross-language parity is reliable when geometry and colors are shared explicitly rather than reconstructed independently in each backend.
