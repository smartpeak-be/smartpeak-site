"""Prepare images for the build (run locally after adding or changing an image; needs Pillow).

- assets/img/**/<name>.webp|jpg|png wider than 700 px get a smaller <name>-w640.webp,
  which build.py offers through srcset so phones download less.
- Article images (and pages with a "slug" and "image" in their meta) get a 1200x630 JPEG in assets/img/og/ for link previews
  (LinkedIn and some others do not show WebP).
- The header logo gets a small WebP version.
- content/image-sizes.json records width and height of every image, so build.py can
  always write width/height (no layout shift) and knows which variants exist.
"""
import json
import re
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
IMG = ROOT / "assets" / "img"
SKIP = {"favicon.png", "og-smartpeak.jpg"}
VARIANT_WIDTH = 640


def article_images():
    """Articles, and pages with a "slug" and an "image" in their meta (such as a customer case)."""
    for path in list((ROOT / "content" / "artikels").glob("*.html")) + list((ROOT / "pages").rglob("*.html")):
        meta = json.loads(re.match(r"<!--meta\s*(\{.*?\})\s*-->", path.read_text(encoding="utf-8"), re.S).group(1))
        is_article = path.parent.name == "artikels"
        if meta.get("image") and (is_article or meta.get("slug")):
            yield (path.stem if is_article else meta["slug"]), ROOT / meta["image"].lstrip("/")


def main():
    sizes = {}
    for path in sorted(IMG.rglob("*")):
        if path.suffix.lower() not in {".webp", ".jpg", ".jpeg", ".png"} or path.name in SKIP:
            continue
        if path.stem.endswith(f"-w{VARIANT_WIDTH}") or path.parent.name in ("og", "social"):
            continue
        with Image.open(path) as im:
            width, height = im.size
            entry = {"width": width, "height": height}
            if width > 700:
                variant = path.with_name(f"{path.stem}-w{VARIANT_WIDTH}.webp")
                small = im.convert("RGBA" if im.mode in ("RGBA", "LA", "P") else "RGB")
                small = small.resize((VARIANT_WIDTH, round(height * VARIANT_WIDTH / width)), Image.LANCZOS)
                small.save(variant, "WEBP", quality=80, method=6)
                entry["variant"] = "/" + variant.relative_to(ROOT).as_posix()
            sizes["/" + path.relative_to(ROOT).as_posix()] = entry

    og_dir = IMG / "og"
    og_dir.mkdir(exist_ok=True)
    for slug, source in article_images():
        with Image.open(source) as im:
            im = im.convert("RGB")
            ratio = 1200 / 630
            w, h = im.size
            if w / h > ratio:
                nw = round(h * ratio)
                im = im.crop(((w - nw) // 2, 0, (w - nw) // 2 + nw, h))
            else:
                nh = round(w / ratio)
                im = im.crop((0, (h - nh) // 2, w, (h - nh) // 2 + nh))
            im.resize((1200, 630), Image.LANCZOS).save(og_dir / f"{slug}.jpg", "JPEG", quality=82, optimize=True, progressive=True)

    with Image.open(IMG / "site" / "logo-mark.png") as logo:
        logo.convert("RGBA").resize((88, round(logo.height * 88 / logo.width)), Image.LANCZOS) \
            .save(IMG / "site" / "logo-mark.webp", "WEBP", quality=90, method=6)

    (ROOT / "content" / "image-sizes.json").write_text(json.dumps(sizes, indent=1) + "\n", encoding="utf-8")
    print(f"{len(sizes)} images, {sum('variant' in e for e in sizes.values())} variants")


if __name__ == "__main__":
    main()
