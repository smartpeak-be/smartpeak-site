"""Build the static SmartPeak website into _site/ (Python 3.10+, stdlib only).

Sources:
  site.json              contact details, navigation, redirects
  templates/layout.html  shared page shell (header, footer)
  pages/*.html           hand-written pages, with a meta block (title, path, ...)
  content/pages/*.html   long text pages imported from WordPress, served at /<slug>/
  content/artikels/*.html  articles, served at /artikels/<slug>/
  content/realisaties.json
"""
import html
import json
import os
import re
import shutil
from datetime import date
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).parent
OUT = ROOT / "_site"
SITE = json.loads((ROOT / "site.json").read_text(encoding="utf-8"))
SITE_URL = os.environ.get("SITE_URL", "http://localhost:8000").rstrip("/")
BASE_PATH = urlparse(SITE_URL).path.rstrip("/")
IS_LIVE_DOMAIN = SITE_URL in (SITE["domain"], SITE["domain"].replace("://", "://www."))
MONTHS = ["januari", "februari", "maart", "april", "mei", "juni", "juli", "augustus",
          "september", "oktober", "november", "december"]


def esc(value):
    return html.escape(str(value or ""), quote=True)


def read_entry(path):
    text = path.read_text(encoding="utf-8")
    match = re.match(r"<!--meta\s*(\{.*?\})\s*-->\s*", text, re.S)
    if not match:
        raise ValueError(f"{path} has no <!--meta {{...}} --> block")
    return json.loads(match.group(1)), text[match.end():]


def dutch_date(iso):
    day = date.fromisoformat(iso)
    return f"{day.day} {MONTHS[day.month - 1]} {day.year}"


def load_posts():
    posts = []
    for path in (ROOT / "content" / "artikels").glob("*.html"):
        meta, body = read_entry(path)
        meta.update(slug=path.stem, path=f"/artikels/{path.stem}/", body=body)
        posts.append(meta)
    return sorted(posts, key=lambda p: p["date"], reverse=True)


def post_cards(posts):
    cards = []
    for post in posts:
        image = (f'<img src="{esc(post["image"])}" alt="" loading="lazy" width="480" height="300">'
                 if post.get("image") else "")
        cards.append(f'''<li class="post-card">
  <a href="{post["path"]}">{image}<span class="post-card-text">
    <time datetime="{post["date"]}">{dutch_date(post["date"])}</time>
    <strong>{esc(post["title"])}</strong>
    <span>{esc(post["description"])}</span>
  </span></a>
</li>''')
    return '<ul class="post-cards">' + "\n".join(cards) + "</ul>"


def realisatie_cards(items):
    cards = []
    for item in items:
        facts = "".join(f"<li>{esc(fact)}</li>" for fact in item.get("facts", []))
        cards.append(f'''<figure class="realisatie">
  <img src="{esc(item["image"])}" alt="{esc(item["alt"])}" loading="lazy">
  <figcaption>
    <strong>{esc(item["title"])}</strong>
    <span>{esc(item["text"])}</span>
    {f'<ul class="facts">{facts}</ul>' if facts else ""}
  </figcaption>
</figure>''')
    return '<div class="realisaties">' + "\n".join(cards) + "</div>"


def reviews_block(limit):
    return (f'<div id="smartpeak-reviews" class="reviews-mount"></div>\n'
            f'<script defer src="{esc(SITE["reviews_widget_url"])}" data-limit="{limit}"></script>')


def section_cards(entries):
    cards = []
    for meta in sorted(entries, key=lambda m: (m.get("order", 99), m["title"])):
        cards.append(f'''<li class="link-card">
  <a href="{meta["path"]}"><strong>{esc(meta.get("card_title") or meta["title"])}</strong>
  <span>{esc(meta.get("summary") or meta.get("description"))}</span></a>
</li>''')
    return '<ul class="link-cards">' + "\n".join(cards) + "</ul>"


def tokens(posts, realisaties, sections):
    section_tokens = {f"list_{name}": section_cards(entries) for name, entries in sections.items()}
    return section_tokens | {
        "analysis_url": esc(SITE["analysis_url"]),
        "email": esc(SITE["email"]),
        "phone": esc(SITE["phone"]),
        "phone_href": esc(SITE["phone_href"]),
        "hours": esc(SITE["hours"]),
        "latest_posts": post_cards(posts[:3]),
        "article_list": post_cards(posts),
        "realisaties": realisatie_cards(realisaties),
        "realisaties_preview": realisatie_cards(realisaties[:3]),
        "reviews": reviews_block(9),
        "reviews_short": reviews_block(6),
        "cta": (ROOT / "templates" / "post-cta.html").read_text(encoding="utf-8"),
    }


def fill(body, values):
    def replace(match):
        if match.group(1).startswith("list_") and match.group(1) not in values:
            return section_cards([])
        if match.group(1) not in values:
            raise KeyError(f"Unknown token {{{{{match.group(1)}}}}}")
        return values[match.group(1)]
    return re.sub(r"\{\{\s*(\w+)\s*\}\}", replace, body)


def nav_links(items, current):
    links = []
    for item in items:
        active = ' aria-current="page"' if item["path"] == current else ""
        links.append(f'<a href="{item["path"]}"{active}>{esc(item["label"])}</a>')
    return "\n".join(links)


def breadcrumbs(meta, titles):
    parts = [p for p in meta["path"].strip("/").split("/") if p]
    trail, path = [("Home", "/")], "/"
    if meta.get("date"):
        trail.append(("Artikels", "/artikels/"))
    for part in parts:
        path += part + "/"
        trail.append((titles.get(path, meta["title"]), path))
    return trail if len(trail) > 2 or meta.get("date") else None


def structured_data(meta, titles):
    organization = {
        "@context": "https://schema.org", "@type": "LocalBusiness", "name": SITE["name"],
        "url": SITE_URL + "/", "email": SITE["email"], "telephone": SITE["phone_href"],
        "logo": SITE_URL + "/assets/img/site/logo-mark.png", "areaServed": "Vlaanderen",
        "sameAs": [s["url"] for s in SITE["social"]],
    }
    data = [organization]
    if meta.get("date"):
        data.append({
            "@context": "https://schema.org", "@type": "BlogPosting", "headline": meta["title"],
            "datePublished": meta["date"], "dateModified": meta.get("modified") or meta["date"],
            "publisher": {"@type": "Organization", "name": SITE["name"]},
            "mainEntityOfPage": SITE_URL + meta["path"],
        })
    trail = breadcrumbs(meta, titles)
    if trail:
        data.append({
            "@context": "https://schema.org", "@type": "BreadcrumbList",
            "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": name,
                                 "item": SITE_URL + path} for i, (name, path) in enumerate(trail)],
        })
    return json.dumps(data, ensure_ascii=False).replace("</", "<\\/")


def render(meta, body, titles):
    layout = (ROOT / "templates" / "layout.html").read_text(encoding="utf-8")
    title = meta["title"] if meta["path"] == "/" else f'{meta["title"]} | {SITE["name"]}'
    image = meta.get("image") or "/assets/img/site/og-smartpeak.jpg"
    page = fill(layout, {
        "title": esc(title),
        "description": esc(meta.get("description")),
        "canonical": esc(SITE_URL + meta["path"]),
        "og_image": esc(SITE_URL + image),
        "og_type": "article" if meta.get("date") else "website",
        "robots": "index, follow" if IS_LIVE_DOMAIN else "noindex, nofollow",
        "structured_data": structured_data(meta, titles),
        "nav": nav_links(SITE["nav"], meta["path"]),
        "footer_nav": nav_links(SITE["nav"] + SITE["footer_nav"], meta["path"]),
        "social": nav_links([{"label": s["label"], "path": s["url"]} for s in SITE["social"]], ""),
        "entities": " en ".join(f'{esc(e["name"])} ({esc(e["number"])})' for e in SITE["entities"]),
        "email": esc(SITE["email"]),
        "phone": esc(SITE["phone"]),
        "phone_href": esc(SITE["phone_href"]),
        "year": str(date.today().year),
        "body_class": esc(meta.get("body_class", "")),
        "content": body,
    })
    return with_base_path(page)


def with_base_path(page):
    """Prefix root-relative links so the site also works under /<repo>/ on github.io."""
    if not BASE_PATH:
        return page
    return re.sub(r'((?:href|src|action)=")/(?!/)', rf"\1{BASE_PATH}/", page)


def article(meta, body, kicker=""):
    image = (f'<img class="article-image" src="{esc(meta["image"])}" alt="" width="1200" height="700">'
             if meta.get("image") else "")
    return f'''<article class="article">
  <header class="article-head wrap-narrow">
    {kicker}
    <h1>{esc(meta["title"])}</h1>
  </header>
  {f'<div class="wrap-narrow">{image}</div>' if image else ""}
  <div class="prose wrap-narrow">
{body}
  </div>
</article>'''


def post_page(post, cta):
    kicker = (f'<p class="article-meta"><a href="/artikels/">Artikels</a> <span aria-hidden="true">/</span> '
              f'<time datetime="{post["date"]}">{dutch_date(post["date"])}</time></p>')
    return article(post, post["body"], kicker) + cta


def redirect_page(target):
    url = esc(BASE_PATH + target)
    return (f'<!doctype html><html lang="nl"><head><meta charset="utf-8">'
            f'<title>Doorverwijzing | {SITE["name"]}</title><meta name="robots" content="noindex">'
            f'<link rel="canonical" href="{esc(SITE_URL + target)}">'
            f'<meta http-equiv="refresh" content="0; url={url}"></head>'
            f'<body><p>Deze pagina is verhuisd naar <a href="{url}">{url}</a>.</p></body></html>')


def write_page(path, document):
    target = OUT / path.strip("/") / "index.html" if path != "/" else OUT / "index.html"
    if target.exists():
        raise ValueError(f"Two pages want {path}")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(document, encoding="utf-8")


def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()
    shutil.copytree(ROOT / "assets", OUT / "assets")

    posts = load_posts()
    realisaties = json.loads((ROOT / "content" / "realisaties.json").read_text(encoding="utf-8"))
    pages = [read_entry(source) for source in sorted((ROOT / "pages").rglob("*.html"))]
    long_pages = []
    for source in sorted((ROOT / "content" / "pages").glob("*.html")):
        meta, body = read_entry(source)
        meta["path"] = f"/{source.stem}/"
        long_pages.append((meta, body))

    sections = {}
    for meta, _ in pages + long_pages:
        if meta.get("section"):
            sections.setdefault(meta["section"], []).append(meta)
    titles = {meta["path"]: meta.get("card_title") or meta["title"] for meta, _ in pages + long_pages}
    values = tokens(posts, realisaties, sections)
    cta = fill((ROOT / "templates" / "post-cta.html").read_text(encoding="utf-8"), values)
    paths = []

    for meta, body in pages:
        document = render(meta, fill(body, values), titles)
        if meta["path"] == "/404/":
            (OUT / "404.html").write_text(document, encoding="utf-8")
            continue
        write_page(meta["path"], document)
        paths.append(meta["path"])

    for meta, body in long_pages:
        with_cta = meta.get("cta", True)
        write_page(meta["path"], render(meta, article(meta, body) + (cta if with_cta else ""), titles))
        paths.append(meta["path"])

    for post in posts:
        write_page(post["path"], render(post, post_page(post, cta), titles))
        paths.append(post["path"])

    redirects = dict(SITE["redirects"])
    redirects.update({p["legacy_path"]: p["path"] for p in posts if p.get("legacy_path")})
    for old, new in redirects.items():
        write_page(old, redirect_page(new))

    (OUT / ".nojekyll").touch()
    robots = f"User-agent: *\nAllow: /\nSitemap: {SITE_URL}/sitemap.xml\n" if IS_LIVE_DOMAIN \
        else "User-agent: *\nDisallow: /\n"
    (OUT / "robots.txt").write_text(robots, encoding="utf-8")
    urls = "".join(f"<url><loc>{esc(SITE_URL + p)}</loc></url>" for p in paths)
    (OUT / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>'
        f'<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>\n',
        encoding="utf-8")
    print(f"Built {len(paths)} pages and {len(redirects)} redirects for {SITE_URL}")


if __name__ == "__main__":
    main()
