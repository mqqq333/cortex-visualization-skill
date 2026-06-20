#!/usr/bin/env python3
"""Create a display-smoothed cortical polygon atlas CSV from a shared ggseg-derived atlas CSV.

The default smoother is one-pass Chaikin corner cutting. This is intended as a
visual-display asset generator: both Python and R renderers should read the same
smoothed CSV when cross-backend parity matters.
"""
from __future__ import annotations

import argparse
import csv
from collections import OrderedDict
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEFAULT_INPUT = HERE.parent / "assets" / "atlases" / "dk_polygons.csv"
DEFAULT_OUTPUT = HERE.parent / "assets" / "atlases" / "dk_polygons_chaikin.csv"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def chaikin_closed(points: list[tuple[float, float]], iterations: int = 1, ratio: float = 0.25) -> list[tuple[float, float]]:
    pts = points[:]
    if pts and pts[0] == pts[-1]:
        pts = pts[:-1]
    if len(pts) < 3:
        return pts
    ratio = max(0.0, min(0.5, float(ratio)))
    for _ in range(max(0, int(iterations))):
        out: list[tuple[float, float]] = []
        n = len(pts)
        for i in range(n):
            p = pts[i]
            q = pts[(i + 1) % n]
            out.append(((1 - ratio) * p[0] + ratio * q[0], (1 - ratio) * p[1] + ratio * q[1]))
            out.append((ratio * p[0] + (1 - ratio) * q[0], ratio * p[1] + (1 - ratio) * q[1]))
        pts = out
    return pts


def smooth_rows(rows: list[dict[str, str]], iterations: int, ratio: float, precision: int) -> list[dict[str, str]]:
    if not rows:
        return []
    required = {"x", "y", ".feature_id", "subgroup"}
    missing = required - set(rows[0].keys())
    if missing:
        raise SystemExit(f"Input atlas missing required columns: {sorted(missing)}")

    groups: OrderedDict[tuple[str, str], list[dict[str, str]]] = OrderedDict()
    for row in rows:
        groups.setdefault((row[".feature_id"], row.get("subgroup") or "1"), []).append(row)

    fmt = f"{{:.{precision}f}}"
    out_rows: list[dict[str, str]] = []
    for (_fid, _subgroup), ring_rows in groups.items():
        points = [(float(r["x"]), float(r["y"])) for r in ring_rows]
        smoothed = chaikin_closed(points, iterations=iterations, ratio=ratio)
        template = dict(ring_rows[0])
        for x, y in smoothed:
            row = dict(template)
            row["x"] = fmt.format(x).rstrip("0").rstrip(".")
            row["y"] = fmt.format(y).rstrip("0").rstrip(".")
            out_rows.append(row)
    return out_rows


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--input", default=str(DEFAULT_INPUT), help="Raw shared polygon atlas CSV")
    p.add_argument("--output", default=str(DEFAULT_OUTPUT), help="Smoothed polygon atlas CSV")
    p.add_argument("--iterations", type=int, default=1, help="Chaikin iterations; 1 is the recommended display default")
    p.add_argument("--ratio", type=float, default=0.25, help="Chaikin corner-cutting ratio in [0, 0.5]")
    p.add_argument("--precision", type=int, default=6, help="Decimal precision for output coordinates")
    args = p.parse_args()

    rows = read_csv(Path(args.input))
    if not rows:
        raise SystemExit("Input atlas is empty")
    out = smooth_rows(rows, args.iterations, args.ratio, args.precision)
    write_csv(Path(args.output), out, list(rows[0].keys()))
    print(f"Wrote {args.output}")
    print(f"Input rows: {len(rows)}")
    print(f"Output rows: {len(out)}")
    print(f"Features: {len({r['.feature_id'] for r in out})}")
    print(f"Labels: {len({r['label'] for r in out if r.get('label')})}")
    print(f"Smoother: chaikin iterations={args.iterations} ratio={args.ratio}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
