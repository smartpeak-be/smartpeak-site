"""Social media images (Instagram/Facebook carousel, 1080 x 1350, 4:5) in the SmartPeak house style.

Each set is described in content/social/<slug>.json:
  {"slides": [
     {"type": "cover", "kicker": "...", "title": "...", "sub": "..."},
     {"type": "stat", "value": "51%", "title": "...", "sub": "...", "source": "..."},
     {"type": "list", "title": "...", "items": ["...", "..."], "source": "..."},
     {"type": "text", "title": "...", "body": "...", "source": "..."},
     {"type": "cta", "title": "...", "sub": "...", "url": "smartpeak.be/..."}
  ]}

Run: python3 tools/social_slides.py <slug>   → assets/img/social/<slug>-1.jpg, -2.jpg, ...
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
.url {{ display: inline-block; margin-top: 56px; font-size: 40px; font-weight: 650; background: #fff; color: #0b7a42; padding: 22px 34px; border-radius: 999px; }}
.main {{ flex: 1; display: flex; flex-direction: column; justify-content: center; padding-bottom: 40px; }}
.source {{ font-size: 24px; line-height: 1.35; color: #4b5661; margin-bottom: 22px; }}
.dark .source {{ color: #d9f2e6; }}
.foot {{ height: 120px; border-top: 3px solid #e3ebe8; display: flex; align-items: center; gap: 18px; font-size: 30px; font-weight: 650; }}
.dark .foot {{ border-top-color: rgba(255,255,255,.35); }}
.foot img {{ width: 52px; height: 52px; }}
.foot .count {{ margin-left: auto; font-weight: 400; color: #4b5661; }}
.dark .foot .count {{ color: #e6f6ee; }}
"""


def e(s):
    return html.escape(s or "")


def slide_html(s, n, total):
    t = s["type"]
    dark = t in ("cover", "cta")
    if t == "cover":
        inner = f'<div class="kicker">{e(s.get("kicker"))}</div><h1>{e(s["title"])}</h1><p class="sub">{e(s.get("sub"))}</p>'
    elif t == "stat":
        inner = f'<h2>{e(s["title"])}</h2><div class="value">{e(s["value"])}</div><p class="body">{e(s.get("sub"))}</p>'
    elif t == "list":
        items = "".join(f"<li>{e(i)}</li>" for i in s["items"])
        inner = f'<h2>{e(s["title"])}</h2><ol>{items}</ol>'
    elif t == "text":
        inner = f'<h2>{e(s["title"])}</h2><p class="body">{e(s["body"])}</p>'
    elif t == "cta":
        inner = f'<h1>{e(s["title"])}</h1><p class="sub">{e(s.get("sub"))}</p><div><span class="url">{e(s["url"])}</span></div>'
    else:
        raise ValueError(f"unknown slide type {t}")
    source = f'<p class="source">{e(s["source"])}</p>' if s.get("source") else ""
    foot = (f'<div class="foot"><img src="{MARK}" alt="">SmartPeak'
            f'<span class="count">{n}/{total}</span></div>')
    return (f'<html><head><meta charset="utf-8"><style>{CSS}</style></head><body>'
            f'<div class="slide{" dark" if dark else ""}"><div class="main">{inner}</div>{source}{foot}</div></body></html>')


def render(slug):
    spec = json.loads((SPECS / f"{slug}.json").read_text(encoding="utf-8"))
    slides = spec["slides"]
    OUT.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": W, "height": H})
        for i, s in enumerate(slides, 1):
            page.set_content(slide_html(s, i, len(slides)))
            page.evaluate("document.fonts.ready")
            overflow = page.evaluate("document.querySelector('.slide').scrollHeight > %d" % H)
            out = OUT / f"{slug}-{i}.jpg"
            page.screenshot(path=str(out), type="jpeg", quality=90, clip={"x": 0, "y": 0, "width": W, "height": H})
            print("rendered", out.relative_to(ROOT), "(TE VEEL TEKST: inkorten)" if overflow else "")
        browser.close()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("usage: python3 tools/social_slides.py <slug> [<slug> ...]")
    for slug in sys.argv[1:]:
        render(slug)
