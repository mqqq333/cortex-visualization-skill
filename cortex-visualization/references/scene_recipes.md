# Scene recipes

Use this file when proposing demos, showcase panels, or figure variants.

## 1. Python/R parity demo

Purpose: prove that Python and R can render the same cortical geometry and colors.

Inputs:

- `assets/examples/dk_demo_values.csv`
- `assets/atlases/dk_polygons_chaikin.csv`

Outputs:

- `demo/cortex_dk_demo_python.png/svg/pdf`
- `demo/cortex_dk_demo_r.png/svg/pdf`
- `demo/cortex_dk_demo_plot_data.csv`

## 2. Style audit against subcortex

Purpose: compare cortex output with the existing subcortex visual language.

Output:

- `demo/STYLE_AUDIT_cortex_vs_subcortex.png`

Check:

- white background;
- matte fills;
- dark outlines;
- flat 2D atlas geometry;
- no Workbench mesh/lighting/curvature.

## 3. Boundary smoothing audit

Purpose: document why the default display asset uses one-pass Chaikin smoothing.

Output:

- `demo/SMOOTHING_EXPERIMENT_cortex_boundaries.png`

Interpretation:

- raw ggseg polygons are faithful but jagged;
- Catmull-Rom can over-round and misfit boundaries;
- one-pass Chaikin gives smoother cortex boundaries with better visual fit.

## 4. README hero showcase

Purpose: a compact GitHub landing image.

Output:

- `assets/gallery/cortex_showcase.png`

It should show Python/R parity and the subcortex-style audit in one image.
