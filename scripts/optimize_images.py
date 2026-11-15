"""Shrink oversized photos in place so the website stays fast.

Runs in GitHub Actions after every change; photos uploaded through Pages CMS arrive
at full camera size. Files keep their names, so content/*.yml stays valid.
"""
import sys
from pathlib import Path

from PIL import Image, ImageOps

MAX_SIDE = 2400
MAX_BYTES = 1_500_000
Image.MAX_IMAGE_PIXELS = 200_000_000

folders = [Path(p) for p in sys.argv[1:]] or [Path(__file__).resolve().parent.parent / "static" / "uploads"]
changed = 0
for folder in folders:
    for path in sorted(folder.rglob("*")):
        if path.suffix.lower() not in {".jpg", ".jpeg", ".png", ".webp"}:
            continue
        with Image.open(path) as img:
            if max(img.size) <= MAX_SIDE and path.stat().st_size <= MAX_BYTES:
                continue
            fmt = img.format
            img = ImageOps.exif_transpose(img)
            img.thumbnail((MAX_SIDE, MAX_SIDE))
            if fmt == "JPEG":
                img.convert("RGB").save(path, "JPEG", quality=84, optimize=True, progressive=True)
            else:
                img.save(path, fmt, optimize=True)
        changed += 1
        print(f"optimized {path} -> {img.size[0]}x{img.size[1]}, {path.stat().st_size // 1024} KB")
print(f"{changed} photo(s) optimized")
