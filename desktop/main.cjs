'use strict';
const { app, BrowserWindow, dialog, session, shell } = require('electron');
const { spawn, execFile } = require('node:child_process');
const { randomBytes } = require('node:crypto');
const path = require('node:path');
const readline = require('node:readline');
const { isLocalURL, externalURL, authorizeHeaders } = require('./security.cjs');

let window, engine, origin, closing = false, stopped = false;
let recentErrors = '';
const token = randomBytes(32).toString('hex');
app.setName('mdeverything');
const requestedData = app.commandLine.getSwitchValue('user-data-dir');
if (requestedData) {
  require('node:fs').mkdirSync(path.resolve(requestedData), { recursive: true });
  app.setPath('userData', path.resolve(requestedData));
}

function openExternal(url) {
  if (externalURL(url)) shell.openExternal(url).catch(() => {});
}

function forceStop() {
  if (!engine || engine.exitCode !== null) return Promise.resolve();
  if (process.platform === 'win32') {
    return new Promise(resolve => execFile(path.join(process.env.SystemRoot, 'System32', 'taskkill.exe'),
      ['/pid', String(engine.pid), '/T', '/F'], { windowsHide: true }, () => resolve()));
  }
  // Workers use process groups of their own; enumerate descendants before killing the engine.
  return new Promise(resolve => execFile('/bin/ps', ['-axo', 'pid=,ppid='], (error, stdout) => {
    const rows = (stdout || '').trim().split('\n').map(line => line.trim().split(/\s+/).map(Number));
    const descendants = [engine.pid];
    for (let index = 0; index < descendants.length; index++) {
      for (const [pid, ppid] of rows) if (ppid === descendants[index] && !descendants.includes(pid)) descendants.push(pid);
    }
    for (const pid of descendants.reverse()) {
      if (!Number.isInteger(pid) || pid <= 1) continue;
      try { process.kill(pid, 'SIGKILL'); } catch {}
    }
    resolve();
  }));
}

async function stopEngine() {
  if (!engine || engine.exitCode !== null) return;
  await new Promise(resolve => {
    const timer = setTimeout(() => { forceStop().finally(resolve); }, 12000);
    engine.once('exit', () => { clearTimeout(timer); resolve(); });
    engine.stdin.end();
  });
}

function startEngine() {
  const base = app.isPackaged ? process.resourcesPath : __dirname;
  const executable = path.join(base, app.isPackaged ? 'engine' : 'engine/mde-engine',
    process.platform === 'win32' ? 'mde-engine.exe' : 'mde-engine');
  const runtime = path.join(base, 'runtime', 'bin');
  const env = { ...process.env, MDE_DESKTOP_TOKEN: token, MDE_DATA_DIR: path.join(app.getPath('userData'), 'workspace'),
    MDE_MODEL_DIR: path.join(app.getPath('userData'), 'models'),
    PATH: runtime + path.delimiter + (process.env.PATH || ''), PYTHONIOENCODING: 'utf-8' };
  // Do not pass Electron/Node debug injection flags to the bundled external runtime.
  delete env.NODE_OPTIONS;
  engine = spawn(executable, [], { env, stdio: ['pipe', 'pipe', 'pipe'], windowsHide: true });
  engine.stdin.on('error', () => {});
  engine.stderr.on('data', chunk => { recentErrors = (recentErrors + chunk.toString()).slice(-6000); });
  return new Promise((resolve, reject) => {
    const timer = setTimeout(() => reject(new Error('The local engine did not start within 90 seconds.')), 90000);
    const lines = readline.createInterface({ input: engine.stdout });
    lines.on('line', line => {
      if (!line.startsWith('::mde-ready::')) return;
      try {
        const { port } = JSON.parse(line.slice(13));
        if (!Number.isInteger(port) || port < 1 || port > 65535) throw new Error('Invalid engine port');
        origin = `http://127.0.0.1:${port}`;
        clearTimeout(timer);
        resolve();
      } catch (error) { clearTimeout(timer); reject(error); }
    });
    engine.once('error', error => { clearTimeout(timer); reject(error); });
    engine.once('exit', code => {
      clearTimeout(timer);
      if (!origin) reject(new Error(`The local engine exited (${code}). ${recentErrors}`));
      else if (!closing) {
        dialog.showErrorBox('Workspace stopped', 'The local engine stopped unexpectedly. Reopen mdeverything to retry.');
        app.quit();
      }
    });
  });
}

if (!app.requestSingleInstanceLock()) app.quit();
else {
  app.on('second-instance', () => {
    if (window) { if (window.isMinimized()) window.restore(); window.show(); window.focus(); }
  });
  app.on('before-quit', event => {
    if (stopped) return;
    event.preventDefault();
    if (closing) return;
    closing = true;
    stopEngine().finally(() => { stopped = true; app.quit(); });
  });
  app.on('window-all-closed', () => app.quit());
  app.whenReady().then(async () => {
    const workspace = session.fromPartition('mde-workspace');
    workspace.setPermissionRequestHandler((contents, permission, callback) => callback(
      permission === 'clipboard-sanitized-write' && isLocalURL(contents.getURL(), origin)));
    workspace.setPermissionCheckHandler((_contents, permission, requestingOrigin) =>
      permission === 'clipboard-sanitized-write' && isLocalURL(requestingOrigin, origin));
    workspace.webRequest.onBeforeSendHeaders((details, callback) => callback({
      requestHeaders: authorizeHeaders(details.url, origin, token, details.requestHeaders)
    }));
    workspace.webRequest.onBeforeRequest((details, callback) => {
      const localFile = details.url === require('node:url').pathToFileURL(path.join(__dirname, 'status.html')).href;
      callback({ cancel: !localFile && !isLocalURL(details.url, origin) });
    });
    workspace.on('will-download', (_event, item) => {
      item.setSaveDialogOptions({ title: 'Save your document',
        defaultPath: path.join(app.getPath('downloads'), path.basename(item.getFilename())) });
    });
    window = new BrowserWindow({ width: 1360, height: 900, minWidth: 680, minHeight: 520,
      backgroundColor: '#f7f5ef', title: 'mdeverything', show: false,
      webPreferences: { session: workspace, sandbox: true, contextIsolation: true,
        nodeIntegration: false, webviewTag: false, spellcheck: false, devTools: !app.isPackaged } });
    window.removeMenu();
    window.once('ready-to-show', () => window.show());
    window.webContents.setWindowOpenHandler(({ url }) => { openExternal(url); return { action: 'deny' }; });
    window.webContents.on('will-navigate', (event, url) => {
      if (!isLocalURL(url, origin)) { event.preventDefault(); openExternal(url); }
    });
    window.webContents.on('will-attach-webview', event => event.preventDefault());
    window.webContents.on('render-process-gone', () => app.quit());
    await window.loadFile(path.join(__dirname, 'status.html'));
    try {
      await startEngine();
      if (!closing) await window.loadURL(origin);
    } catch (error) {
      if (!closing) dialog.showErrorBox('Could not open mdeverything',
        `${error.message}\n\nReopen the app to retry. Your saved documents remain in your local workspace.`);
      app.quit();
    }
  }).catch(error => { dialog.showErrorBox('Startup failed', error.message); app.quit(); });
}
