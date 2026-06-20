# python-ggseg PR #10 Context Notes

Saved: 2026-06-21 02:57:43 local time

## PR link

https://github.com/ggsegverse/python-ggseg/pull/10

## PR title

```text
Add shared polygon atlas API for strict R/Python ggseg visual parity
```

## Base and head

```text
base: ggsegverse/python-ggseg:main
head: mqqq333/python-ggseg:proposal/r-ggseg-polygon-interop
```

Local checkout:

```text
E:\learn_pytorch\pythonProject\ggsseg_py\python-ggseg-pr
branch: proposal/r-ggseg-polygon-interop
```

Important commits:

```text
8d4081d Add R ggseg polygon interop proposal
fd1dfde Implement polygon atlas interop API
```

## Why this PR exists

The project goal is strict visual parity between R `ggseg` and Python `python-ggseg` for 2D cortical gray-matter atlas visualizations.

"Strict visual parity" means more than generic interoperability. The desired outcome is that R and Python can render cortical atlas maps with matching:

- atlas geometry;
- parcel shapes;
- boundary layout;
- flat matte material/texture;
- outline style;
- color assignment;
- vector-export behavior.

The motivation came from building the `cortex-visualization-skill`, which needs to match the existing `subcortex-visualization-skill` style while preserving Python and R dual-backend workflows.

## Downstream prototype evidence

The local `cortex-visualization-skill` prototype achieved strict Python/R parity by using:

1. R `ggseg` as the canonical polygon source.
2. A shared exported polygon CSV as the geometry source of truth.
3. A one-pass Chaikin-smoothed display atlas for smoother cortical boundaries:

```text
cortex-visualization/assets/atlases/dk_polygons_chaikin.csv
```

4. A shared `fill_hex` column for backend-independent color assignment.
5. Python and R renderers reading the same plot-data CSV.

Relevant local repo:

```text
E:\learn_pytorch\pythonProject\cortex-visualization-skill-project
GitHub: git@github.com:mqqq333/cortex-visualization-skill.git
```

## What PR #10 implements in python-ggseg

PR #10 is no longer only a documentation proposal. It adds a minimal implementation of the shared polygon atlas path.

Changed files:

```text
modified README.md
added    doc/r_ggseg_polygon_interop_proposal.md
modified ggseg/__init__.py
added    ggseg/tests/test_polygon_interop.py
```

New API functions:

```python
read_polygon_atlas(path)
validate_polygon_atlas(atlas)
join_polygon_values(atlas, data, match_column='label', value_column='value')
plot_polygons(...)
```

Key behavior:

- reads canonical R `ggseg`-exported polygon CSV files;
- validates required schema;
- joins user values by explicit `label` or `region`;
- renders shared polygon coordinates with Matplotlib;
- supports `fill_column='fill_hex'` as identity-color rendering;
- does not change existing `plot_dk`, `plot_aseg`, or `plot_jhu` behavior.

## Expected polygon schema

```text
label, region, hemi, view, x, y, .group, subgroup, .feature_id
```

Optional useful columns:

```text
value, fill_hex, atlas, source_package, source_version, export_date
```

## Tests added

File:

```text
ggseg/tests/test_polygon_interop.py
```

Tests cover:

- reading a polygon atlas CSV;
- schema validation;
- joining values by `label`;
- strict unmatched-label errors;
- plotting with `fill_hex` identity colors.

Local validation performed because `pytest` was not installed in the local Python 3.12 environment:

```text
py -3.12 -m py_compile ggseg\__init__.py ggseg	ests	est_polygon_interop.py
```

Then direct test function calls were run for:

```text
test_polygon_interop.py
existing test_plotting.py smoke test
```

Both passed locally. The only warnings were expected Agg backend non-interactive `plt.show()` warnings from existing plot functions.

## PR description currently used

The PR description states that the PR adds a minimal polygon atlas interoperability API for rendering R `ggseg`-exported 2D polygon atlas tables in `python-ggseg`, with the goal of strict visual parity by sharing geometry and optional `fill_hex` colors.

Checklist notes:

- `New feature` checked.
- `Documentation update` checked.
- `Other: Cross-language visual-parity / interoperability API` checked.
- Tests/documentation checked.
- `devtools::check()` and tidyverse style guide not checked because this is a Python repository / not an R package workflow.

## Current PR state at time of saving

Observed via GitHub API shortly after PR creation:

```text
state: open
commits: 2
changed_files: 4
mergeable_state: unstable
statuses/check_runs: none reported at that time
```

`mergeable_state: unstable` did not correspond to a known failed check at that time. It may mean GitHub had not computed mergeability or no CI/check run had reported yet.

## Likely reviewer feedback and response strategy

### If maintainers say this should first be an issue/discussion

Agree and say this PR can serve as a concrete prototype. Offer to split into:

1. an issue/RFC for API discussion;
2. a smaller implementation PR after interface agreement.

### If maintainers dislike adding API functions to `ggseg/__init__.py`

Offer to move them into a dedicated module, for example:

```text
ggseg/polygon.py
```

and re-export from `ggseg/__init__.py` only if desired.

### If maintainers want pandas support

Current implementation intentionally avoids adding dependencies. A future version could accept pandas DataFrames optionally, but the minimal implementation uses `csv` + list-of-dicts to preserve the current lightweight dependency profile.

### If maintainers object to `fill_hex`

Explain that `fill_hex` is needed for exact cross-backend color parity, because R and Python colormaps can differ slightly. Identity-color rendering makes the color source explicit and reproducible.

### If maintainers ask about smoothing

Clarify that PR #10 does not force smoothing. It supports shared polygon geometry. If smoothing is desired, the recommended safe workflow is to generate a separate shared display atlas, e.g. Chaikin-smoothed CSV, and render the same CSV from both R and Python.

### If maintainers ask for fixtures from R ggseg

We can add a tiny fixture exported from R `ggseg`, or a reduced toy fixture. The current tests use a small synthetic atlas to avoid large fixture files.

### If maintainers request full R/Python visual comparison

Use downstream prototype artifacts from:

```text
E:\learn_pytorch\pythonProject\cortex-visualization-skill-project\demo
```

Key files:

```text
STYLE_AUDIT_cortex_vs_subcortex.png
cortex_dk_demo_python.png/svg/pdf
cortex_dk_demo_r.png/svg/pdf
cortex_dk_demo_plot_data.csv
```

## Useful commands

Check local PR branch:

```powershell
cd E:\learn_pytorch\pythonProject\ggsseg_py\python-ggseg-pr
git status
git log --oneline --decorate -5
```

Push further changes:

```powershell
git push
```

Cortex skill repo:

```powershell
cd E:\learn_pytorch\pythonProject\cortex-visualization-skill-project
git status
git log --oneline --decorate -5
```

## Short summary for future replies

PR #10 proposes and implements a minimal shared-polygon atlas workflow in `python-ggseg` so R `ggseg` and Python can render the same 2D cortical gray-matter geometry. The main design is: shared R ggseg-exported polygon CSV for geometry, explicit label/region joins, optional `fill_hex` identity colors for exact color parity, and no changes to existing native plot functions.
