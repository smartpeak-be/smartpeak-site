"""Download posts, pages and images from the current WordPress site of smartpeak.be.

Runs in GitHub Actions (see .github/workflows/import-wordpress.yml) because the
WordPress host is reachable from there. Output lands in content/wordpress/ and is
used as the source for the static pages and blog posts. Python stdlib only.
"""
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

SOURCE = "https://smartpeak.be"
OUT = Path(__file__).resolve().parent.parent / "content" / "wordpress"
USER_AGENT = "Mozilla/5.0 (compatible; SmartPeakSiteImport/1.0; +https://github.com/smartpeak-be/smartpeak-site)"
PREFERRED_SIZES = ("1536x1536", "large", "full")


def get(url):
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            return response.read(), response.headers
    except urllib.error.HTTPError as error:
        print(f"HTTP {error.code} for {url}: {error.read()[:300]!r}", file=sys.stderr)
        raise


def get_collection(endpoint, fields):
    items, page, total_pages = [], 1, 1
    while page <= total_pages:
        query = urllib.parse.urlencode({"per_page": 100, "page": page, "_fields": fields})
        body, headers = get(f"{SOURCE}/wp-json/wp/v2/{endpoint}?{query}")
        items.extend(json.loads(body))
        total_pages = int(headers.get("X-WP-TotalPages", "1"))
        page += 1
    return items


def save_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def simplify(item):
    return {
        "id": item["id"],
        "slug": item["slug"],
        "link": item.get("link"),
        "date": item.get("date"),
        "modified": item.get("modified"),
        "title": item["title"]["rendered"],
        "excerpt": (item.get("excerpt") or {}).get("rendered", ""),
        "content": item["content"]["rendered"],
        "featured_media": item.get("featured_media") or None,
        "description": ((item.get("yoast_head_json") or {}).get("description") or ""),
    }


def best_image_url(media):
    sizes = (media.get("media_details") or {}).get("sizes") or {}
    for name in PREFERRED_SIZES:
        if name in sizes:
            return sizes[name]["source_url"]
    return media["source_url"]


def safe_name(url):
    name = urllib.parse.unquote(url.rsplit("/", 1)[-1])
    return re.sub(r"[^A-Za-z0-9._-]+", "-", name)


def main():
    fields = "id,slug,link,date,modified,title,excerpt,content,featured_media,yoast_head_json"
    posts = [simplify(p) for p in get_collection("posts", fields)]
    pages = [simplify(p) for p in get_collection("pages", fields)]
    for post in posts:
        save_json(OUT / "posts" / f"{post['slug']}.json", post)
    for page in pages:
        save_json(OUT / "pages" / f"{page['slug']}.json", page)

    media_index = []
    for media in get_collection("media", "id,slug,source_url,alt_text,title,media_type,mime_type,media_details,date"):
        if media.get("media_type") != "image":
            continue
        url = best_image_url(media)
        target = OUT / "media" / safe_name(url)
        if not target.exists():
            try:
                body, _ = get(url)
            except Exception as error:  # keep importing the rest
                print(f"skip {url}: {error}", file=sys.stderr)
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(body)
            time.sleep(0.2)
        media_index.append({
            "id": media["id"],
            "file": target.name,
            "original_url": media["source_url"],
            "alt": media.get("alt_text") or "",
            "title": (media.get("title") or {}).get("rendered", ""),
            "date": media.get("date"),
        })
    save_json(OUT / "media.json", sorted(media_index, key=lambda m: m["id"]))
    print(f"Imported {len(posts)} posts, {len(pages)} pages, {len(media_index)} images into {OUT}")


if __name__ == "__main__":
    main()
