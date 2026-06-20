#!/usr/bin/env python3
"""Validate a cortical ROI table against a shared polygon atlas CSV."""
from __future__ import annotations

import argparse
import csv
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEFAULT_ATLAS = HERE.parent / "assets" / "atlases" / "dk_polygons_chaikin.csv"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--input", required=True)
    p.add_argument("--atlas-csv", default=str(DEFAULT_ATLAS))
    p.add_argument("--value-column", default="value")
    p.add_argument("--match-column", default="auto", choices=["auto", "label", "region"])
    p.add_argument("--strict", action="store_true")
    args = p.parse_args()

    atlas = read_csv(Path(args.atlas_csv))
    table = read_csv(Path(args.input))
    if not atlas or not table:
        raise SystemExit("Atlas or input table is empty")
    if args.value_column not in table[0]:
        raise SystemExit(f"Missing value column: {args.value_column}")
    if args.match_column == "auto":
        match_col = "label" if "label" in table[0] else "region"
    else:
        match_col = args.match_column
    if match_col not in table[0]:
        raise SystemExit(f"Input table missing match column: {match_col}")
    if match_col not in atlas[0]:
        raise SystemExit(f"Atlas CSV missing match column: {match_col}")

    atlas_keys = {row[match_col] for row in atlas if row.get(match_col)}
    table_keys = {row[match_col] for row in table if row.get(match_col)}
    matched = sorted(table_keys & atlas_keys)
    unmatched = sorted(table_keys - atlas_keys)
    missing_values = [row.get(match_col, "") for row in table if row.get(args.value_column, "") == ""]
    print(f"Atlas rows: {len(atlas)}")
    print(f"Atlas unique {match_col}: {len(atlas_keys)}")
    print(f"Input rows: {len(table)}")
    print(f"Input unique {match_col}: {len(table_keys)}")
    print(f"Matched {match_col}: {len(matched)}")
    print(f"Unmatched {match_col}: {len(unmatched)}")
    if unmatched:
        print("First unmatched:", ", ".join(unmatched[:20]))
    if missing_values:
        print(f"Rows with empty {args.value_column}: {len(missing_values)}")
    if args.strict and (unmatched or missing_values):
        raise SystemExit("Strict validation failed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
