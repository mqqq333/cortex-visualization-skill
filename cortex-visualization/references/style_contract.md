# Cortex/Subcortex Style Contract

Use this style when the user wants cortex figures to match the existing `subcortex-visualization` skill.

## Visual target

The target is a flat atlas-polygon figure, not a Workbench/fsLR surface render.

Required visual features:

- white background (`#FFFFFF`);
- matte filled parcels, no lighting, curvature, mesh, or 3D shading;
- dark parcel outlines (`#2E2E2E`);
- default cortex outline width `0.55` in the bundled renderers;
- preserve the ggseg polygon topology by default (`--smooth-boundaries none`);
- SVG/PDF as primary outputs, PNG as preview;
- explicit `fill_hex` colors for Python/R parity when exact consistency matters.

## Confirmed audit

A visual audit was generated at:

```text
demo/STYLE_AUDIT_cortex_vs_subcortex.png
```

It compares the new cortex demo against representative panels from the existing `subcortex-visualization-skill-project/assets/gallery/all_atlas_showcase.png`.

Conclusion: the cortex renderer is in the same flat/vector family as the existing subcortex figures after bumping default outlines from `0.35` to `0.55`.

Boundary caveat: do **not** make per-parcel smoothing the default. A `simplify + Catmull-Rom`
experiment made individual parcel outlines look rounder, but adjacent cortical parcels no
longer shared exactly the same boundary, producing visible non-fitting edges. Treat smoothing
as an experimental preview only. For final Python/R parity figures, keep raw shared polygons
and rely on vector export, anti-aliasing, high-DPI PNG previews, line join style, and line width.

## Important distinction

Python `python-ggseg` and R `ggseg` native geometries are not identical. For cross-backend parity, use shared exported polygon assets plus shared `fill_hex`, then render with the Python or R backend.
