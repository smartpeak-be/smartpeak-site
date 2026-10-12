"""Walk through the live battery analysis wizard once, end to end.

Creates ONE real test lead (name starts with "TEST") and triggers the real result mail.
Screenshots and a log end up in content/e2e-lead/. Run via
.github/workflows/e2e-lead-live.yml only, and delete the test lead afterwards.
"""
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

URL = "https://smartpeak-be.github.io/battery-roi-tool/lead.html"
OUT = Path(__file__).resolve().parent.parent / "content" / "e2e-lead"
CSV, EMAIL = sys.argv[1], sys.argv[2]


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    log = []
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 430, "height": 900})
        page.on("console", lambda m: log.append(f"console.{m.type}: {m.text}"))
        page.on("pageerror", lambda e: log.append(f"pageerror: {e}"))
        page.on("requestfailed", lambda r: log.append(f"requestfailed: {r.url} {r.failure}"))
        ok = False
        try:
            page.goto(URL, wait_until="networkidle")
            page.screenshot(path=OUT / "1-start.png", full_page=True)
            page.set_input_files("#csvFileInput", CSV)
            page.wait_for_selector("#btnStep1Next:not([disabled])", timeout=15000)
            page.screenshot(path=OUT / "2-csv-geladen.png", full_page=True)
            page.click("#btnStep1Next")
            page.fill("#leadName", "TEST website-check (mag weg)")
            page.fill("#leadEmail", EMAIL)
            page.click("#btnStep2Next")
            page.wait_for_selector("#step3.active", timeout=10000)
            page.screenshot(path=OUT / "3-optioneel.png", full_page=True)
            page.click("#btnSubmit")
            page.wait_for_selector("#step4.active", timeout=90000)
            page.screenshot(path=OUT / "4-bevestiging.png", full_page=True)
            log.append("RESULT: wizard completed, confirmation shown for " + page.inner_text("#confirmEmail"))
            ok = True
        except Exception as error:
            log.append(f"RESULT: FAILED: {error}")
            page.screenshot(path=OUT / "fout.png", full_page=True)
            toasts = page.locator("#toastContainer").inner_text()
            if toasts.strip():
                log.append("toast: " + toasts.strip())
        browser.close()
    (OUT / "log.txt").write_text("\n".join(log) + "\n", encoding="utf-8")
    print("\n".join(log))
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
