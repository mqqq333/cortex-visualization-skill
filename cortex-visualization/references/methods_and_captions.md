# Methods and captions

## Methods template

Cortical region-level values were visualized on a two-dimensional ggseg-derived atlas polygon layout. Atlas polygons were exported from R `ggseg` to a canonical CSV schema containing parcel labels, hemisphere, view, feature identifiers, and polygon coordinates. Python and R renderings used the same polygon CSV and, when exact cross-language color parity was required, the same precomputed `fill_hex` column. Figures were exported as SVG/PDF with PNG previews.

## Caption template

Flat 2D cortical atlas map showing [statistic] for [atlas/parcellation]. Parcel colors encode [value meaning] with [color scale and midpoint]. Dark outlines indicate atlas parcel boundaries. The figure is an atlas-level visualization and does not represent subject-specific cortical geometry.

## Provenance checklist

- Atlas source and export date.
- Join key: `label` or `region`.
- Value column and units.
- Color scale limits and midpoint.
- Backend used for final render: Python, R, or both.
- Export formats and output paths.
