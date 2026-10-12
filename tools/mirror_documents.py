"""Download external files we want a local copy of.

  content/documents.json      -> assets/docs/               (datasheets, PDF)
  content/product-images.json -> content/product-images-raw/ (photos, picked and
                                 converted to WebP by hand before publishing)

Manufacturer and distributor files move or change without notice. Existing copies
are kept; pass --refresh to download everything again. Runs in GitHub Actions
(see .github/workflows/mirror-documents.yml). Stdlib only.
"""
import json
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LISTS = [
    (ROOT / "content" / "documents.json", ROOT / "assets" / "docs", (b"%PDF",)),
    (ROOT / "content" / "product-images.json", ROOT / "content" / "product-images-raw",
     (b"\x89PNG", b"\xff\xd8", b"RIFF")),
]
USER_AGENT = "Mozilla/5.0 (compatible; SmartPeakSite/1.0; +https://github.com/smartpeak-be/smartpeak-site)"


def download(url):
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=60) as response:
        return response.read()


def main():
    refresh = "--refresh" in sys.argv
    failed = []
    for list_file, target_dir, signatures in LISTS:
        if not list_file.exists():
            continue
        target_dir.mkdir(parents=True, exist_ok=True)
        for item in json.loads(list_file.read_text(encoding="utf-8")):
            target = target_dir / item["file"]
            if target.exists() and not refresh:
                continue
            try:
                body = download(item["url"])
            except Exception as error:
                failed.append(f'{item["file"]}: {error}')
                continue
            if not body.startswith(signatures):
                failed.append(f'{item["file"]}: unexpected file type')
                continue
            target.write_bytes(body)
            print(f'saved {target.relative_to(ROOT)} ({len(body) // 1024} kB)')
    for line in failed:
        print("FAILED", line)
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
