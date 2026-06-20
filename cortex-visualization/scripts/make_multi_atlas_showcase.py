#!/usr/bin/env python3
"""Render a multi-atlas cortex showcase from bundled atlas CSV assets."""
from __future__ import annotations

import argparse
import csv
import math
from collections import OrderedDict
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon


def read_csv(path: Path):
    with path.open(newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def hex_color(v: float) -> str:
    # compact blue-white-red diverging palette
    low = (59, 76, 192)
    mid = (221, 221, 221)
    high = (180, 4, 38)
    v = max(-1.0, min(1.0, v))
    if v <= 0:
        t = v + 1
        a, b = low, mid
    else:
        t = v
        a, b = mid, high
    rgb = tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(3))
    return "#" + "".join(f"{x:02X}" for x in rgb)


def draw_atlas(ax, rows, title: str):
    labels = sorted({r["label"] for r in rows if r.get("label")})
    label_value = {lab: math.sin((i + 1) / max(1, len(labels)) * math.pi * 2) for i, lab in enumerate(labels)}
    features = OrderedDict()
    xs, ys = [], []
    for r in rows:
        fid = r[".feature_id"]
        subgroup = r.get("subgroup") or "1"
        features.setdefault(fid, {"rings": OrderedDict(), "label": r.get("label", "")})
        x = float(r["x"]); y = float(r["y"])
        features[fid]["rings"].setdefault(subgroup, []).append((x, y))
        xs.append(x); ys.append(y)
    for item in features.values():
        fill = hex_color(label_value.get(item["label"], 0.0))
        for pts in item["rings"].values():
            if len(pts) >= 3:
                ax.add_patch(Polygon(pts, closed=True, facecolor=fill, edgecolor="#2E2E2E", linewidth=0.35, joinstyle="round"))
    pad_x = (max(xs) - min(xs)) * 0.04
    pad_y = (max(ys) - min(ys)) * 0.04
    ax.set_xlim(min(xs) - pad_x, max(xs) + pad_x)
    ax.set_ylim(min(ys) - pad_y, max(ys) + pad_y)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title(f"{title}\n{len(labels)} labels", fontsize=14, color="#2E2E2E", pad=8)


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--project-root", default=str(Path(__file__).resolve().parents[2]))
    p.add_argument("--atlases", default="dk,dkt,yeo7,schaefer7_100,glasser,brainnetome")
    p.add_argument("--output", default="assets/gallery/multi_atlas_showcase.png")
    args = p.parse_args()
    root = Path(args.project_root)
    atlas_dir = root / "cortex-visualization" / "assets" / "atlases"
    atlas_names = [a.strip() for a in args.atlases.split(",") if a.strip()]
    n = len(atlas_names)
    cols = 3
    rows_n = math.ceil(n / cols)
    fig, axes = plt.subplots(rows_n, cols, figsize=(cols * 6, rows_n * 4.2), facecolor="white")
    axes = axes.ravel() if hasattr(axes, "ravel") else [axes]
    for ax, name in zip(axes, atlas_names):
        path = atlas_dir / f"{name}_polygons_chaikin.csv"
        draw_atlas(ax, read_csv(path), name)
    for ax in axes[n:]:
        ax.axis("off")
    fig.suptitle("Bundled cortex atlas showcase", fontsize=24, color="#1F1F1F", y=0.99)
    fig.text(0.5, 0.02, "All panels use shared ggseg-derived Chaikin-smoothed polygon assets; colours are simulated for display.", ha="center", fontsize=12, color="#555555")
    fig.tight_layout(rect=(0, 0.04, 1, 0.95))
    out = root / args.output
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=180, bbox_inches="tight", facecolor="white")
    print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
