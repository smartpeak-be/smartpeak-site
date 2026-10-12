"""Turn the raw WordPress import (content/wordpress/) into clean site content.

Writes:
  content/artikels/<slug>.html     articles (former blog posts)
  content/pages/<slug>.html        long text pages (terms, privacy, method article)
  assets/img/wp/<file>.webp        images used by that content, resized

Run once after tools/import_wordpress.py. It overwrites the files above, so do not
run it again after hand-editing them. Needs Pillow for the image resize step.
"""
import html
import json
import re
from html.parser import HTMLParser
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "content" / "wordpress"
IMG_OUT = ROOT / "assets" / "img" / "wp"
OLD_HOST = re.compile(r"^https?://(www\.)?smartpeak\.be")

POST_OVERRIDES = {
    "557-2": {
        "slug": "hoe-groot-moet-mijn-thuisbatterij-zijn",
        "title": "Hoe groot moet mijn thuisbatterij zijn? 5, 10 of 20 kWh?",
    },
}
PAGES = ["algemene-voorwaarden", "privacyverklaring"]

KEEP = {"p", "h2", "h3", "h4", "ul", "ol", "li", "strong", "em", "a", "img", "figure",
        "figcaption", "table", "thead", "tbody", "tr", "th", "td", "blockquote", "br", "hr"}
RENAME = {"b": "strong", "i": "em", "h1": "h2", "h5": "h4", "h6": "h4"}
DROP_WITH_CONTENT = {"script", "style", "form", "svg", "noscript", "button", "select", "textarea"}
BLOCK = {"p", "h2", "h3", "h4", "ul", "ol", "li", "figure", "table", "thead", "tbody", "tr",
         "blockquote", "hr"}
VOID = {"img", "br", "hr"}


class Cleaner(HTMLParser):
    def __init__(self, image_for):
        super().__init__(convert_charrefs=True)
        self.image_for = image_for
        self.out = []
        self.dropping = 0
        self.images = set()

    def handle_starttag(self, tag, attrs):
        if self.dropping or tag in DROP_WITH_CONTENT:
            self.dropping += tag in DROP_WITH_CONTENT
            return
        tag = RENAME.get(tag, tag)
        if tag not in KEEP:
            return
        attrs = dict(attrs)
        if tag == "a":
            href = OLD_HOST.sub("", attrs.get("href") or "").strip() or "/"
            self.out.append(f'<a href="{html.escape(href, quote=True)}">')
            return
        if tag == "img":
            local = self.image_for(attrs.get("src") or "")
            if local:
                self.images.add(local)
                alt = html.escape(attrs.get("alt") or "", quote=True)
                self.out.append(f'<img src="/assets/img/wp/{local}" alt="{alt}" loading="lazy">')
            return
        self.out.append(("\n" if tag in BLOCK else "") + f"<{tag}>")

    def handle_endtag(self, tag):
        if tag in DROP_WITH_CONTENT:
            self.dropping = max(0, self.dropping - 1)
            return
        if self.dropping:
            return
        tag = RENAME.get(tag, tag)
        if tag in KEEP and tag not in VOID:
            self.out.append(f"</{tag}>")

    def handle_data(self, data):
        if not self.dropping:
            self.out.append(html.escape(re.sub(r"\s+", " ", data), quote=False))

    def result(self):
        text = "".join(self.out)
        text = re.sub(r"<(p|li|h[234]|strong|em)>\s*</\1>", "", text)
        text = re.sub(r"<p>\s*(<br>\s*)*", "<p>", text)
        text = re.sub(r"(\s*<br>)+\s*</p>", "</p>", text)
        text = re.sub(r">\s+<", lambda m: ">\n<" if "\n" in m.group(0) else "> <", text)
        text = re.sub(r"\n{2,}", "\n", text)
        return text.strip() + "\n"


def stem(url):
    name = url.rsplit("/", 1)[-1]
    name = re.sub(r"-\d+x\d+(?=\.\w+$)", "", name)
    name = re.sub(r"-e\d{9,}(?=\.\w+$)", "", name)
    return name.rsplit(".", 1)[0].lower()


def build_image_index():
    media = json.loads((RAW / "media.json").read_text(encoding="utf-8"))
    by_id = {m["id"]: m for m in media}
    by_stem = {stem(m["original_url"]): m for m in media}
    return by_id, by_stem


def export_image(media_item):
    source = RAW / "media" / media_item["file"]
    target_name = re.sub(r"-\d+x\d+$", "", source.stem) + ".webp"
    target = IMG_OUT / target_name
    if not target.exists():
        IMG_OUT.mkdir(parents=True, exist_ok=True)
        with Image.open(source) as image:
            image = image.convert("RGBA" if image.mode in ("RGBA", "LA", "P") else "RGB")
            image.thumbnail((1600, 1600))
            image.save(target, "WEBP", quality=80, method=6)
    return target_name


def plain(fragment, limit=None):
    text = html.unescape(re.sub(r"<[^>]+>", " ", fragment))
    text = re.sub(r"\s+", " ", text).replace("[…]", "").replace("[&hellip;]", "").strip()
    if limit and len(text) > limit:
        text = text[:limit].rsplit(" ", 1)[0] + "…"
    return text


def write(path, meta, body):
    path.parent.mkdir(parents=True, exist_ok=True)
    header = "<!--meta\n" + json.dumps(meta, ensure_ascii=False, indent=2) + "\n-->\n"
    path.write_text(header + body, encoding="utf-8")


def convert(item, image_for):
    cleaner = Cleaner(image_for)
    cleaner.feed(item["content"])
    return cleaner.result()


def main():
    by_id, by_stem = build_image_index()

    def image_for(url):
        item = by_stem.get(stem(url))
        return export_image(item) if item else None

    for raw in sorted((RAW / "posts").glob("*.json")):
        item = json.loads(raw.read_text(encoding="utf-8"))
        override = POST_OVERRIDES.get(item["slug"], {})
        slug = override.get("slug", item["slug"])
        featured = by_id.get(item["featured_media"])
        meta = {
            "title": override.get("title") or html.unescape(item["title"]),
            "description": item["description"] or plain(item["excerpt"] or item["content"], 155),
            "date": item["date"][:10],
            "modified": (item["modified"] or item["date"])[:10],
            "image": f"/assets/img/wp/{export_image(featured)}" if featured else None,
            "legacy_path": f"/{item['slug']}/",
        }
        write(ROOT / "content" / "artikels" / f"{slug}.html", meta, convert(item, image_for))

    for slug in PAGES:
        item = json.loads((RAW / "pages" / f"{slug}.json").read_text(encoding="utf-8"))
        meta = {
            "title": html.unescape(item["title"]),
            "description": item["description"] or plain(item["content"], 155),
            "modified": (item["modified"] or item["date"])[:10],
        }
        write(ROOT / "content" / "pages" / f"{slug}.html", meta, convert(item, image_for))
    print("Converted posts and pages; images in", IMG_OUT)


if __name__ == "__main__":
    main()
