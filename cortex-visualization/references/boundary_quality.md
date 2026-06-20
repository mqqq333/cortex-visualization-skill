# Boundary quality and smoothing decision

## Observed issue

Raw ggseg cortex polygons can look more jagged than the existing subcortex figures because the cortical parcel paths contain many angular coordinate steps. This is visually different from smoother subcortical/cerebellar vector paths.

## Rejected default: per-parcel smoothing

A `simplify + Catmull-Rom` experiment made individual cortical parcels appear rounder, but it changed each parcel independently. Adjacent parcels no longer used exactly the same shared edge, so the audit image showed imperfect boundary fit, small gaps, and overlap-like seams.

Therefore per-parcel smoothing must **not** be the default for final figures.

## Default decision

Preserve the raw shared ggseg polygon topology and improve perceived edge quality through rendering choices:

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

The current skill keeps `--smooth-boundaries none` by default. Experimental options remain available only for visual exploration.
