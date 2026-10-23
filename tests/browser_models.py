"""Model setup UI contract test with deterministic download API responses."""

import json
import os
from pathlib import Path

from playwright.sync_api import expect, sync_playwright


def main():
    base = os.environ.get("MDE_TEST_URL", "http://127.0.0.1:8765")
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1440, "height": 1000})
        models = [
            {
                "name": name,
                "status": "missing",
                "downloaded_bytes": 0,
                "total_bytes": 80000000,
                "can_cancel": False,
                "error": None,
            }
            for name in ("tiny", "base", "small", "medium", "large-v3")
        ]
        errors = []
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.route(
            "**/api/health",
            lambda route: route.fulfill(
                json={"version": "0.2.0", "whisper": True, "ffmpeg": True, "desktop": False, "ollama": False}
            ),
        )
        page.route("**/api/models", lambda route: route.fulfill(json={"models": models}))

        def action(route):
            model = models[1]
            if route.request.url.endswith("/download"):
                assert route.request.headers["x-mde-client"] == "web"
                model.update(status="downloading", downloaded_bytes=40000000, can_cancel=True)
            else:
                model.update(status="paused", can_cancel=False)
            route.fulfill(body=json.dumps(model), content_type="application/json")

        page.route("**/api/models/base/*", action)
        page.goto(base)
        expect(page.locator("#model-setup-status")).to_contain_text("BASE")
        page.locator("#model-manage").click()
        card = page.locator('[data-model="base"]')
        card.get_by_role("button", name="Download", exact=True).click()
        expect(card.locator("progress")).to_have_attribute("value", "40000000")
        card.get_by_role("button", name="Cancel", exact=True).click()
        expect(card).to_contain_text("Paused")
        card.get_by_role("button", name="Resume / retry").click()
        expect(card).to_contain_text("Downloading")
        models[1].update(status="ready", downloaded_bytes=80000000, can_cancel=False)
        expect(card).to_contain_text("Ready for offline transcription", timeout=6000)
        expect(card.locator("button")).to_have_count(0)
        page.locator("#settings-close").click()
        page.locator("#locale-toggle").click()
        expect(page.locator("#model-setup-status")).to_contain_text("可离线转录")
        page.set_viewport_size({"width": 390, "height": 844})
        page.locator("#model-manage").click()
        expect(page.locator("#model-list")).to_contain_text("已就绪")
        assert page.evaluate("document.documentElement.scrollWidth <= innerWidth")
        if os.environ.get("MDE_SCREENSHOT_DIR"):
            folder = Path(os.environ["MDE_SCREENSHOT_DIR"])
            folder.mkdir(parents=True, exist_ok=True)
            page.screenshot(path=str(folder / "models-mobile.png"))
            page.set_viewport_size({"width": 1440, "height": 1000})
            page.screenshot(path=str(folder / "models-desktop.png"))
        assert not errors, errors
        browser.close()
    print("Model UI passed: download, progress, cancel, resume, ready, Chinese, mobile.")


if __name__ == "__main__":
    main()
