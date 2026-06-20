#!/usr/bin/env python3
"""Build a compact cortex visualization showcase image for the repository README."""
from __future__ import annotations

import argparse
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps


def _font(size: int):
    for name in ("arial.ttf", "DejaVuSans.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except Exception:
            pass
    return ImageFont.load_default()


def fit_box(img: Image.Image, size: tuple[int, int], bg: str = "white") -> Image.Image:
    img = img.convert("RGB")
    canvas = Image.new("RGB", size, bg)
    tmp = img.copy()
    tmp.thumbnail((size[0] - 30, size[1] - 55), Image.LANCZOS)
    x = (size[0] - tmp.width) // 2
    y = 45 + (size[1] - 55 - tmp.height) // 2
    canvas.paste(tmp, (x, y))
    return canvas


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--project-root", default=str(Path(__file__).resolve().parents[2]))
    p.add_argument("--output", default="assets/gallery/cortex_showcase.png")
    args = p.parse_args()

    root = Path(args.project_root)
    out = root / args.output
    demo = root / "demo"
    py_img = Image.open(demo / "cortex_dk_demo_python.png")
    r_img = Image.open(demo / "cortex_dk_demo_r.png")
    audit_img = Image.open(demo / "STYLE_AUDIT_cortex_vs_subcortex.png")

    W, H = 2200, 1320
    canvas = Image.new("RGB", (W, H), "white")
    draw = ImageDraw.Draw(canvas)
    title = _font(54)
    subtitle = _font(27)
    label = _font(31)
    small = _font(23)

    draw.text((60, 38), "Cortex visualization skill", fill="#1F1F1F", font=title)
    draw.text((62, 105), "Strict Python/R ggseg-style parity: shared Chaikin-smoothed geometry + shared fill_hex colors", fill="#555555", font=subtitle)

    panel_w, panel_h = 1010, 520
    py_panel = fit_box(py_img, (panel_w, panel_h))
    r_panel = fit_box(r_img, (panel_w, panel_h))
    for panel, x, text in [(py_panel, 60, "Python renderer"), (r_panel, 1130, "R renderer")]:
        draw.rounded_rectangle((x, 165, x + panel_w, 165 + panel_h), radius=24, outline="#DDDDDD", width=2, fill="white")
        canvas.paste(panel, (x, 165))
        draw.text((x + 30, 185), text, fill="#2E2E2E", font=label)

    # Bottom style audit, cropped to avoid duplicating huge title whitespace.
    audit = audit_img.convert("RGB")
    audit_crop = audit.crop((0, 110, audit.width, audit.height - 20))
    audit_crop.thumbnail((2070, 520), Image.LANCZOS)
    bx, by = 60, 735
    draw.rounded_rectangle((bx, by, bx + 2080, by + 525), radius=24, outline="#DDDDDD", width=2, fill="white")
    canvas.paste(audit_crop, (bx + (2080 - audit_crop.width)//2, by + 15))
    draw.text((bx + 30, by + 25), "Style audit vs existing subcortex skill", fill="#2E2E2E", font=label)

    draw.text((62, 1272), "Default: dk_polygons_chaikin.csv | SVG/PDF primary | PNG preview | raw ggseg geometry retained for provenance", fill="#444444", font=small)

    out.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(out, quality=95)
    print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
