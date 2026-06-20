from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps

sub_path = Path(r"E:\learn_pytorch\pythonProject\subcortex-visualization-skill-project\assets\gallery\all_atlas_showcase.png")
cortex_path = Path(r"E:\learn_pytorch\pythonProject\cortex-visualization-skill-project\demo\cortex_dk_demo_python.png")
out = Path(r"E:\learn_pytorch\pythonProject\cortex-visualization-skill-project\demo\STYLE_AUDIT_cortex_vs_subcortex.png")
sub = Image.open(sub_path).convert("RGB")
cortex = Image.open(cortex_path).convert("RGB")
# crop three representative subcortex tiles from existing showcase
# source image is 2130x1791 with 3x4 cards
crops = [
    (40, 135, 700, 515),     # subcortex overview
    (1430, 950, 2090, 1335), # thalamus HCP-ish area
    (1430, 1370, 2090, 1760) # SUIT cerebellum
]
sub_tiles = [ImageOps.expand(sub.crop(box), border=8, fill="white") for box in crops]
# Prepare canvas
W, H = 1900, 1100
canvas = Image.new("RGB", (W, H), "white")
d = ImageDraw.Draw(canvas)
try:
    title_font = ImageFont.truetype("arial.ttf", 42)
    label_font = ImageFont.truetype("arial.ttf", 28)
    small_font = ImageFont.truetype("arial.ttf", 21)
except Exception:
    title_font = label_font = small_font = ImageFont.load_default()

d.text((50, 28), "Style audit: cortex skill vs existing subcortex skill", fill="#1F1F1F", font=title_font)
d.text((50, 82), "Check: flat 2D polygons | white background | matte fills | dark parcel outlines | no mesh/lighting", fill="#555555", font=small_font)

# left cortex panel
c = cortex.copy()
c.thumbnail((1120, 880), Image.LANCZOS)
canvas.paste(c, (40, 160))
d.text((60, 130), "Cortex demo (new skill)", fill="#2E2E2E", font=label_font)
# right subcortex panels stacked
x0, y0 = 1230, 160
d.text((x0, 130), "Existing subcortex style references", fill="#2E2E2E", font=label_font)
y = y0
for tile in sub_tiles:
    tile.thumbnail((610, 270), Image.LANCZOS)
    canvas.paste(tile, (x0, y))
    y += 295

# checklist
check_x, check_y = 50, 1010
d.text((check_x, check_y), "Decision: preserve raw ggseg shared boundaries by default; use SVG/PDF or high-DPI PNG for anti-aliased edges, not per-parcel smoothing.", fill="#333333", font=small_font)
out.parent.mkdir(parents=True, exist_ok=True)
canvas.save(out, quality=95)
print(out)
