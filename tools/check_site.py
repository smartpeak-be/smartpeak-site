"""Check the built site in _site/ for broken internal links, images and anchors.

Also enforces a few SEO basics per page: exactly one <h1>, a <title>, a meta
description and a canonical link. Exits with status 1 when something is wrong.
"""
import os
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlparse

SITE = Path(__file__).resolve().parent.parent / "_site"
BASE_PATH = urlparse(os.environ.get("SITE_URL", "")).path.rstrip("/")


class PageScan(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links, self.ids, self.h1 = [], set(), 0
        self.has = {"title": False, "description": False, "canonical": False}
        self.redirect = False

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if attrs.get("id"):
            self.ids.add(attrs["id"])
        if tag in ("a", "link") and attrs.get("href"):
            if attrs.get("rel") == "canonical":
                self.has["canonical"] = True
            elif tag == "a":
                self.links.append(attrs["href"])
        if tag in ("img", "script") and attrs.get("src"):
            self.links.append(attrs["src"])
        if tag == "h1":
            self.h1 += 1
        if tag == "title":
            self.has["title"] = True
        if tag == "meta" and attrs.get("name") == "description" and attrs.get("content"):
            self.has["description"] = True
        if tag == "meta" and attrs.get("http-equiv") == "refresh":
            self.redirect = True


def target_for(path):
    path = unquote(path)
    if BASE_PATH and path.startswith(BASE_PATH + "/"):
        path = path[len(BASE_PATH):]
    file = SITE / path.lstrip("/")
    return file / "index.html" if path.endswith("/") else file


def main():
    pages = {f: PageScan() for f in SITE.rglob("*.html")}
    for file, scan in pages.items():
        scan.feed(file.read_text(encoding="utf-8"))

    problems = []
    for file, scan in pages.items():
        name = "/" + str(file.relative_to(SITE))
        if not scan.redirect:
            if scan.h1 != 1:
                problems.append(f"{name}: {scan.h1} <h1> elements")
            problems += [f"{name}: missing {key}" for key, ok in scan.has.items() if not ok]
        for link in scan.links:
            parsed = urlparse(link)
            if parsed.scheme or link.startswith(("mailto:", "tel:", "//")):
                continue
            if not parsed.path:
                if parsed.fragment and parsed.fragment not in scan.ids:
                    problems.append(f"{name}: missing anchor #{parsed.fragment}")
                continue
            target = target_for(parsed.path)
            if not target.exists():
                problems.append(f"{name}: broken link {link}")
            elif parsed.fragment and target.suffix == ".html":
                target_scan = pages.get(target)
                if target_scan and parsed.fragment not in target_scan.ids:
                    problems.append(f"{name}: missing anchor {link}")

    for problem in sorted(set(problems)):
        print(problem)
    print(f"Checked {len(pages)} pages: {len(set(problems))} problem(s)")
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    main()
