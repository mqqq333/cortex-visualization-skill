#!/usr/bin/env python3
"""Plot 2D cortical atlas polygons from a shared ggseg-derived atlas CSV."""
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

HERE = Path(__file__).resolve().parent
DEFAULT_ATLAS = HERE.parent / "assets" / "atlases" / "dk_polygons_chaikin.csv"


def parse_hex(text: str) -> tuple[int, int, int]:
    text = text.strip().lstrip("#")
    if len(text) != 6:
        raise ValueError(f"Expected 6-digit hex color, got {text!r}")
    return tuple(int(text[i:i + 2], 16) for i in (0, 2, 4))


def to_hex(rgb: tuple[float, float, float]) -> str:
    return "#" + "".join(f"{max(0, min(255, int(round(x)))):02X}" for x in rgb)


def lerp(a: tuple[int, int, int], b: tuple[int, int, int], t: float) -> tuple[float, float, float]:
    t = max(0.0, min(1.0, t))
    return tuple(a[i] + (b[i] - a[i]) * t for i in range(3))


def value_to_hex(value: float | None, vmin: float, midpoint: float, vmax: float,
                 low: str, mid: str, high: str, na_fill: str) -> str:
    if value is None or math.isnan(value):
        return na_fill.upper()
    lo, mi, hi = parse_hex(low), parse_hex(mid), parse_hex(high)
    if value <= midpoint:
        denom = midpoint - vmin
        t = 0.5 if denom == 0 else (value - vmin) / denom
        return to_hex(lerp(lo, mi, t))
    denom = vmax - midpoint
    t = 0.5 if denom == 0 else (value - midpoint) / denom
    return to_hex(lerp(mi, hi, t))


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        raise ValueError("No rows to write")
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def choose_match_column(table_rows: list[dict[str, str]], atlas_rows: list[dict[str, str]], requested: str) -> str:
    if requested != "auto":
        return requested
    table_cols = set(table_rows[0].keys()) if table_rows else set()
    for col in ("label", "region"):
        if col in table_cols and col in atlas_rows[0]:
            return col
    raise SystemExit("Could not choose match column automatically; provide --match-column label or region")


def build_plot_rows(args: argparse.Namespace) -> tuple[list[dict[str, str]], dict[str, int]]:
    if args.plot_data:
        rows = read_csv(Path(args.plot_data))
        if "fill_hex" not in rows[0]:
            raise SystemExit("--plot-data must contain a fill_hex column")
        return rows, {"rows": len(rows), "matched": -1, "unmatched": -1}

    if not args.input:
        raise SystemExit("Provide --input ROI table or --plot-data prejoined polygon CSV")
    atlas_rows = read_csv(Path(args.atlas_csv))
    table_rows = read_csv(Path(args.input))
    if not atlas_rows:
        raise SystemExit("Atlas CSV is empty")
    if not table_rows:
        raise SystemExit("Input table is empty")
    if args.value_column not in table_rows[0]:
        raise SystemExit(f"Missing value column {args.value_column!r} in input table")

    match_col = choose_match_column(table_rows, atlas_rows, args.match_column)
    values: dict[str, float] = {}
    bad_values: list[str] = []
    for row in table_rows:
        key = str(row.get(match_col, "")).strip()
        if not key:
            continue
        try:
            values[key] = float(row[args.value_column])
        except Exception:
            bad_values.append(key)
    if bad_values:
        raise SystemExit(f"Non-numeric values for {len(bad_values)} rows; first: {bad_values[:5]}")
    if not values:
        raise SystemExit("No usable values found in input table")

    finite_values = [v for v in values.values() if not math.isnan(v)]
    vmin = args.vmin if args.vmin is not None else min(finite_values)
    vmax = args.vmax if args.vmax is not None else max(finite_values)
    midpoint = args.midpoint

    rows: list[dict[str, str]] = []
    matched_keys: set[str] = set()
    for row in atlas_rows:
        out = dict(row)
        key = str(row.get(match_col, "")).strip()
        value = values.get(key)
        if value is not None:
            matched_keys.add(key)
            out["value"] = f"{value:.12g}"
        else:
            out["value"] = ""
        out["fill_hex"] = value_to_hex(value, vmin, midpoint, vmax, args.low, args.mid, args.high, args.na_fill)
        rows.append(out)

    unmatched_input = sorted(set(values) - matched_keys)
    if unmatched_input and args.strict:
        raise SystemExit(f"Unmatched input {match_col}s: {', '.join(unmatched_input[:20])}")
    return rows, {
        "rows": len(rows),
        "matched": len(matched_keys),
        "unmatched": len(unmatched_input),
        "vmin": vmin,
        "vmax": vmax,
        "midpoint": midpoint,
    }


def _perpendicular_distance(point, start, end):
    px, py = point
    ax, ay = start
    bx, by = end
    dx = bx - ax
    dy = by - ay
    if dx == 0 and dy == 0:
        return math.hypot(px - ax, py - ay)
    return abs(dy * px - dx * py + bx * ay - by * ax) / math.hypot(dx, dy)


def _rdp_open(points, epsilon):
    """Ramer-Douglas-Peucker simplification for an open polyline."""
    if len(points) <= 2:
        return points[:]
    start, end = points[0], points[-1]
    max_dist = -1.0
    index = 0
    for i, point in enumerate(points[1:-1], 1):
        dist = _perpendicular_distance(point, start, end)
        if dist > max_dist:
            max_dist = dist
            index = i
    if max_dist > epsilon:
        return _rdp_open(points[:index + 1], epsilon)[:-1] + _rdp_open(points[index:], epsilon)
    return [start, end]


def _simplify_closed(points, epsilon):
    """Simplify a closed polygon ring without the first==last degeneracy."""
    pts = points[:]
    if len(pts) < 4 or epsilon <= 0:
        return pts
    if pts[0] == pts[-1]:
        pts = pts[:-1]
    n = len(pts)
    best_i, best_j, best_d = 0, n // 2, -1.0
    for i in range(n):
        xi, yi = pts[i]
        for j in range(i + 1, n):
            xj, yj = pts[j]
            d = (xi - xj) ** 2 + (yi - yj) ** 2
            if d > best_d:
                best_i, best_j, best_d = i, j, d
    chain1 = pts[best_i:best_j + 1]
    chain2 = pts[best_j:] + pts[:best_i + 1]
    return _rdp_open(chain1, epsilon)[:-1] + _rdp_open(chain2, epsilon)[:-1]


def _catmull_rom_closed(points, samples=8):
    """Interpolate a closed ring through its vertices with Catmull-Rom curves."""
    pts = points[:]
    if len(pts) < 4:
        return pts
    if pts[0] == pts[-1]:
        pts = pts[:-1]
    n = len(pts)
    out = []
    samples = max(1, int(samples))
    for i in range(n):
        p0 = pts[(i - 1) % n]
        p1 = pts[i]
        p2 = pts[(i + 1) % n]
        p3 = pts[(i + 2) % n]
        for s in range(samples):
            t = s / samples
            t2 = t * t
            t3 = t2 * t
            x = 0.5 * ((2 * p1[0]) + (-p0[0] + p2[0]) * t + (2 * p0[0] - 5 * p1[0] + 4 * p2[0] - p3[0]) * t2 + (-p0[0] + 3 * p1[0] - 3 * p2[0] + p3[0]) * t3)
            y = 0.5 * ((2 * p1[1]) + (-p0[1] + p2[1]) * t + (2 * p0[1] - 5 * p1[1] + 4 * p2[1] - p3[1]) * t2 + (-p0[1] + 3 * p1[1] - 3 * p2[1] + p3[1]) * t3)
            out.append((x, y))
    return out


def _chaikin_closed(points, iterations=1, ratio=0.25):
    """One or more Chaikin corner-cutting passes for a closed ring."""
    pts = points[:]
    if len(pts) < 3:
        return pts
    if pts[0] == pts[-1]:
        pts = pts[:-1]
    ratio = max(0.0, min(0.5, float(ratio)))
    for _ in range(max(0, int(iterations))):
        out = []
        n = len(pts)
        for i in range(n):
            p = pts[i]
            q = pts[(i + 1) % n]
            out.append(((1 - ratio) * p[0] + ratio * q[0], (1 - ratio) * p[1] + ratio * q[1]))
            out.append((ratio * p[0] + (1 - ratio) * q[0], ratio * p[1] + (1 - ratio) * q[1]))
        pts = out
    return pts


def smooth_ring(points, mode, tolerance, samples):
    """Optional per-parcel visual smoothing.

    Keep this disabled by default. Per-parcel smoothing does not preserve shared
    boundaries between adjacent cortical parcels, so it can introduce visible
    gaps/overlaps even when each individual parcel looks rounder.
    """
    if mode == "none":
        return points
    if mode == "simplify":
        return _simplify_closed(points, tolerance)
    if mode == "catmull":
        return _catmull_rom_closed(points, samples=samples)
    if mode == "chaikin":
        return _chaikin_closed(points, iterations=1, ratio=0.25)
    if mode == "simplify-catmull":
        return _catmull_rom_closed(_simplify_closed(points, tolerance), samples=samples)
    raise ValueError(f"Unknown smoothing mode: {mode}")


def render(rows: list[dict[str, str]], args: argparse.Namespace) -> plt.Figure:
    features: OrderedDict[str, dict[str, object]] = OrderedDict()
    xs: list[float] = []
    ys: list[float] = []
    required = {"x", "y", ".feature_id", "subgroup", "fill_hex"}
    missing = required - set(rows[0].keys())
    if missing:
        raise SystemExit(f"Plot rows missing columns: {sorted(missing)}")

    for row in rows:
        fid = row[".feature_id"]
        subgroup = row.get("subgroup") or "1"
        if fid not in features:
            features[fid] = {"fill_hex": row.get("fill_hex") or args.na_fill, "rings": OrderedDict()}
        x = float(row["x"])
        y = float(row["y"])
        features[fid]["rings"].setdefault(subgroup, []).append((x, y))  # type: ignore[index,union-attr]
        xs.append(x)
        ys.append(y)

    plt.rcParams.update({
        "font.family": "sans-serif",
        "font.sans-serif": [args.font_family, "Arial", "DejaVu Sans", "Liberation Sans"],
        "svg.fonttype": "none",
        "pdf.fonttype": 42,
    })
    fig, ax = plt.subplots(figsize=parse_figsize(args.figsize), facecolor=args.background)
    ax.set_facecolor(args.background)
    for item in features.values():
        fill = str(item["fill_hex"])
        rings = item["rings"]  # type: ignore[assignment]
        for points in rings.values():
            points = smooth_ring(points, args.smooth_boundaries, args.smooth_tolerance, args.smooth_samples)
            if len(points) < 3:
                continue
            ax.add_patch(Polygon(points, closed=True, facecolor=fill,
                                 edgecolor=args.edgecolor, linewidth=args.linewidth,
                                 joinstyle="round"))
    pad_x = (max(xs) - min(xs)) * args.pad
    pad_y = (max(ys) - min(ys)) * args.pad
    ax.set_xlim(min(xs) - pad_x, max(xs) + pad_x)
    ax.set_ylim(min(ys) - pad_y, max(ys) + pad_y)
    ax.set_aspect("equal")
    ax.axis("off")
    if args.title:
        ax.set_title(args.title, fontsize=args.title_size, color=args.text_color, pad=14)
    return fig


def parse_figsize(text: str) -> tuple[float, float]:
    if "," in text:
        a, b = text.split(",", 1)
    else:
        a, b = text.lower().split("x", 1)
    return float(a), float(b)


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--input", help="CSV/TSV-style cortical ROI table with label/region and value columns")
    p.add_argument("--plot-data", help="Prejoined polygon CSV containing x/y/.feature_id/subgroup/fill_hex")
    p.add_argument("--atlas-csv", default=str(DEFAULT_ATLAS), help="Shared polygon atlas CSV")
    p.add_argument("--output-prefix", required=True, help="Output path prefix without extension")
    p.add_argument("--value-column", default="value")
    p.add_argument("--match-column", default="auto", choices=["auto", "label", "region"])
    p.add_argument("--strict", action="store_true", help="Fail if any input labels/regions are unmatched")
    p.add_argument("--write-plot-data", help="Optional joined polygon CSV with computed fill_hex")
    p.add_argument("--vmin", type=float)
    p.add_argument("--vmax", type=float)
    p.add_argument("--midpoint", type=float, default=0.0)
    p.add_argument("--low", default="#3B4CC0")
    p.add_argument("--mid", default="#DDDDDD")
    p.add_argument("--high", default="#B40426")
    p.add_argument("--na-fill", default="#CCCCCC")
    p.add_argument("--background", default="#FFFFFF")
    p.add_argument("--edgecolor", default="#2E2E2E")
    p.add_argument("--linewidth", type=float, default=0.55)
    p.add_argument("--font-family", default="Arial")
    p.add_argument("--text-color", default="#2E2E2E")
    p.add_argument("--title", default="")
    p.add_argument("--title-size", type=float, default=18)
    p.add_argument("--figsize", default="12,8")
    p.add_argument("--pad", type=float, default=0.04)
    p.add_argument("--smooth-boundaries", default="none", choices=["none", "simplify", "catmull", "simplify-catmull", "chaikin"], help="Experimental per-parcel smoothing. Default none because the recommended Chaikin style is normally applied once to the shared atlas CSV; runtime smoothing is for experiments.")
    p.add_argument("--smooth-tolerance", type=float, default=4.0, help="Coordinate tolerance for boundary simplification before smoothing")
    p.add_argument("--smooth-samples", type=int, default=8, help="Catmull-Rom samples per simplified segment")
    p.add_argument("--formats", default="svg,pdf,png")
    args = p.parse_args()

    rows, stats = build_plot_rows(args)
    if args.write_plot_data:
        write_csv(Path(args.write_plot_data), rows)
        print(f"Wrote plot data: {args.write_plot_data}")
    fig = render(rows, args)
    out_prefix = Path(args.output_prefix)
    out_prefix.parent.mkdir(parents=True, exist_ok=True)
    for fmt in [x.strip().lstrip(".") for x in args.formats.split(",") if x.strip()]:
        out = out_prefix.with_suffix("." + fmt)
        if fmt.lower() == "png":
            fig.savefig(out, dpi=300, bbox_inches="tight", facecolor=args.background)
        else:
            fig.savefig(out, bbox_inches="tight", facecolor=args.background)
        print(f"Wrote {out}")
    print("Stats:", ", ".join(f"{k}={v}" for k, v in stats.items()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

