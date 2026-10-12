"""Collect official Sigenergy product images from their public image server.

sigenergy.com itself blocks automated visits, but its images are served from the
public CDN wwwstatic.sigenergy.com. The Internet Archive keeps a list of image URLs it
has seen there; this script asks for that list, keeps the product folders and
downloads the current files from the CDN into content/product-images-raw/sigenergy/
(not published). Pick and convert by hand. Run via fetch-sigen-images.yml.
"""
import json
import re
import urllib.request
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "content" / "product-images-raw" / "sigenergy"
CDX = ("http://web.archive.org/cdx/search/cdx?url=wwwstatic.sigenergy.com/static/images/"
       "&matchType=prefix&output=json&fl=original&collapse=urlkey&limit=5000")
KEEP = re.compile(r"/static/images/(product-[^/]+|hry|home[^/]*)/[^/?]+\.(png|jpe?g|webp)$", re.I)
UA = "Mozilla/5.0 (compatible; SmartPeakSite/1.0; +https://github.com/smartpeak-be/smartpeak-site)"
MIN_BYTES = 25_000


def get(url):
    request = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(request, timeout=60) as response:
        return response.read()


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    rows = json.loads(get(CDX))[1:]
    urls = sorted({re.sub(r"^http://", "https://", r[0].split("?")[0]) for r in rows if KEEP.search(r[0].split("?")[0])})
    print(f"{len(urls)} candidate image URLs")
    index = []
    for url in urls:
        folder, name = url.split("/static/images/")[1].split("/", 1)
        target = OUT / f"{folder}__{name}"
        try:
            body = get(url)
        except Exception as error:
            print("skip", url, error)
            continue
        if len(body) < MIN_BYTES:
            continue
        target.write_bytes(body)
        index.append({"file": target.name, "url": url, "bytes": len(body)})
    (OUT / "index.json").write_text(json.dumps(index, indent=2) + "\n", encoding="utf-8")
    print(f"saved {len(index)} images")


if __name__ == "__main__":
    main()
