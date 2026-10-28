"""Create responsive WebP variants without changing the original photographs.

Development-only dependency: Pillow. Run from any directory with
python dev/optimize_images.py. No cropping or image content changes are applied.
"""
from pathlib import Path
from PIL import Image, ImageOps

ASSETS = Path(__file__).resolve().parents[1] / "assets"

for name, widths, quality in [
    ("jordan", (480, 960), 86),
    ("marlena", (480, 960), 86),
    ("hank", (480,), 86),
    ("banner_photo", (960, 1920), 82),
]:
    with Image.open(ASSETS / f"{name}.jpg") as source:
        original = ImageOps.exif_transpose(source).convert("RGB")
        for width in widths:
            height = round(original.height * width / original.width)
            image = original.resize((width, height), Image.Resampling.LANCZOS)
            output = ASSETS / f"{'banner' if name == 'banner_photo' else name}-{width}.webp"
            image.save(output, "WEBP", quality=quality, method=6)
            print(f"{output.name}: {width} x {height}, {output.stat().st_size:,} bytes")
