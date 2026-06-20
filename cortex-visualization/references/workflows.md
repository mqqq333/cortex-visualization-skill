# Workflows

## 1. Validate an ROI table

Input table should contain one cortical parcel key and one numeric value column, for example:

```csv
label,value
bankssts_left,-0.21
bankssts_right,0.34
```

Validate against the bundled DK polygons:

```bash
python scripts/validate_cortex_table.py \
  --input values.csv \
  --atlas-csv assets/atlases/dk_polygons.csv \
  --match-column label \
  --value-column value \
  --strict
```

## 2. Python render with shared plot data

```bash
python scripts/plot_cortex_table.py \
  --input values.csv \
  --atlas-csv assets/atlases/dk_polygons.csv \
  --output-prefix outputs/cortex_dk_python \
  --match-column label \
  --value-column value \
  --vmin -1 --vmax 1 --midpoint 0 \
  --formats svg,pdf,png \
  --write-plot-data outputs/cortex_dk_plot_data.csv
```

`outputs/cortex_dk_plot_data.csv` includes one row per polygon coordinate plus `value` and `fill_hex`. Use it for R parity rendering.

## 3. R render from the same plot data

```bash
Rscript scripts/plot_cortex_table.R \
  --plot-data outputs/cortex_dk_plot_data.csv \
  --output-prefix outputs/cortex_dk_r \
  --formats svg,pdf,png
```

This avoids tiny color-scale differences across languages.

## 4. R render by joining values directly

```bash
Rscript scripts/plot_cortex_table.R \
  --input values.csv \
  --atlas-csv assets/atlases/dk_polygons.csv \
  --output-prefix outputs/cortex_dk_r \
  --match-column label \
  --value-column value \
  --vmin -1 --vmax 1 --midpoint 0 \
  --formats svg,pdf,png
```

## 5. Export a new ggseg atlas from R

```bash
Rscript scripts/export_ggseg_atlas.R \
  --atlas dk \
  --package ggseg \
  --output assets/atlases/dk_polygons.csv \
  --hemi left,right \
  --view lateral,medial \
  --position hemi~view
```

Expected schema:

```text
label, region, hemi, view, x, y, .group, subgroup, .feature_id
```

Keep this schema stable so Python and R renderers can share the same asset.
