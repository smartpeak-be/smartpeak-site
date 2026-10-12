"""Render the SVG charts in assets/img/grafieken/ to WebP with the site font (Playwright + Chromium).

Usage: python3 tools/render_svg.py [name ...]   (no names: all SVGs)
Then run tools/make_image_variants.py for the phone-size versions and sizes.
"""
import io
import sys
from pathlib import Path

from PIL import Image
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
CHARTS = ROOT / "assets" / "img" / "grafieken"
FONT = (ROOT / "assets" / "fonts" / "instrument-sans.woff2").as_uri()


def main(names):
    svgs = [CHARTS / f"{n}.svg" for n in names] if names else sorted(CHARTS.glob("*.svg"))
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1600, "height": 900})
        for path in svgs:
            html = (f'<html><head><style>@font-face{{font-family:"Instrument Sans";src:url("{FONT}") format("woff2");'
                    f'font-weight:400 700;font-stretch:75% 100%}}body{{margin:0}}</style></head>'
                    f'<body>{path.read_text(encoding="utf-8")}</body></html>')
            page.set_content(html)
            page.evaluate("document.fonts.ready")
            png = page.locator("svg").screenshot()
            Image.open(io.BytesIO(png)).convert("RGB").save(path.with_suffix(".webp"), "WEBP", quality=88, method=6)
            print("rendered", path.with_suffix(".webp").name)
        browser.close()


if __name__ == "__main__":
    main(sys.argv[1:])
