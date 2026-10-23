'use strict';
// Run with npm-installed Playwright, or MDE_PLAYWRIGHT_MODULE=/absolute/path/to/playwright.
const { _electron: electron } = require(process.env.MDE_PLAYWRIGHT_MODULE || 'playwright');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const root = path.resolve(__dirname, '..');
(async () => {
  const data = fs.mkdtempSync(path.join(os.tmpdir(), 'mde-electron-'));
  const executable = process.argv[2] || require(path.join(root, 'desktop/node_modules/electron'));
  const app = await electron.launch({ executablePath: executable,
    args: [...(process.argv[2] ? [] : [path.join(root, 'desktop')]), '--user-data-dir=' + data],
    timeout: 90000 });
  let clipboard;
  try {
    const page = await app.firstWindow();
    const errors = [];
    page.on('pageerror', error => errors.push(error.message));
    await page.locator('#health-status.online').waitFor({ timeout: 90000 });
    assert.equal(await page.evaluate('typeof require'), 'undefined');
    assert.equal(await page.evaluate('typeof process'), 'undefined');
    await page.locator('#demo-button').click();
    await page.locator('#document-actions').waitFor({ state: 'visible', timeout: 45000 });
    clipboard = await app.evaluate(({ clipboard }) => clipboard.readText());
    await page.locator('#copy-button').click();
    await page.waitForTimeout(500);
    assert.equal(await app.evaluate(async ({ clipboard }) => (await clipboard.readText()).includes('## Transcript')), true, 'Copy did not write the document');
    const destination = path.join(data, 'export.md');
    await app.evaluate(({ BrowserWindow }, destination) => {
      BrowserWindow.getAllWindows()[0].webContents.session.once('will-download', (_event, item) => {
        globalThis.downloadOptions = item.getSaveDialogOptions();
        item.setSavePath(destination); // Automated choice; application still sets native Save dialog options.
      });
    }, destination);
    await page.locator('#download-button').click();
    for (let tries = 0; tries < 50 && !fs.existsSync(destination); tries++) await page.waitForTimeout(100);
    assert.match(fs.readFileSync(destination, 'utf8'), /## Transcript/);
    assert.equal((await app.evaluate(() => globalThis.downloadOptions)).title, 'Save your document');
    assert.equal(await app.evaluate(({ app }) => app.getName()), 'mdeverything');
    assert.deepEqual(errors, []);
    const screen = process.env.MDE_ELECTRON_SCREENSHOT;
    if (screen) {
      await page.evaluate(() => window.scrollTo(0, 0));
      await page.waitForTimeout(3500);
      await page.screenshot({ path: path.resolve(screen) });
    }
    console.log(JSON.stringify({ result: 'passed', sandbox: true, copy: true, export: true,
      nativeSaveOptions: true, origin: new URL(page.url()).origin }));
  } finally {
    if (clipboard !== undefined) await app.evaluate(({ clipboard }, text) => clipboard.writeText(text), clipboard);
    // Playwright's close() calls app.quit(), exercising our graceful EOF shutdown handler.
    await app.close();
    fs.rmSync(data, { recursive: true, force: true });
  }
})().catch(error => { console.error(error); process.exitCode = 1; });
