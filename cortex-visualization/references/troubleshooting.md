# Troubleshooting

## Empty plot

Check that the atlas CSV exists and contains required columns:

```text
label, region, hemi, view, x, y, .group, subgroup, .feature_id
```

Then run:

```bash
python scripts/validate_cortex_table.py --input values.csv --atlas-csv assets/atlases/dk_polygons_chaikin.csv --match-column label --value-column value --strict
```

## Many unmatched regions

Likely causes:

- using display names instead of ggseg labels;
- joining by `region` when labels are needed;
- left/right suffix mismatch;
- atlas mismatch.

Prefer `label` for strict parity.

## Python and R colors differ

Use Python to write a shared plot-data CSV with `fill_hex`, then render R with `--plot-data`:

```bash
python scripts/plot_cortex_table.py ... --write-plot-data cortex_plot_data.csv
Rscript scripts/plot_cortex_table.R --plot-data cortex_plot_data.csv --output-prefix cortex_r
```

## Figure looks too jagged

Use `dk_polygons_chaikin.csv`, not the raw `dk_polygons.csv`, for final display. Do not apply renderer-level smoothing again unless explicitly experimenting.

## Figure looks over-smoothed or boundaries look wrong

Switch back to the raw atlas for diagnosis:

```bash
--atlas-csv assets/atlases/dk_polygons.csv
```

Compare against `demo/SMOOTHING_EXPERIMENT_cortex_boundaries.png`.

## R cannot find packages

Set `R_LIBS_USER` if packages are installed in a custom Windows library, then rerun the R command. Read `environment_setup.md` for details.
