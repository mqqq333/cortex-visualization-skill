# Cortex atlas catalog

Use this file when choosing a cortex atlas or validating that an atlas asset exists.

## Bundled atlas assets

| Atlas | Source | Labels | Features | Raw CSV | Chaikin CSV |
|---|---|---:|---:|---|---|
| `brainnetome` | `ggsegBrainnetome::brainnetome` | 210 | 261 | `brainnetome_polygons.csv` (2.42 MB) | `brainnetome_polygons_chaikin.csv` (3.99 MB) |
| `destrieux` | `ggsegDestrieux::destrieux` | 148 | 210 | `destrieux_polygons.csv` (10.0 MB) | `destrieux_polygons_chaikin.csv` (17.01 MB) |
| `dk` | `ggseg::dk` | 70 | 204 | `dk_polygons.csv` (0.33 MB) | `dk_polygons_chaikin.csv` (0.45 MB) |
| `dkt` | `ggsegDKT::dkt` | 62 | 96 | `dkt_polygons.csv` (0.21 MB) | `dkt_polygons_chaikin.csv` (0.33 MB) |
| `glasser` | `ggsegGlasser::glasser` | 360 | 436 | `glasser_polygons.csv` (12.71 MB) | `glasser_polygons_chaikin.csv` (20.82 MB) |
| `gordon` | `ggsegGordon::gordon` | 331 | 388 | `gordon_polygons.csv` (0.7 MB) | `gordon_polygons_chaikin.csv` (1.07 MB) |
| `power` | `ggsegPower::power` | 130 | 191 | `power_polygons.csv` (0.41 MB) | `power_polygons_chaikin.csv` (0.63 MB) |
| `schaefer17_100` | `ggsegSchaefer::schaefer17_100` | 100 | 142 | `schaefer17_100_polygons.csv` (9.06 MB) | `schaefer17_100_polygons_chaikin.csv` (15.88 MB) |
| `schaefer7_100` | `ggsegSchaefer::schaefer7_100` | 100 | 142 | `schaefer7_100_polygons.csv` (8.63 MB) | `schaefer7_100_polygons_chaikin.csv` (15.02 MB) |
| `yeo17` | `ggsegYeo2011::yeo17` | 34 | 162 | `yeo17_polygons.csv` (7.24 MB) | `yeo17_polygons_chaikin.csv` (12.0 MB) |
| `yeo7` | `ggsegYeo2011::yeo7` | 14 | 85 | `yeo7_polygons.csv` (5.11 MB) | `yeo7_polygons_chaikin.csv` (8.42 MB) |

## Default choice

Use `dk_polygons_chaikin.csv` for the default demo and for direct comparison with the existing subcortex skill.

## Choosing an atlas

- **DK / DKT / Destrieux**: FreeSurfer-style anatomical parcels.
- **Yeo7 / Yeo17 / Schaefer**: functional network/parcellation views.
- **Glasser**: multimodal HCP-MMP style fine cortical parcels.
- **Brainnetome / Gordon / Power**: connectivity/network-oriented cortical parcellations.

## Raw vs Chaikin assets

Each bundled atlas has:

- a raw R ggseg-derived polygon CSV (`*_polygons.csv`);
- a one-pass Chaikin-smoothed display CSV (`*_polygons_chaikin.csv`).

Use the Chaikin CSV for final flat-vector figures unless debugging atlas provenance or smoothing artifacts.

## Inspect an atlas

```bash
python scripts/inspect_cortex_atlas.py --atlas-csv assets/atlases/glasser_polygons_chaikin.csv --list-labels
```
