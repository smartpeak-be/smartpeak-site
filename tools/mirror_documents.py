"""Download the datasheets listed in content/documents.json into assets/docs/.

Manufacturer and distributor PDFs move or change without notice, so the site links to
a local copy. Existing copies are kept; pass --refresh to download everything again.
Runs in GitHub Actions (see .github/workflows/mirror-documents.yml). Stdlib only.
"""
import json
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / "assets" / "docs"
USER_AGENT = "Mozilla/5.0 (compatible; SmartPeakSite/1.0; +https://github.com/smartpeak-be/smartpeak-site)"


def download(url):
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=60) as response:
        return response.read()


def main():
    refresh = "--refresh" in sys.argv
    documents = json.loads((ROOT / "content" / "documents.json").read_text(encoding="utf-8"))
    TARGET.mkdir(parents=True, exist_ok=True)
    failed = []
    for document in documents:
        target = TARGET / document["file"]
        if target.exists() and not refresh:
            continue
        try:
            body = download(document["url"])
        except Exception as error:
            failed.append(f'{document["file"]}: {error}')
            continue
        if not body.startswith(b"%PDF"):
            failed.append(f'{document["file"]}: response is not a PDF')
            continue
        target.write_bytes(body)
        print(f'saved {document["file"]} ({len(body) // 1024} kB)')
    for line in failed:
        print("FAILED", line)
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
