#!/usr/bin/env python3
"""Inspect a cortex polygon atlas CSV and optionally list labels."""
from __future__ import annotations

import argparse
import csv
from pathlib import Path

REQUIRED = ("label", "region", "hemi", "view", "x", "y", ".group", "subgroup", ".feature_id")


def read_csv(path: Path):
    with path.open(newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--atlas-csv", required=True)
    p.add_argument("--list-labels", action="store_true")
    p.add_argument("--limit", type=int, default=30)
    args = p.parse_args()

    path = Path(args.atlas_csv)
    rows = read_csv(path)
    if not rows:
        raise SystemExit("Atlas CSV is empty")
    missing = [c for c in REQUIRED if c not in rows[0]]
    if missing:
        raise SystemExit("Missing columns: " + ", ".join(missing))

    labels = sorted({r["label"] for r in rows if r.get("label")})
    regions = sorted({r["region"] for r in rows if r.get("region")})
    features = sorted({r[".feature_id"] for r in rows if r.get(".feature_id")})
    hemis = sorted({r["hemi"] for r in rows if r.get("hemi")})
    views = sorted({r["view"] for r in rows if r.get("view")})
    sources = sorted({r.get("source_atlas", "") for r in rows if r.get("source_atlas")})

    print(f"Atlas CSV: {path}")
    print(f"Rows: {len(rows)}")
    print(f"Labels: {len(labels)}")
    print(f"Regions: {len(regions)}")
    print(f"Features: {len(features)}")
    print(f"Hemispheres: {', '.join(hemis)}")
    print(f"Views: {', '.join(views)}")
    if sources:
        print(f"Source: {', '.join(sources)}")
    if args.list_labels:
        shown = labels[:args.limit]
        print("Labels:")
        for label in shown:
            print(f"  {label}")
        if len(labels) > args.limit:
            print(f"  ... {len(labels) - args.limit} more")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
