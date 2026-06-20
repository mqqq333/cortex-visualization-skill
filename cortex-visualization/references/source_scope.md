# Source scope

This skill is a thin reproducibility layer around ggseg-style cortical atlas polygons. It is not a replacement for R `ggseg`, `ggseg3d`, Workbench, Nilearn, or FreeSurfer.

Source concepts:

- `ggseg` renders predefined brain segmentations as 2D polygons with ggplot2-style grammar.
- `ggseg3d` covers 3D mesh-style visualizations.
- Region-level empirical data are joined to atlas regions and rendered as filled atlas parcels.
- For this skill, R `ggseg` is treated as the canonical source for polygon atlas exports because it has the richer atlas ecosystem and stable atlas objects.

Citation to include when appropriate:

Mowinckel AM, Vidal-Pi?eiro D. Visualization of Brain Statistics With R Packages ggseg and ggseg3d. *Advances in Methods and Practices in Psychological Science*. 2020;3(4):466-483. doi:10.1177/2515245920928009

Claim boundary: a cortex atlas plot visualizes region-level values on atlas parcels. It does not show subject-native anatomy, vertex-wise data, curvature, sulcal depth, or statistical significance unless those were explicitly computed upstream.
