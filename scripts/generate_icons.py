"""Rasterize the project's original M/down-arrow mark for native app icons (Pillow)."""

from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
output = ROOT / "desktop/icons"
output.mkdir(exist_ok=True)
size = 2048
image = Image.new("RGBA", (size, size))
draw = ImageDraw.Draw(image)
draw.rounded_rectangle((180, 180, 1868, 1868), radius=370, fill="#e76542")
scale = 29
left, top = 445, 560
for points in (
    ((3, 25), (3, 7), (11, 17), (19, 7), (19, 25)),
    ((30, 7), (30, 25)),
    ((24, 19), (30, 25), (36, 19)),
):
    draw.line(
        [(left + x * scale, top + y * scale) for x, y in points],
        fill="#ffffff",
        width=round(3.5 * scale),
        joint="curve",
    )
image = image.resize((1024, 1024), Image.Resampling.LANCZOS)
image.save(output / "icon.png")
image.save(output / "icon.icns")
image.save(
    output / "icon.ico", sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
)
