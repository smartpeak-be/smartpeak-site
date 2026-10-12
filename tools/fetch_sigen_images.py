"""Collect product images from the official Sigenergy product pages.

sigenergy.com loads its product photos with JavaScript, so a plain download finds
nothing. This opens each page in a real browser, scrolls through it and keeps every
image of reasonable size it loads. Results go to content/product-images-raw/sigenergy/
(not published); pick and convert by hand. Run via .github/workflows/fetch-sigen-images.yml.
"""
import hashlib
import json
from pathlib import Path

from playwright.sync_api import sync_playwright

PAGES = {
    "sigenstor": "https://www.sigenergy.com/en/products/sigenstor",
    "gateway": "https://www.sigenergy.com/en/products/gateway",
    "ac-charger": "https://www.sigenergy.com/en/products/ac-charger",
    "dc-charger": "https://www.sigenergy.com/en/products/dc-charger",
}
OUT = Path(__file__).resolve().parent.parent / "content" / "product-images-raw" / "sigenergy"
MIN_BYTES = 25_000
EXT = {"image/png": "png", "image/jpeg": "jpg", "image/webp": "webp"}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    index = []
    with sync_playwright() as p:
        browser = p.chromium.launch()
        for name, url in PAGES.items():
            page = browser.new_page(viewport={"width": 1440, "height": 900})
            found = []

            def keep(response, name=name, found=found):
                kind = (response.headers.get("content-type") or "").split(";")[0]
                if kind not in EXT or response.status != 200:
                    return
                try:
                    body = response.body()
                except Exception:
                    return
                if len(body) < MIN_BYTES:
                    return
                digest = hashlib.sha1(body).hexdigest()[:10]
                target = OUT / f"{name}-{digest}.{EXT[kind]}"
                if not target.exists():
                    target.write_bytes(body)
                    found.append({"file": target.name, "url": response.url, "bytes": len(body)})

            page.on("response", keep)
            page.goto(url, wait_until="networkidle", timeout=60000)
            for y in range(0, 20000, 700):
                page.mouse.wheel(0, 700)
                page.wait_for_timeout(250)
            page.wait_for_timeout(1500)
            page.screenshot(path=OUT / f"_{name}-pagina.png", full_page=False)
            index += found
            print(f"{name}: {len(found)} images")
            page.close()
        browser.close()
    (OUT / "index.json").write_text(json.dumps(index, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
