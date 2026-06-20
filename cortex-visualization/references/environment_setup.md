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

## Backend principle

Only the selected backend should create the final figure. The other backend may be used to inspect tables or export canonical atlas polygons when the user asks for parity.
