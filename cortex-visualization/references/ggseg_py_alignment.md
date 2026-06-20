# Plan: align ggseg-py with R ggseg

## Motivation

R `ggseg` and Python `python-ggseg` can produce ggseg-style cortical plots, but their native geometry/data paths are not guaranteed to match exactly. For a Python/R dual-backend visualization skill, the most robust path is to make the atlas geometry a shared artifact rather than relying on each backend's native atlas representation.

## Proposed upstream contribution

Add a first-class shared-polygon workflow to `python-ggseg` so Python users can render canonical R `ggseg` atlas exports with predictable parity.

## Canonical schema

Support a CSV or JSON-lines polygon table with these minimum fields:

```text
label, region, hemi, view, x, y, .group, subgroup, .feature_id
```

Optional fields:

```text
value, fill_hex, atlas, source_package, source_version, export_date
```

Semantics:

- `label`: exact join key preferred for reproducibility.
- `region`: human-readable region name.
- `hemi`: left/right.
- `view`: lateral/medial/etc.
- `x`, `y`: positioned 2D polygon coordinates.
- `.feature_id`: parcel polygon feature identifier.
- `subgroup`: ring or multipart polygon group.
- `fill_hex`: optional backend-independent color assigned before plotting.

## Minimal Python API proposal

```python
import ggseg

atlas = ggseg.read_polygon_atlas("dk_polygons.csv")
fig = ggseg.plot_polygons(
    atlas,
    data=values_df,
    match_column="label",
    value_column="value",
    vmin=-1,
    vmax=1,
    midpoint=0,
    edgecolor="#2E2E2E",
    linewidth=0.55,
)
fig.savefig("dk_python.svg")
```

Also support exact-color parity:

```python
plot_data = ggseg.join_values(atlas, values_df, match_column="label", value_column="value")
plot_data = ggseg.assign_fill_hex(plot_data, palette="diverging", vmin=-1, midpoint=0, vmax=1)
ggseg.plot_polygons(plot_data, fill_column="fill_hex")
```

## Export helper proposal for R side

Provide an R helper or documented recipe:

```r
export_ggseg_polygon_atlas(atlas = ggseg::dk(), file = "dk_polygons.csv")
```

This can live in documentation, `ggsegExtra`, or a small interop vignette if it does not belong in core `ggseg`.

## Boundary handling recommendation

Do not make independent per-parcel smoothing a default in `python-ggseg`. It can break shared boundaries. If smoothing is added, it should be topology-preserving:

1. identify shared edges;
2. smooth each shared edge once;
3. rebuild adjacent parcels from the same smoothed edge;
4. test for gaps/overlaps.

Until then, recommend raw polygons plus vector export/high-DPI previews.

## Tests for an upstream PR

1. Load an R-exported DK atlas CSV.
2. Verify expected rows/features/labels.
3. Join a small values table by `label`.
4. Render deterministic SVG without errors.
5. If `fill_hex` is supplied, verify no colormap remapping occurs.
6. Compare Python output against a reference R output at the data/schema level; visual snapshot tests can be optional.

## Contribution pitch

This contribution would give `python-ggseg` a reproducible bridge to the larger R `ggseg` atlas ecosystem, improve cross-language parity, and make it easier for mixed Python/R neuroimaging pipelines to produce consistent publication figures.

## Local evidence from this project

The shared-DK experiment used one R `ggseg`-exported polygon CSV for both renderers and produced matched Python/R outputs with:

```text
rows = 3233
labels = 70
features = 204
fill_hex colors = 63
```

The key lesson is that parity is reliable when geometry and colors are shared explicitly.
