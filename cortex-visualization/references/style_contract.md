# Cortex/Subcortex Style Contract

Use this style when the user wants cortex figures to match the existing `subcortex-visualization` skill.

## Visual target

The target is a flat atlas-polygon figure, not a Workbench/fsLR surface render.

Required visual features:

- white background (`#FFFFFF`);
- matte filled parcels, no lighting, curvature, mesh, or 3D shading;
- dark parcel outlines (`#2E2E2E`);
- default cortex outline width `0.55` in the bundled renderers;
- use the shared Chaikin-smoothed atlas asset by default (`dk_polygons_chaikin.csv`) and keep renderer-level `--smooth-boundaries none`;
- SVG/PDF as primary outputs, PNG as preview;
- explicit `fill_hex` colors for Python/R parity when exact consistency matters.

## Confirmed audit

A visual audit was generated at:

```text
demo/STYLE_AUDIT_cortex_vs_subcortex.png
```

It compares the new cortex demo against representative panels from the existing `subcortex-visualization-skill-project/assets/gallery/all_atlas_showcase.png`.

Conclusion: the cortex renderer is in the same flat/vector family as the existing subcortex figures after bumping default outlines from `0.35` to `0.55`.

Boundary decision: use one-pass Chaikin smoothing as a **canonical atlas preprocessing step**, not as a backend-specific render-time effect. This produced a smoother cortex style than the raw ggseg polygons and looked better than the `simplify + Catmull-Rom` experiment. For Python/R parity, both renderers should read the same `dk_polygons_chaikin.csv` and should not apply extra smoothing during rendering. Keep `dk_polygons.csv` as the raw provenance asset and fallback.

## Important distinction

Python `python-ggseg` and R `ggseg` native geometries are not identical. For cross-backend parity, use shared exported polygon assets plus shared `fill_hex`, then render with the Python or R backend.
