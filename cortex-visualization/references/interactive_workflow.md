# Interactive workflow

Use this file when the user asks for a cortex figure but has not fully specified backend, atlas, data, and export needs.

## Compact loop

```text
backend -> environment check -> figure contract -> atlas/label validation -> preview/export -> QC -> revision
```

## First question

If plotting or extraction code is required and the user has not chosen a backend, ask exactly one concise question and stop:

```text
Do you want Python or R for the final rendering?
```

Suggested explanation:

- Python is better for Python analysis pipelines and scripted batch rendering.
- R is better for tidyverse/ggplot workflows and native ggseg atlas export.
- Exact Python/R parity is achieved by shared polygon CSV plus shared `fill_hex`.

## Figure contract

After backend selection, gather or infer:

1. **Atlas**: DK/desikan by default; another R ggseg atlas if requested.
2. **Geometry asset**: default `dk_polygons_chaikin.csv`; raw `dk_polygons.csv` for provenance or debugging.
3. **Input data**: ROI table path, match column, value column.
4. **Visual claim**: what the plot should demonstrate.
5. **Color scale**: diverging for signed values, sequential for magnitude-only values.
6. **Parity level**: Python-only, R-only, or Python+R matched outputs.
7. **Export**: SVG/PDF primary; PNG preview.
8. **QC risks**: unmatched labels, over-smoothing, misleading color limits, missing values.

If two or more fields are unknown, ask one concise question with 2-3 options. If one field is unknown, choose a sensible default and state it.

## Preview/QC loop

After rendering, report:

- matched/unmatched ROI labels;
- atlas CSV used;
- backend(s) used;
- output files;
- whether a shared plot-data CSV with `fill_hex` was used;
- any visual caveats such as missing values or smoothing provenance.
