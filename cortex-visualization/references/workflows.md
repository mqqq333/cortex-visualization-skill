# Workflows

## 1. Validate an ROI table

Input table should contain one cortical parcel key and one numeric value column, for example:

```csv
label,value
bankssts_left,-0.21
bankssts_right,0.34
```

Validate against the bundled DK polygons, or replace the atlas CSV with another
bundled asset from `references/atlas_catalog.md`:

```bash
python scripts/validate_cortex_table.py \
  --input values.csv \
  --atlas-csv assets/atlases/dk_polygons_chaikin.csv \
  --match-column label \
  --value-column value \
  --strict
```

## 2. Python render with shared plot data

```bash
python scripts/plot_cortex_table.py \
  --input values.csv \
  --atlas-csv assets/atlases/dk_polygons_chaikin.csv \
  --output-prefix outputs/cortex_dk_python \
  --match-column label \
  --value-column value \
  --vmin -1 --vmax 1 --midpoint 0 \
  --formats svg,pdf,png \
  --write-plot-data outputs/cortex_dk_plot_data.csv
```

`outputs/cortex_dk_plot_data.csv` includes one row per polygon coordinate plus `value` and `fill_hex`. Use it for R parity rendering.

For another bundled atlas, keep the same command shape and swap both the ROI
labels and atlas file, for example:

```bash
python scripts/plot_cortex_table.py \
  --input glasser_values.csv \
  --atlas-csv assets/atlases/glasser_polygons_chaikin.csv \
  --output-prefix outputs/cortex_glasser_python \
  --match-column label \
  --value-column value \
  --formats svg,pdf,png \
  --write-plot-data outputs/cortex_glasser_plot_data.csv
```

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
  --atlas-csv assets/atlases/dk_polygons_chaikin.csv \
  --output-prefix outputs/cortex_dk_r \
  --match-column label \
  --value-column value \
  --vmin -1 --vmax 1 --midpoint 0 \
  --formats svg,pdf,png
```

## 5. Inspect bundled atlases

Use the catalog first:

```bash
python scripts/inspect_cortex_atlas.py \
  --atlas-csv assets/atlases/glasser_polygons_chaikin.csv \
  --list-labels \
  --limit 20
```

Bundled cortical atlas families currently include DK, DKT, Destrieux, Yeo7,
Yeo17, Schaefer 7/17-network 100-parcel, Glasser, Brainnetome, Gordon, and
Power. Each has a raw `*_polygons.csv` and a default display
`*_polygons_chaikin.csv`.

## 6. Export a new ggseg atlas from R

```bash
Rscript scripts/export_ggseg_atlas.R \
  --atlas dk \
  --package ggseg \
  --output assets/atlases/dk_polygons.csv \
  --hemi left,right \
  --view lateral,medial \
  --position hemi~view
```

For ggsegverse extension packages:

```bash
Rscript scripts/export_ggseg_atlas.R \
  --atlas glasser \
  --package ggsegGlasser \
  --output assets/atlases/glasser_polygons.csv \
  --hemi left,right \
  --view lateral,medial \
  --position hemi~view \
  --include-metadata
```

Expected schema:

```text
label, region, hemi, view, x, y, .group, subgroup, .feature_id
```

Keep this schema stable so Python and R renderers can share the same asset.
When `--include-metadata` is used, additional provenance columns such as
`atlas`, `source_package`, and `source_atlas` may be appended; renderers should
ignore unknown columns.

## 7. Generate the default Chaikin-smoothed display atlas

After exporting a raw R ggseg atlas, generate the smoother display asset used by default:

```bash
python scripts/smooth_polygon_atlas.py \
  --input assets/atlases/dk_polygons.csv \
  --output assets/atlases/dk_polygons_chaikin.csv \
  --iterations 1 \
  --ratio 0.25
```

Use the smoothed CSV for final Python/R figures. Keep the raw CSV for provenance and fallback. Do not apply renderer-level smoothing again unless explicitly experimenting.
