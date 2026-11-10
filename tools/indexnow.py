"""Tell Bing and the other IndexNow search engines which pages changed in this deploy.

Compares the freshly built _site/sitemap.xml with the sitemap that was live before the deploy
and sends the new and changed URLs (a different <lastmod>). Without an old sitemap it sends all.
Google does not use IndexNow; it reads the sitemap from Search Console.

    python3 tools/indexnow.py <old-sitemap.xml>
"""
import json
import re
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = json.loads((ROOT / "site.json").read_text(encoding="utf-8"))


def entries(xml):
    return dict(re.findall(r"<loc>([^<]+)</loc>(?:<lastmod>([^<]+)</lastmod>)?", xml))


def main():
    key = SITE.get("indexnow_key")
    new = entries((ROOT / "_site" / "sitemap.xml").read_text(encoding="utf-8"))
    old_file = Path(sys.argv[1]) if len(sys.argv) > 1 else None
    old = entries(old_file.read_text(encoding="utf-8")) if old_file and old_file.exists() else {}
    changed = [url for url, day in new.items() if old.get(url, "-") != day]
    if not key or not changed or not all(url.startswith(SITE["domain"] + "/") for url in changed):
        print(f"IndexNow: nothing to send ({len(changed)} changed)")
        return
    body = json.dumps({"host": SITE["domain"].split("://")[1], "key": key,
                       "keyLocation": f'{SITE["domain"]}/{key}.txt', "urlList": changed}).encode()
    request = urllib.request.Request("https://api.indexnow.org/indexnow", data=body,
                                     headers={"Content-Type": "application/json; charset=utf-8"})
    with urllib.request.urlopen(request, timeout=20) as response:
        print(f"IndexNow: {len(changed)} URL(s) sent, status {response.status}")
    for url in changed:
        print(" ", url)


if __name__ == "__main__":
    main()
