# Boundary quality and Chaikin smoothing decision

## Observed issue

Raw ggseg cortex polygons can look more jagged than the existing subcortex figures because the cortical parcel paths contain many angular coordinate steps. This is visually different from smoother subcortical/cerebellar vector paths.

## Smoothing comparison

The initial `simplify + Catmull-Rom` experiment made individual parcels rounder but caused visible boundary misfit in some areas. The one-pass Chaikin option looked smoother while preserving a better visual fit in the audit image.

## Default decision

Use one-pass Chaikin smoothing as a **canonical atlas preprocessing step** and render the resulting shared CSV in both Python and R:

```text
dk_polygons.csv -> smooth_polygon_atlas.py -> dk_polygons_chaikin.csv
```

The renderer defaults remain `--smooth-boundaries none` so the smoothed asset is not smoothed a second time. This keeps Python/R outputs aligned because both backends read identical coordinates. Recommended rendering settings remain:

- SVG/PDF as the primary deliverables;
- high-DPI PNG previews;
- anti-aliased Matplotlib/ggplot output;
- dark but not overly thick outlines (`#2E2E2E`, default `0.55`);
- `joinstyle="round"` in the Python renderer.

## If smoother cortex boundaries are still required

Use one of these future-safe strategies instead of independent per-parcel smoothing:

1. Smooth a shared boundary graph, then rebuild all adjacent parcel polygons from the same smoothed edges.
2. Use a higher-quality atlas polygon source if available.
3. Make a display-only SVG post-processing pass that smooths shared paths consistently.
4. Clearly label any independent smoothing as experimental and inspect every region boundary.

The current skill keeps renderer-level `--smooth-boundaries none` by default because `dk_polygons_chaikin.csv` is already smoothed. Experimental runtime smoothing options remain available only for visual exploration.
