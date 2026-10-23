"""Desktop preferences must not overwrite edits or save out of order."""

import asyncio
import os

from playwright.async_api import async_playwright, expect


async def main():
    base = os.environ.get("MDE_TEST_URL", "http://127.0.0.1:8765")
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={"width": 1440, "height": 1000})
        release_health = asyncio.Event()
        health_started = asyncio.Event()
        release_get = asyncio.Event()
        get_started = asyncio.Event()
        release_put = asyncio.Event()
        put_started = asyncio.Event()
        gets = []
        writes = []
        errors = []
        page.on("pageerror", lambda error: errors.append(str(error)))

        async def health(route):
            health_started.set()
            await release_health.wait()
            await route.fulfill(json={"version": "0.2.0", "whisper": True, "ffmpeg": True, "desktop": True})

        await page.route("**/api/health", health)

        async def preferences(route):
            if route.request.method == "GET":
                gets.append(True)
                get_started.set()
                await release_get.wait()
                await route.fulfill(
                    json={"locale": "en", "language": "auto", "model": "base", "notes": False}
                )
            else:
                writes.append(route.request.post_data_json)
                put_started.set()
                if len(writes) == 1:
                    await release_put.wait()
                await route.fulfill(json=writes[-1])

        await page.route("**/api/preferences", preferences)
        await page.goto(base)
        await asyncio.wait_for(health_started.wait(), timeout=5)
        await page.locator("#language").select_option("zh")
        release_health.set()
        await asyncio.wait_for(get_started.wait(), timeout=5)
        await page.locator("#settings-open").click()
        await page.locator("#settings-close").click()
        await page.locator("#model").select_option("tiny")
        release_get.set()
        await asyncio.wait_for(put_started.wait(), timeout=5)
        await expect(page.locator("#model")).to_have_value("tiny")
        assert len(gets) == 1, gets
        await expect(page.locator("#language")).to_have_value("zh")
        await page.locator("#model").select_option("small")
        await page.locator("#language").select_option("ja")
        # First save is still held; later snapshots must remain queued in the client.
        assert len(writes) == 1, writes
        release_put.set()
        for _ in range(50):
            if len(writes) == 3:
                break
            await asyncio.sleep(0.1)
        assert [w["model"] for w in writes] == ["tiny", "small", "small"], writes
        assert writes[-1]["language"] == "ja", writes
        assert not errors, errors
        await browser.close()
    print("Desktop preference races passed: one GET, no stale overwrite, ordered PUT snapshots.")


if __name__ == "__main__":
    asyncio.run(main())
