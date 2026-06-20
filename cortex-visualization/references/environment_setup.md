# Environment setup

## Python

Required for bundled Python renderer:

```bash
python -m pip install matplotlib
```

Check:

```bash
python scripts/check_cortex_environment.py --backend python
```

The Python renderer intentionally avoids depending on `python-ggseg` for final parity plots; it reads the shared polygon CSV directly.

## R

Required for R renderer:

```r
install.packages(c("ggplot2", "svglite"))
# install ggseg and ggseg.formats from the source appropriate for the project environment
```

Check:

```bash
python scripts/check_cortex_environment.py --backend r
```

On Windows, if packages live outside the default library path, set `R_LIBS_USER` before running `Rscript`.

Atlas export requires the source R package that owns the atlas symbol. Examples:

- `ggseg::dk`
- `ggsegDKT::dkt`
- `ggsegDestrieux::destrieux`
- `ggsegYeo2011::yeo7` / `yeo17`
- `ggsegSchaefer::schaefer7_100` / `schaefer17_100`
- `ggsegGlasser::glasser`
- `ggsegBrainnetome::brainnetome`
- `ggsegGordon::gordon`
- `ggsegPower::power`

If a bundled CSV already exists, plotting does not require the corresponding R
atlas package; only re-exporting does.

## Backend principle

Only the selected backend should create the final figure. The other backend may be used to inspect tables or export canonical atlas polygons when the user asks for parity.
