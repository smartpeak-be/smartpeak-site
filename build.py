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
IMAGE_SIZES_FILE = ROOT / "content" / "image-sizes.json"
IMAGE_SIZES = json.loads(IMAGE_SIZES_FILE.read_text(encoding="utf-8")) if IMAGE_SIZES_FILE.exists() else {}
TITLE_MAX = 60  # longer titles get cut off in search results
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


def img_tag(src, alt="", sizes="(max-width: 760px) 100vw, 720px", eager=False, css_class=""):
    """<img> with the real width/height and, when tools/make_image_variants.py made one,
    a smaller variant in srcset. Only the first image in view should be eager."""
    info = IMAGE_SIZES.get(src, {})
    attrs = [f'src="{esc(src)}"', f'alt="{esc(alt)}"']
    if css_class:
        attrs.insert(0, f'class="{css_class}"')
    if info.get("variant"):
        attrs.append(f'srcset="{esc(info["variant"])} 640w, {esc(src)} {info["width"]}w" sizes="{sizes}"')
    if info:
        attrs.append(f'width="{info["width"]}" height="{info["height"]}"')
    attrs.append('fetchpriority="high"' if eager else 'loading="lazy"')
    attrs.append('decoding="async"')
    return f'<img {" ".join(attrs)}>'


def post_cards(posts, eager_first=False):
    cards = []
    for i, post in enumerate(posts):
        image = (img_tag(post["image"], sizes="(max-width: 700px) 100vw, 380px", eager=eager_first and i == 0)
                 if post.get("image") else "")
        cards.append(f'''<li class="post-card">
  <a href="{post["path"]}">{image}<span class="post-card-text">
    <time datetime="{post["date"]}">{dutch_date(post["date"])}</time>
    <strong>{esc(post["title"])}</strong>
    <span>{esc(post["description"])}</span>
  </span></a>
</li>''')
    return '<ul class="post-cards">' + "\n".join(cards) + "</ul>"


def realisatie_cards(items, eager_first=False):
    cards = []
    for i, item in enumerate(items):
        facts = "".join(f"<li>{esc(fact)}</li>" for fact in item.get("facts", []))
        image = img_tag(item["image"], item["alt"], sizes="(max-width: 700px) 100vw, 380px", eager=eager_first and i == 0)
        cards.append(f'''<figure class="realisatie">
  {image}
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


def analysis_widget():
    """The verbruiksanalyse wizard from battery-roi-tool, embedded in the page (no keys)."""
    return (f'<div id="smartpeak-analyse" class="analysis-mount"'
            f' data-help-url="/hulp/p1-poort-activeren/#verbruik-downloaden"'
            f' data-inverter-help-url="/hulp/omvormer-vermogen-vinden/"'
            f' data-privacy-url="/privacyverklaring/" data-email="{esc(SITE["email"])}">\n'
            f'<noscript><p>De analyse heeft JavaScript nodig. Je kan ook '
            f'<a href="{esc(SITE["analysis_url"])}" rel="noopener">de analyse op een aparte pagina openen</a> '
            f'of je CSV-bestand mailen naar <a href="mailto:{esc(SITE["email"])}">{esc(SITE["email"])}</a>.</p></noscript>\n'
            f'</div>\n'
            f'<script type="module" src="{esc(SITE["analysis_widget_url"])}"></script>')


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
        "analysis_widget": analysis_widget(),
        "email": esc(SITE["email"]),
        "phone": esc(SITE["phone"]),
        "phone_href": esc(SITE["phone_href"]),
        "hours": esc(SITE["hours"]),
        "latest_posts": post_cards(posts[:3]),
        "article_list": post_cards(posts, eager_first=True),
        "realisaties": realisatie_cards(realisaties, eager_first=True),
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


def page_title(meta):
    """Add the brand to the title when it still fits in a search result."""
    with_brand = f'{meta["title"]} | {SITE["name"]}'
    if meta["path"] == "/" or len(with_brand) > TITLE_MAX:
        return meta["title"]
    return with_brand


def share_image(meta):
    """Link-preview image: a JPEG made for it when there is one (not every platform shows WebP)."""
    if meta.get("slug") and (ROOT / "assets" / "img" / "og" / f'{meta["slug"]}.jpg').exists():
        return f'/assets/img/og/{meta["slug"]}.jpg', meta.get("image_alt") or meta["title"]
    return "/assets/img/site/og-smartpeak.jpg", "SmartPeak, slim omgaan met jouw energie"


def preconnects(body):
    """Open connections early to the services a widget on this page will call."""
    origins = []
    if "smartpeak-reviews" in body or "smartpeak-analyse" in body:
        origins += ["https://smartpeak-be.github.io", "https://firestore.googleapis.com"]
    return "\n".join(f'<link rel="preconnect" href="{o}" crossorigin>' for o in origins)


def scrollable_tables(body):
    """Wide tables scroll inside a focusable region, so keyboard users can scroll them too.
    The region is named after the table caption or the heading above it, and kept unique."""
    used = {}

    def wrap(match):
        caption = re.search(r"<caption[^>]*>(.*?)</caption>", match.group(0), re.S)
        headings = re.findall(r"<h[2-4][^>]*>(.*?)</h[2-4]>", body[:match.start()], re.S)
        source = caption.group(1) if caption else (headings[-1] if headings else "")
        label = "Tabel: " + html.unescape(re.sub(r"<[^>]+>", "", source)).strip() if source else "Tabel"
        used[label] = used.get(label, 0) + 1
        if used[label] > 1:
            label += f" ({used[label]})"
        return f'<div class="table-scroll" role="region" tabindex="0" aria-label="{esc(label)}">{match.group(0)}</div>'
    return re.sub(r"<table\b.*?</table>", wrap, body, flags=re.S)


def enhance_images(body):
    """Hand-written <img> tags get the real size and the small variant too."""
    def fix(match):
        tag = match.group(0)
        src = re.search(r'src="([^"]+)"', tag)
        info = IMAGE_SIZES.get(src.group(1) if src else "", {})
        if not info:
            return tag
        extra = []
        if info.get("variant") and "srcset=" not in tag:
            in_shot = body[max(0, match.start() - 40):match.start()].endswith('<figure class="product-shot">')
            sizes = "(max-width: 640px) 320px, 300px" if in_shot else "(max-width: 760px) 100vw, 720px"
            extra.append(f'srcset="{esc(info["variant"])} 640w, {esc(src.group(1))} {info["width"]}w" sizes="{sizes}"')
        if "width=" not in tag:
            extra.append(f'width="{info["width"]}" height="{info["height"]}"')
        return tag[:-1].rstrip("/ ") + (" " + " ".join(extra) if extra else "") + ">"
    return re.sub(r"<img\b[^>]*>", fix, body)


def render(meta, body, titles):
    layout = (ROOT / "templates" / "layout.html").read_text(encoding="utf-8")
    title = page_title(meta)
    image, image_alt = share_image(meta)
    body = enhance_images(scrollable_tables(body))
    noindex = not IS_LIVE_DOMAIN or meta["path"] == "/404/"
    page = fill(layout, {
        "title": esc(title),
        "description": esc(meta.get("description")),
        "canonical": esc(SITE_URL + meta["path"]),
        "og_image": esc(SITE_URL + image),
        "og_image_alt": esc(image_alt),
        "site_name": esc(SITE["name"]),
        "head_extra": preconnects(body),
        "og_type": "article" if meta.get("date") else "website",
        "robots": "noindex, nofollow" if noindex else "index, follow",
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
    page = re.sub(r'((?:href|src|action|data-[\w-]+-url)=")/(?!/)', rf"\1{BASE_PATH}/", page)
    return re.sub(r'srcset="([^"]*)"',
                  lambda m: 'srcset="' + re.sub(r'(^|, )/(?!/)', rf"\1{BASE_PATH}/", m.group(1)) + '"', page)


def article(meta, body, kicker=""):
    image = (img_tag(meta["image"], meta.get("image_alt", ""), eager=True, css_class="article-image")
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
    modified = post.get("modified")
    updated = (f', bijgewerkt op <time datetime="{modified}">{dutch_date(modified)}</time>'
               if modified and modified != post["date"] else "")
    kicker = (f'<p class="article-meta"><a href="/artikels/">Artikels</a> <span aria-hidden="true">/</span> '
              f'<time datetime="{post["date"]}">{dutch_date(post["date"])}</time>{updated}</p>')
    return article(post, post["body"], kicker) + cta


def redirect_page(target):
    url = esc(BASE_PATH + target)
    return (f'<!doctype html><html lang="nl"><head><meta charset="utf-8">'
            f'<title>Doorverwijzing | {SITE["name"]}</title><meta name="robots" content="noindex">'
            f'<link rel="canonical" href="{esc(SITE_URL + target)}">'
            f'<meta http-equiv="refresh" content="0; url={url}"></head>'
            f'<body><p>Deze pagina is verhuisd naar <a href="{url}">{url}</a>.</p></body></html>')


def minify_css(css):
    """Drop comments and whitespace. Spaces around ':' stay: they can be part of a selector."""
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    css = re.sub(r"\s+", " ", css)
    css = re.sub(r"\s*([{};,>])\s*", r"\1", css)
    return css.replace(";}", "}").strip() + "\n"


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
    css = OUT / "assets" / "css" / "site.css"
    css.write_text(minify_css(css.read_text(encoding="utf-8")), encoding="utf-8")

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
        write_page(meta["path"], render(meta, article(meta, fill(body, values)) + (cta if with_cta else ""), titles))
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
    lastmod = {p["path"]: p.get("modified") or p["date"] for p in posts}
    urls = "".join(f"<url><loc>{esc(SITE_URL + p)}</loc>"
                   + (f"<lastmod>{lastmod[p]}</lastmod>" if p in lastmod else "") + "</url>" for p in paths)
    (OUT / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>'
        f'<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>\n',
        encoding="utf-8")
    print(f"Built {len(paths)} pages and {len(redirects)} redirects for {SITE_URL}")


if __name__ == "__main__":
    main()
