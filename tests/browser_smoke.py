"""Optional UI regression: pip install playwright && playwright install chromium.

Start mde serve, then MDE_TEST_URL=http://127.0.0.1:8765 python tests/browser_smoke.py.
Creates and deletes its own demo/upload jobs.
"""

import os

from playwright.sync_api import expect, sync_playwright


def main():
    base = os.environ.get("MDE_TEST_URL", "http://127.0.0.1:8765")
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1440, "height": 1000})
        errors = []
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.goto(base)
        page.locator("#health-status.online").wait_for()
        before = {j["id"] for j in page.request.get(base + "/api/jobs").json()["jobs"]}
        try:
            page.locator("#demo-button").click()
            page.locator("#document-actions").wait_for(state="visible")
            assert page.locator(".document-body h1").inner_text() == "From watching to knowing"
            page.locator("#raw-view").click()
            assert "## Transcript" in page.locator(".document-body.raw").inner_text()
            page.locator("#read-view").click()
            page.set_viewport_size({"width": 390, "height": 844})
            page.locator("#search").fill("no-such-title-0238")
            assert page.locator("#search").is_visible()
            page.locator("#search").fill("")
            assert page.locator(".job-item").count() > 0
            assert page.evaluate("document.documentElement.scrollWidth <= innerWidth")
            page.set_viewport_size({"width": 1440, "height": 1000})
            page.locator("#locale-toggle").click()
            assert "少一点观看" in page.locator("#hero-title").inner_text()
            page.locator("#file-tab").click()
            # HTML entities are decoded into text, never into live HTML nodes.
            page.locator("#files").set_input_files(
                {
                    "name": "浏览器回归.srt",
                    "mimeType": "application/x-subrip",
                    "buffer": b"1\n00:00:00,000 --> 00:00:02,000\nA &amp; B ~ &lt;script&gt;\n",
                }
            )
            page.locator("#convert-button").click()
            expect(page.locator(".document-body h1")).to_have_text("浏览器回归", timeout=15000)
            assert "A & B ~ <script>" in page.locator(".document-body").inner_text()
            assert page.locator(".document-body script").count() == 0
            for fmt in ("md", "srt", "json"):
                page.locator("#export-format").select_option(fmt)
                with page.expect_download() as result:
                    page.locator("#download-button").click()
                assert result.value.suggested_filename.endswith("." + fmt)
            assert not errors, errors
        finally:
            jobs = page.request.get(base + "/api/jobs").json()["jobs"]
            for job in jobs:
                if job["id"] not in before and job["status"] in ("done", "error", "cancelled"):
                    page.request.delete(base + "/api/jobs/" + job["id"], headers={"X-MDE-Client": "web"})
            browser.close()
    print("Browser smoke passed: real conversion, mobile search, localization, safe preview, three exports.")


if __name__ == "__main__":
    main()
