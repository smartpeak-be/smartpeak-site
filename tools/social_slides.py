"""Social media images (Instagram/Facebook carousel, 1080 x 1350, 4:5) in the SmartPeak house style.

Each set is described in content/social/<slug>.json (texts for the posts sit in the same file,
see .claude/skills/smartpeak-social/SKILL.md):
  {"page": "/artikels/<slug>/", "slides": [
     {"type": "cover", "kicker": "...", "title": "...", "sub": "..."},
     {"type": "cover", "kicker": "...", "title": "...", "image": "/assets/img/grafieken/<x>.webp"},   (graph as eyecatcher)
     {"type": "cover", "kicker": "...", "title": "...", "image": "/assets/img/site/<x>.webp", "photo": true},  (full-bleed photo)
     {"type": "image", "title": "...", "image": "/assets/img/grafieken/<x>.webp", "body": "...", "source": "..."},
     {"type": "stat", "value": "51%", "title": "...", "sub": "...", "source": "..."},
     {"type": "list", "title": "...", "items": ["...", "..."], "source": "..."},
     {"type": "text", "title": "...", "body": "...", "source": "..."},
     {"type": "review", "rating": 5, "quote": "...", "name": "...", "label": "..."},
     {"type": "cta", "title": "...", "sub": "...", "url": "smartpeak.be/..."}
  ]}

Run: python3 tools/social_slides.py <slug>   → assets/img/social/<slug>-1.jpg, -2.jpg, ...
     python3 tools/social_slides.py --tiktok <slug>   → assets/img/social/tiktok/<slug>-N.jpg (1080 x 1920, 9:16),
     with the content inside TikTok's safe zone (top bar, buttons on the right, caption at the bottom).
Published on the site, the images get a public URL that Metricool can use.
"""
import base64
import html
import json
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
SPECS = ROOT / "content" / "social"
OUT = ROOT / "assets" / "img" / "social"
FONT = "data:font/woff2;base64," + base64.b64encode((ROOT / "assets" / "fonts" / "instrument-sans.woff2").read_bytes()).decode()
MARK = "data:image/png;base64," + base64.b64encode((ROOT / "assets" / "logo" / "smartpeak-logo-mark.png").read_bytes()).decode()
W, H = 1080, 1350
TIKTOK_H = 1920
# TikTok covers the top ~200 px, the right ~150 px (buttons) and the bottom ~380 px (caption).
TIKTOK_CSS = f"""
body, .slide {{ height: {TIKTOK_H}px; }}
.slide {{ padding: 230px 170px 380px 88px; }}
h1 {{ font-size: 96px; }}
.chart {{ width: 100%; margin: 8px 0 0; }}
.photo {{ padding: 0 0 380px; background: #0d2a24; }}
.photo .main {{ padding: 230px 170px 48px 88px; }}
.photo .foot {{ padding: 0 170px 0 88px; }}
"""

CSS = f"""
@font-face {{ font-family: "Instrument Sans"; src: url("{FONT}") format("woff2"); font-weight: 400 700; }}
* {{ box-sizing: border-box; margin: 0; }}
body {{ width: {W}px; height: {H}px; font-family: "Instrument Sans", sans-serif; color: #1f272e; background: #fff; }}
.slide {{ width: {W}px; height: {H}px; padding: 96px 88px 0; display: flex; flex-direction: column; position: relative; }}
.dark {{ background: linear-gradient(135deg, #0b7a42 0%, #0a6a78 100%); color: #fff; }}
.kicker {{ font-size: 34px; font-weight: 650; letter-spacing: .02em; color: #0b7a42; text-transform: uppercase; margin-bottom: 36px; }}
.dark .kicker {{ color: #bdf3d2; }}
h1 {{ font-size: 104px; line-height: 1.04; font-weight: 700; letter-spacing: -.01em; }}
h2 {{ font-size: 70px; line-height: 1.1; font-weight: 700; margin-bottom: 44px; }}
.sub {{ font-size: 44px; line-height: 1.35; color: #4b5661; margin-top: 44px; }}
.dark .sub {{ color: #e6f6ee; }}
.value {{ font-size: 230px; font-weight: 700; line-height: 1; color: #c2412d; margin: 40px 0 28px; letter-spacing: -.03em; }}
.body {{ font-size: 48px; line-height: 1.4; color: #1f272e; }}
ol {{ list-style: none; padding: 0; counter-reset: n; }}
li {{ counter-increment: n; font-size: 44px; line-height: 1.32; padding: 26px 0 26px 104px; position: relative; border-top: 3px solid #e3ebe8; }}
li::before {{ content: counter(n); position: absolute; left: 0; top: 22px; width: 70px; height: 70px; border-radius: 50%;
  background: #17c15c; color: #fff; font-weight: 700; font-size: 38px; display: grid; place-items: center; }}
.stars {{ font-size: 64px; color: #17c15c; letter-spacing: 6px; margin-bottom: 40px; }}
.quote {{ font-size: 52px; line-height: 1.32; font-weight: 600; }}
.quote::before {{ content: "“"; display: block; font-size: 140px; line-height: .6; color: #17c15c; }}
.who {{ font-size: 36px; font-weight: 650; margin-top: 48px; }}
.who span {{ display: block; font-weight: 400; color: #4b5661; font-size: 30px; margin-top: 8px; }}
.url {{ display: inline-block; margin-top: 56px; font-size: 40px; font-weight: 650; background: #fff; color: #0b7a42; padding: 22px 34px; border-radius: 999px; }}
.main {{ flex: 1; display: flex; flex-direction: column; justify-content: center; padding-bottom: 40px; }}
.source {{ font-size: 24px; line-height: 1.35; color: #4b5661; margin-bottom: 22px; }}
.dark .source {{ color: #d9f2e6; }}
.foot {{ height: 120px; border-top: 3px solid #e3ebe8; display: flex; align-items: center; gap: 18px; font-size: 30px; font-weight: 650; }}
.dark .foot {{ border-top-color: rgba(255,255,255,.35); }}
.foot img {{ width: 52px; height: 52px; }}
.foot .count {{ margin-left: auto; font-weight: 400; color: #4b5661; }}
.dark .foot .count {{ color: #e6f6ee; }}
/* graphs from the site as eyecatcher: wider than the text column */
.chart {{ width: calc(100% + 96px); margin: 8px -48px 0; border-radius: 18px; border: 3px solid #e3ebe8; display: block; }}
h2.lead {{ font-size: 78px; line-height: 1.06; margin-bottom: 40px; }}
.body.small {{ font-size: 40px; margin-top: 40px; color: #4b5661; }}
/* full-bleed photo with the title on a shade at the bottom */
.photo {{ color: #fff; padding: 0; }}
.photo .main {{ justify-content: flex-end; padding: 0 88px 56px; position: relative; }}
.photo .bg {{ position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; }}
.photo .shade {{ position: absolute; inset: 0; background: linear-gradient(180deg, rgba(10,30,25,0) 35%, rgba(10,30,25,.82) 78%); }}
.photo .over {{ position: relative; }}
.photo .kicker {{ color: #bdf3d2; }}
.photo h1 {{ font-size: 92px; text-shadow: 0 2px 18px rgba(0,0,0,.35); }}
.photo .sub {{ color: #e6f6ee; font-size: 40px; margin-top: 28px; }}
.photo .foot {{ position: relative; background: #0d2a24; color: #fff; border-top: 0; padding: 0 88px; }}
.photo .foot .count {{ color: #e6f6ee; }}
.photo .source {{ display: none; }}
"""


def e(s):
    return html.escape(s or "")


def data_uri(path):
    """A site image (path as used on the site, e.g. /assets/img/grafieken/x.webp) as a data URI."""
    file = ROOT / path.lstrip("/")
    mime = {".webp": "image/webp", ".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".svg": "image/svg+xml"}[file.suffix]
    return f"data:{mime};base64," + base64.b64encode(file.read_bytes()).decode()


def slide_html(s, n, total, extra_css=""):
    t = s["type"]
    dark = t in ("cover", "cta") and not s.get("image")
    photo = t == "cover" and s.get("image") and s.get("photo")
    if photo:
        inner = (f'<img class="bg" src="{data_uri(s["image"])}" alt=""><div class="shade"></div>'
                 f'<div class="over"><div class="kicker">{e(s.get("kicker"))}</div><h1>{e(s["title"])}</h1>'
                 + (f'<p class="sub">{e(s["sub"])}</p>' if s.get("sub") else "") + '</div>')
    elif t == "cover" and s.get("image"):
        inner = (f'<div class="kicker">{e(s.get("kicker"))}</div><h2 class="lead">{e(s["title"])}</h2>'
                 f'<img class="chart" src="{data_uri(s["image"])}" alt="">'
                 + (f'<p class="body small">{e(s["sub"])}</p>' if s.get("sub") else ""))
    elif t == "image":
        inner = (f'<h2>{e(s["title"])}</h2><img class="chart" src="{data_uri(s["image"])}" alt="">'
                 + (f'<p class="body small">{e(s["body"])}</p>' if s.get("body") else ""))
    elif t == "cover":
        inner = f'<div class="kicker">{e(s.get("kicker"))}</div><h1>{e(s["title"])}</h1><p class="sub">{e(s.get("sub"))}</p>'
    elif t == "stat":
        inner = f'<h2>{e(s["title"])}</h2><div class="value">{e(s["value"])}</div><p class="body">{e(s.get("sub"))}</p>'
    elif t == "list":
        items = "".join(f"<li>{e(i)}</li>" for i in s["items"])
        inner = f'<h2>{e(s["title"])}</h2><ol>{items}</ol>'
    elif t == "text":
        inner = f'<h2>{e(s["title"])}</h2><p class="body">{e(s["body"])}</p>'
    elif t == "review":
        stars = "★" * int(s.get("rating", 5)) + "☆" * (5 - int(s.get("rating", 5)))
        inner = (f'<div class="stars" aria-label="{e(str(s.get("rating", 5)))} op 5">{stars}</div>'
                 f'<p class="quote">{e(s["quote"])}</p><p class="who">{e(s["name"])}<span>{e(s.get("label"))}</span></p>')
    elif t == "cta":
        inner = f'<h1>{e(s["title"])}</h1><p class="sub">{e(s.get("sub"))}</p><div><span class="url">{e(s["url"])}</span></div>'
    else:
        raise ValueError(f"unknown slide type {t}")
    source = f'<p class="source">{e(s["source"])}</p>' if s.get("source") else ""
    foot = (f'<div class="foot"><img src="{MARK}" alt="">SmartPeak'
            f'<span class="count">{n}/{total}</span></div>')
    classes = "slide" + (" dark" if dark else "") + (" photo" if photo else "")
    return (f'<html><head><meta charset="utf-8"><style>{CSS}{extra_css}</style></head><body>'
            f'<div class="{classes}"><div class="main">{inner}</div>{source}{foot}</div></body></html>')


def render(slug, tiktok=False):
    spec = json.loads((SPECS / f"{slug}.json").read_text(encoding="utf-8"))
    slides = spec["slides"]
    h, extra, out_dir = (TIKTOK_H, TIKTOK_CSS, OUT / "tiktok") if tiktok else (H, "", OUT)
    out_dir.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": W, "height": h})
        for i, s in enumerate(slides, 1):
            page.set_content(slide_html(s, i, len(slides), extra))
            page.evaluate("document.fonts.ready")
            overflow = page.evaluate("document.querySelector('.slide').scrollHeight > %d" % h)
            out = out_dir / f"{slug}-{i}.jpg"
            page.screenshot(path=str(out), type="jpeg", quality=90, clip={"x": 0, "y": 0, "width": W, "height": h})
            print("rendered", out.relative_to(ROOT), "(TE VEEL TEKST: inkorten)" if overflow else "")
        browser.close()


if __name__ == "__main__":
    args = sys.argv[1:]
    tiktok = "--tiktok" in args
    slugs = [a for a in args if a != "--tiktok"]
    if not slugs:
        sys.exit("usage: python3 tools/social_slides.py [--tiktok] <slug> [<slug> ...]")
    for slug in slugs:
        render(slug, tiktok)
