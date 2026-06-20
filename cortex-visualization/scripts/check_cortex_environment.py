#!/usr/bin/env python3
"""Check Python/R dependencies for the cortex-visualization skill."""
from __future__ import annotations

import argparse
import importlib.util
import shutil
import subprocess


def check_python() -> bool:
    required = ["matplotlib"]
    ok = True
    print("Python dependencies:")
    for mod in required:
        found = importlib.util.find_spec(mod) is not None
        print(f"  {'OK' if found else 'MISSING'} {mod}")
        ok = ok and found
    if not ok:
        print("Install with: python -m pip install matplotlib")
    return ok


def check_r() -> bool:
    exe = shutil.which("Rscript")
    print("R dependencies:")
    if not exe:
        print("  MISSING Rscript on PATH")
        print("  Install R and/or add Rscript.exe to PATH")
        return False
    code = """
pkgs <- c('ggplot2','svglite','ggseg','ggseg.formats')
for (p in pkgs) {
  ok <- requireNamespace(p, quietly=TRUE)
  cat(if (ok) 'OK ' else 'MISSING ', p, '\n', sep='')
}
quit(status=if (all(vapply(pkgs, requireNamespace, logical(1), quietly=TRUE))) 0 else 1)
"""
    proc = subprocess.run([exe, "-e", code], text=True, capture_output=True)
    print(proc.stdout.strip())
    if proc.returncode != 0:
        print("Install in R with: install.packages(c('ggplot2','svglite')); install ggseg/ggseg.formats from CRAN/r-universe or local source")
    return proc.returncode == 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--backend", choices=["python", "r", "both"], default="both")
    args = p.parse_args()
    ok = True
    if args.backend in ("python", "both"):
        ok = check_python() and ok
    if args.backend in ("r", "both"):
        ok = check_r() and ok
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
