"""Check the embedded verbruiksanalyse on the published site without creating a lead.

Loads /batterij-iets-voor-mij/, waits for the widget, loads the Fluvius test file, fills in
step 2 and stops before submitting. Also checks that the product list loads from Firestore.
Run via .github/workflows/e2e-lead-live.yml (mode embed-check).
"""
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

URL = "https://smartpeak-be.github.io/smartpeak-site/batterij-iets-voor-mij/"
OUT = Path(__file__).resolve().parent.parent / "content" / "e2e-lead"
CSV = sys.argv[1]


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    log, ok = [], False
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 430, "height": 900})
        page.on("console", lambda m: log.append(f"console.{m.type}: {m.text}"))
        page.on("pageerror", lambda e: log.append(f"pageerror: {e}"))
        page.on("requestfailed", lambda r: log.append(f"requestfailed: {r.url} {r.failure}"))
        page.on("response", lambda r: log.append(f"response {r.status}: {r.url[:120]}")
                if "config/products" in r.url or "docs.google" in r.url or "lead-wizard" in r.url else None)
        try:
            page.goto(URL, wait_until="networkidle")
            page.wait_for_selector("#smartpeak-analyse.spa", timeout=15000)
            mount = page.locator("#smartpeak-analyse")
            mount.screenshot(path=OUT / "embed-1-start.png")
            with page.expect_response(lambda r: "config/products" in r.url, timeout=15000) as products:
                page.set_input_files("#smartpeak-analyse [data-file]", CSV)
            page.wait_for_selector('#smartpeak-analyse [data-next="2"]:not([disabled])', timeout=15000)
            assert products.value.ok, f"config/products returned {products.value.status}"
            page.wait_for_timeout(3000)  # let the product sheet load too
            mount.screenshot(path=OUT / "embed-2-geladen.png")
            page.click('#smartpeak-analyse [data-next="2"]')
            page.fill("#smartpeak-analyse [data-name]", "Controle zonder verzenden")
            page.fill("#smartpeak-analyse [data-email]", "controle@example.com")
            page.click('#smartpeak-analyse [data-next="3"]')
            page.wait_for_selector('#smartpeak-analyse [data-step="3"]:not([hidden])')
            mount.screenshot(path=OUT / "embed-3-optioneel.png")
            log.append("RESULT: widget works up to the submit button (nothing was sent)")
            ok = True
        except Exception as error:
            log.append(f"RESULT: FAILED: {error}")
            page.screenshot(path=OUT / "embed-fout.png", full_page=True)
        browser.close()
    (OUT / "embed-log.txt").write_text("\n".join(log) + "\n", encoding="utf-8")
    print("\n".join(log))
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
