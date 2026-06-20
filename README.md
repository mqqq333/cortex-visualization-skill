# cortex-visualization-skill

Codex skill for reproducible 2D cortical atlas visualizations with Python/R dual backends, ggseg-derived polygon assets, and subcortex-style SVG/PDF outputs.

## Core idea

Use R `ggseg` as the canonical atlas polygon source, export a shared polygon CSV, and render that same CSV from either Python or R:

```text
R ggseg atlas -> shared polygon CSV -> Python renderer
                              \-> R renderer
```

When exact Python/R parity matters, compute `fill_hex` once and pass the same prejoined plot-data CSV to both renderers.

## Why not Workbench?

The visual target is the same family as the existing subcortex visualization skill: flat 2D polygons, white background, matte fills, dark outlines, and vector export. Workbench/fsLR surface renders have a different mesh/curvature/lighting texture.

## Boundary decision

Raw ggseg cortex boundaries can look jagged, but independent per-parcel smoothing breaks shared boundary fit. The default therefore preserves raw ggseg topology and relies on SVG/PDF/high-DPI anti-aliasing. Experimental smoothing remains available only for exploration.

See:

- `cortex-visualization/references/boundary_quality.md`
- `cortex-visualization/references/style_contract.md`

## Reproduce demo

```powershell
$proj='E:\learn_pytorch\pythonProject\cortex-visualization-skill-project'
$skill="$proj\cortex-visualization"

py -3.12 "$skill\scripts\plot_cortex_table.py" `
  --input "$skill\assets\examples\dk_demo_values.csv" `
  --atlas-csv "$skill\assets\atlases\dk_polygons.csv" `
  --output-prefix "$proj\demo\cortex_dk_demo_python" `
  --match-column label `
  --value-column value `
  --vmin -1 --vmax 1 --midpoint 0 `
  --title "Cortex DK demo - Python" `
  --formats png,svg,pdf `
  --write-plot-data "$proj\demo\cortex_dk_demo_plot_data.csv"

$env:R_LIBS_USER='C:\Users\mqqq3333\R\win-library\4.6'
& 'C:\Program Files\R\R-4.6.0\bin\Rscript.exe' "$skill\scripts\plot_cortex_table.R" `
  --plot-data "$proj\demo\cortex_dk_demo_plot_data.csv" `
  --output-prefix "$proj\demo\cortex_dk_demo_r" `
  --title "Cortex DK demo - R" `
  --formats png,svg,pdf
```

## Upstream contribution direction

`cortex-visualization/references/ggseg_py_alignment.md` drafts a possible `python-ggseg` contribution: support R `ggseg`-exported polygon assets as a first-class input path so Python and R outputs can be aligned reproducibly.

## Citation

Mowinckel AM, Vidal-Pi?eiro D. Visualization of Brain Statistics With R Packages ggseg and ggseg3d. *Advances in Methods and Practices in Psychological Science*. 2020;3(4):466-483. doi:10.1177/2515245920928009
