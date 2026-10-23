/* mdeverything · no frameworks, no remote assets, no transcript HTML. */
"use strict";

const $ = (id) => document.getElementById(id);
const TERMINAL = new Set(["done", "error", "cancelled"]);
const messages = {
  en: {
    modelSetup: "Speech models", modelIntro: "The speech engine is included in the desktop app. Download a model once; then transcribe local recordings offline. Subtitles and the demo need no model.",
    modelMissing: "Download once, use offline", modelReady: "Ready for offline transcription", modelDownloading: "Downloading", modelVerifying: "Verifying files", modelPaused: "Paused · resume available", modelError: "Download needs attention", modelDownload: "Download", modelResume: "Resume / retry", modelManage: "Manage models", modelAuto: "This model will download automatically when speech recognition is needed.", modelCaption: "Subtitles and demo work immediately.", modelBusy: "Preparing for a conversion. Cancel that job to stop.", engineMissing: "Speech engine unavailable. Reinstall the desktop app, or see the Python installation guide.", modelSize: "download", modelHint: "Tiny: quickest to try · Base: everyday use · Small and above: slower, more memory, often better accuracy.",
    brandTag: "MEDIA → MARKDOWN", newDocument: "New conversion", library: "YOUR LIBRARY", search: "Find a document…",
    localFirst: "Your files. Your machine.", localNote: "Local transcription. Open formats.", settings: "Settings & runtime",
    workspace: "Workspace", newConversion: "Media to Markdown", connecting: "Connecting", online: "Local runtime online", offline: "Runtime unavailable",
    eyebrow: "FROM MEDIA TO MEANING", heroFirst: "Less watching.", heroSecond: "More knowing.",
    description: "Turn the things you watch and listen to into words you can search, keep, and make your own.",
    pasteLink: "Paste a link", uploadFile: "Upload a file", urlLabel: "Media URLs, one per line",
    urlPlaceholder: "Drop a video or audio link here…\nOne link per line for a batch.", andMore: "& more", batchReady: "BATCH READY",
    dropFiles: "Drop your files here", browseFiles: "or click to browse your device", sourceLanguage: "SOURCE LANGUAGE",
    autoDetect: "Auto-detect", transcriptionModel: "WHISPER MODEL", addNotes: "Add AI study notes",
    notesHint: "Optional · requires local Ollama", optional: "OPTIONAL", convert: "Make it Markdown", submitting: "Adding to your library…",
    submitNote: "Readable. Searchable. Yours to keep.", justExploring: "Just exploring?", demoDescription: "See an original sample transcript.",
    tryDemo: "Try demo", flowSource: "ADD MEDIA", flowExtract: "EXTRACT WORDS", flowKeep: "KEEP THE IDEAS",
    document: "Document", read: "Read", raw: "Raw", emptyEyebrow: "A LITTLE LESS NOISE.", emptyTitle: "A place for the good parts.",
    emptyDescription: "Your media becomes a clean, timestamped document. Ready for your notes, your tools, your next idea.",
    waitingSource: "Waiting for your first source", copy: "Copy", exportFormat: "Export format", download: "Download",
    preferences: "PREFERENCES", settingsDescription: "Processing runs on this machine. Your selected language, model, and notes preference are saved in this browser.",
    howItWorks: "A few things to know", runtimeInfo: "Existing subtitles are used when available. Audio transcription uses local Whisper; the first run may download model weights. Larger models need more memory and time.",
    networkInfo: "Online sources need a network connection and support varies by site. Optional study notes are generated through your local Ollama service.",
    done: "Done", libraryEmpty: "A little library of your ideas. Add a link or a file to begin.", noResults: "No matching documents.",
    queued: "Queued", running: "Processing", error: "Failed", cancelled: "Cancelled", completed: "Ready", cancel: "Cancel", retry: "Retry", remove: "Delete",
    confirmDelete: "Delete this job and its saved files? This cannot be undone.", noInput: "Add at least one media link to continue.",
    invalidUrl: "Use complete http:// or https:// links, one per line.", noFiles: "Choose a video, audio, or subtitle file first.",
    copied: "Markdown copied.", copyFailed: "Clipboard access is unavailable. Download the Markdown file instead.",
    networkError: "Cannot reach the local server. Check that mdeverything is running.", requestFailed: "The request could not be completed.",
    added: "Added to your library.", fileAdded: "Files selected. Ready to convert.", removed: "Document deleted.",
    waitingTitle: "Good words take a moment.", waitingDescription: "Your source is being processed on this machine. You can add more media while you wait.",
    queuedDescription: "Your source is in the queue. Processing will begin when a worker is available.",
    errorTitle: "This one needs another look.", errorDescription: "Check the error below, then retry when the source or runtime is ready.",
    cancelledTitle: "Conversion cancelled.", cancelledDescription: "You can retry this source whenever you are ready.",
    loadingTitle: "Opening your document…", loadingDescription: "Reading the saved Markdown from your local library.",
    documentError: "Could not open this document.", segments: "segments", duration: "Duration", available: "Available", unavailable: "Not installed / unavailable",
    dataDirectory: "Data directory", checking: "Checking…", untitled: "Untitled source", pending: "Pending", retryDocument: "Try opening again",
    stageQueued: "Waiting in queue", stageStarting: "Preparing source", stageInspecting: "Inspecting source", stageDownloading: "Downloading media",
    stageSubtitles: "Reading subtitles", stageTranscribing: "Transcribing audio", stageNotes: "Generating local study notes", stageExporting: "Saving document",
    stageDone: "Document ready", stageCancelled: "Conversion cancelled", stageError: "Conversion failed", close: "Close", removeFile: "Remove file"
  },
  zh: {
    modelSetup: "语音模型", modelIntro: "桌面版已内置语音引擎。模型只需下载一次，之后本地录音可离线转录。字幕和演示不需要模型。",
    modelMissing: "下载一次，离线使用", modelReady: "已就绪 · 可离线转录", modelDownloading: "正在下载", modelVerifying: "正在校验文件", modelPaused: "已暂停 · 可继续下载", modelError: "下载需要处理", modelDownload: "下载模型", modelResume: "继续 / 重试", modelManage: "管理模型", modelAuto: "需要语音识别时，将自动下载所选模型。", modelCaption: "字幕和演示可以直接使用。", modelBusy: "转换任务正在准备模型，如需停止请取消该任务。", engineMissing: "语音引擎不可用，请重新安装桌面版，或查看 Python 版安装指南。", modelSize: "下载量", modelHint: "Tiny：快速体验 · Base：日常使用 · Small 及以上：通常更准确，但更慢、占用更多内存。",
    brandTag: "媒体 → MARKDOWN", newDocument: "新建转换", library: "我的文档库", search: "搜索文档…",
    localFirst: "你的文件，你的电脑。", localNote: "本地转录，开放格式。", settings: "设置与运行环境", workspace: "工作区", newConversion: "媒体转 Markdown",
    connecting: "正在连接", online: "本地服务已连接", offline: "本地服务未连接", eyebrow: "让信息，成为你的知识", heroFirst: "少一点观看。", heroSecond: "多一点洞见。",
    description: "把你看过、听过的内容，变成可以搜索、保存和重新思考的文字。", pasteLink: "粘贴链接", uploadFile: "上传文件",
    urlLabel: "媒体链接，每行一个", urlPlaceholder: "在这里粘贴视频或音频链接…\n每行一个，支持批量转换。", andMore: "等更多来源", batchReady: "支持批量",
    dropFiles: "将文件拖放到这里", browseFiles: "或点击选择电脑中的文件", sourceLanguage: "原始语言", autoDetect: "自动识别", transcriptionModel: "WHISPER 模型",
    addNotes: "生成 AI 学习笔记", notesHint: "可选 · 需要本地 Ollama", optional: "可选", convert: "转换为 Markdown", submitting: "正在添加到文档库…",
    submitNote: "方便阅读，随时搜索，自由保存。", justExploring: "先体验一下？", demoDescription: "看看原创示例转录的效果。", tryDemo: "体验演示",
    flowSource: "添加媒体", flowExtract: "提取文字", flowKeep: "留下好想法", document: "文档", read: "阅读", raw: "源码",
    emptyEyebrow: "让噪音少一点。", emptyTitle: "给好内容，一个去处。", emptyDescription: "媒体将变成清晰、带时间戳的文档。放进笔记，接入工具，开启下一个想法。",
    waitingSource: "等待你的第一个素材", copy: "复制", exportFormat: "导出格式", download: "下载", preferences: "偏好设置",
    settingsDescription: "内容在这台电脑上处理。所选语言、模型和笔记偏好会保存在当前浏览器中。", howItWorks: "使用说明",
    runtimeInfo: "优先使用已有字幕。音频转录通过本地 Whisper 完成，首次运行可能需要下载模型。更大的模型需要更多内存与处理时间。",
    networkInfo: "在线素材需要网络连接，不同网站的支持情况可能不同。可选的学习笔记由你的本地 Ollama 服务生成。",
    done: "完成", libraryEmpty: "为你的想法留一个位置。添加链接或文件，开始第一份文档。", noResults: "没有匹配的文档。",
    queued: "排队中", running: "处理中", error: "失败", cancelled: "已取消", completed: "已完成", cancel: "取消", retry: "重试", remove: "删除",
    confirmDelete: "删除这个任务及其已保存的文件？此操作无法撤销。", noInput: "请先添加至少一个媒体链接。", invalidUrl: "请使用完整的 http:// 或 https:// 链接，每行一个。",
    noFiles: "请先选择视频、音频或字幕文件。", copied: "已复制 Markdown。", copyFailed: "无法访问剪贴板，请下载 Markdown 文件。",
    networkError: "无法连接本地服务，请确认 mdeverything 正在运行。", requestFailed: "请求未能完成。", added: "已添加到文档库。", fileAdded: "文件已选择，可以开始转换。", removed: "文档已删除。",
    waitingTitle: "好内容，值得等一会。", waitingDescription: "正在这台电脑上处理素材。等待时，你可以继续添加其他内容。", queuedDescription: "素材正在排队，将在工作进程空闲后开始处理。",
    errorTitle: "这次转换需要检查一下。", errorDescription: "查看下方错误，确认素材或运行环境就绪后重试。", cancelledTitle: "转换已取消。", cancelledDescription: "准备好后，可以随时重试这份素材。",
    loadingTitle: "正在打开文档…", loadingDescription: "正在从本地文档库读取已保存的 Markdown。", documentError: "无法打开这份文档。", segments: "段字幕", duration: "时长",
    available: "可用", unavailable: "未安装或暂不可用", dataDirectory: "数据目录", checking: "检查中…", untitled: "未命名素材", pending: "等待中", retryDocument: "重新打开",
    stageQueued: "等待处理", stageStarting: "准备素材", stageInspecting: "检查素材", stageDownloading: "下载媒体", stageSubtitles: "读取字幕", stageTranscribing: "转录音频",
    stageNotes: "生成本地学习笔记", stageExporting: "保存文档", stageDone: "文档已就绪", stageCancelled: "转换已取消", stageError: "转换失败", close: "关闭", removeFile: "移除文件"
  }
};

function loadPreferences() {
  try { return JSON.parse(localStorage.getItem("mdeverything.preferences") || "{}") || {}; }
  catch (_) { return {}; }
}
const preferences = loadPreferences();
const state = { locale: preferences.locale === "zh" ? "zh" : "en", mode: "url", files: [], jobs: [], selected: null,
  document: null, documentId: null, raw: false, submitting: false, health: null, models: [], fetchingModels: false, preferencesLoaded: false, preferencesLoading: false, preferenceRevision: 0, preferenceBaseline: 0, modelSignature: "", connected: false, fetchingJobs: false, readerRequest: 0, jobsRevision: 0 };
const initialEmptyReader = $("reader-content").firstElementChild.cloneNode(true);
let toastTimer;
let preferenceWrites = Promise.resolve();
const t = (key) => messages[state.locale][key] || messages.en[key] || key;
function element(tag, className, text) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text !== undefined) node.textContent = text;
  return node;
}
function savePreferences() {
  state.preferenceRevision++;
  try { localStorage.setItem("mdeverything.preferences", JSON.stringify({ locale: state.locale, language: $("language").value, model: $("model").value, notes: $("notes").checked })); }
  catch (_) { /* Private browsing may disable persistence. */ }
  if (state.health?.desktop && state.preferencesLoaded) {
    const body = JSON.stringify({locale: state.locale, language: $("language").value, model: $("model").value, notes: $("notes").checked});
    preferenceWrites = preferenceWrites.then(() => api("/api/preferences", {method: "PUT", body})).catch(() => {});
  }
}
function toast(message, error = false) {
  clearTimeout(toastTimer);
  $("toast").textContent = message;
  $("toast").classList.toggle("error", error);
  $("toast").hidden = false;
  toastTimer = setTimeout(() => { $("toast").hidden = true; }, error ? 7000 : 3300);
}
async function api(path, options = {}) {
  const headers = { ...options.headers };
  if (options.method && options.method !== "GET") headers["X-MDE-Client"] = "web";
  if (options.body && !(options.body instanceof FormData)) headers["Content-Type"] = "application/json";
  let response;
  try { response = await fetch(path, { ...options, headers }); }
  catch (_) { throw new Error(t("networkError")); }
  if (!response.ok) {
    let message = `${t("requestFailed")} (${response.status})`;
    try {
      const error = await response.json();
      if (typeof error.detail === "string") message = error.detail;
      else if (typeof error.error === "string") message = error.error;
      else if (Array.isArray(error.detail)) message = error.detail.map((item) => item.msg).filter(Boolean).join("; ") || message;
    } catch (_) { /* An HTTP error can have a non-JSON response. */ }
    throw new Error(message);
  }
  return response.json();
}
function statusText(job) { return t(job.status === "done" ? "completed" : job.status); }
function stageText(job) {
  const chineseStages = {
    "Waiting in queue": "等待处理", "Starting conversion": "开始转换", "Ready to read": "文档已就绪", "Failed": "转换失败", "Cancelled": "转换已取消", "Interrupted": "转换意外中断",
    "Loading local speech model": "加载本地语音模型", "Waiting for speech model download": "等待语音模型下载",
    "Loading local speech model (first use may download weights)": "加载本地语音模型（首次使用可能需要下载）",
    "Transcribing on your device": "正在本地转录音频", "Reading source and looking for captions": "检查素材与可用字幕",
    "Using existing captions — no speech model needed": "使用已有字幕，无需语音模型", "Downloading audio for local transcription": "下载音频以进行本地转录",
    "Downloading audio": "下载音频", "Reading subtitle file": "读取字幕文件", "Writing notes with your local model": "通过本地模型生成笔记", "Exporting your document": "导出文档"
  };
  if (state.locale === "zh" && /^(Downloading|Verifying) speech model/.test(job.stage || "")) return job.stage.replace("Downloading speech model", "下载语音模型").replace("Verifying speech model", "校验语音模型");
  if (state.locale === "zh" && chineseStages[job.stage]) return chineseStages[job.stage];
  const key = { queued: "stageQueued", starting: "stageStarting", inspecting: "stageInspecting", downloading: "stageDownloading",
    subtitles: "stageSubtitles", transcribing: "stageTranscribing", notes: "stageNotes", exporting: "stageExporting", done: "stageDone", cancelled: "stageCancelled", error: "stageError" }[job.stage];
  return key ? t(key) : (job.stage || statusText(job));
}
function currentJob() { return state.jobs.find((job) => job.id === state.selected); }
function titleFor(job) { return job.title || job.source || t("untitled"); }
function formatDate(value) {
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? "" : date.toLocaleDateString(state.locale === "zh" ? "zh-CN" : "en-US", { month: "short", day: "numeric" });
}
function formatDuration(seconds) {
  const total = Math.max(0, Math.floor(Number(seconds) || 0));
  return `${Math.floor(total / 60)}:${String(total % 60).padStart(2, "0")}`;
}
function translate(root = document) {
  root.querySelectorAll("[data-i18n]").forEach((node) => { node.textContent = t(node.dataset.i18n); });
  root.querySelectorAll("[data-placeholder]").forEach((node) => { node.placeholder = t(node.dataset.placeholder); });
  root.querySelectorAll("[data-i18n-aria]").forEach((node) => { node.setAttribute("aria-label", t(node.dataset.i18nAria)); });
}
function setLocale(locale) {
  state.locale = locale;
  document.documentElement.lang = locale === "zh" ? "zh-CN" : "en";
  translate();
  $("locale-toggle").replaceChildren(document.createTextNode(locale === "zh" ? "中 " : "EN "), element("span", "", locale === "zh" ? "/ EN" : "/ 中"));
  $("locale-toggle").setAttribute("aria-label", locale === "zh" ? "Switch to English" : "切换为中文");
  $("settings-close").setAttribute("aria-label", t("close"));
  renderHealth(); renderModels(true); renderLibrary(); renderActiveJob(); renderFiles();
  if (state.document) renderDocument();
  else renderReaderState();
  if (state.submitting) $("convert-button").firstElementChild.textContent = t("submitting");
  savePreferences();
}
function renderHealth() {
  const status = $("health-status");
  status.className = `health-status ${state.connected ? "online" : "offline"}`;
  status.replaceChildren(element("i"), element("span", "", t(state.connected ? "online" : "offline")));
  $("version").textContent = state.health?.version ? `v${state.health.version.replace(/^v/, "")}` : "v—";
  const rows = [["FFmpeg", state.health?.ffmpeg], ["Whisper engine", state.health?.whisper], ["Ollama", state.health?.ollama]];
  $("runtime-details").replaceChildren(...rows.map(([label, value]) => {
    const row = element("div", "runtime-row");
    row.append(element("span", "", label), element("span", "", state.health ? t(value ? "available" : "unavailable") : t("offline")));
    return row;
  }));
  if (state.health?.data_dir) {
    const row = element("div", "runtime-row path-row");
    row.append(element("span", "", t("dataDirectory")), element("span", "", state.health.data_dir));
    $("runtime-details").append(row);
  }
}
async function refreshHealth() {
  try {
    state.health = await api("/api/health"); state.connected = true;
    if (state.health.desktop && !state.preferencesLoaded && !state.preferencesLoading) {
      state.preferencesLoading = true;
      const revision = state.preferenceBaseline;
      try {
        const saved = await api("/api/preferences");
        if (revision === state.preferenceRevision) {
          if (["en", "zh"].includes(saved.locale)) state.locale = saved.locale;
          for (const key of ["model", "language"]) if (Array.from($(key).options).some((o) => o.value === saved[key])) $(key).value = saved[key];
          $("notes").checked = saved.notes === true;
          setLocale(state.locale);
          state.preferencesLoaded = true;
        } else {
          state.preferencesLoaded = true;
          savePreferences(); // Preserve an edit made while the initial GET was in flight.
        }
      } catch (_) { /* Retry settings initialization on the next health refresh. */ }
      finally { state.preferencesLoading = false; }
    }
  }
  catch (_) { state.connected = false; }
  renderHealth();
  renderModels();
}
function renderLibrary() {
  const query = $("search").value.trim().toLocaleLowerCase();
  const jobs = state.jobs.filter((job) => `${titleFor(job)} ${job.source || ""}`.toLocaleLowerCase().includes(query));
  $("job-count").textContent = String(state.jobs.length);
  if (!jobs.length) { $("job-list").replaceChildren(element("p", `library-empty${query ? " search-empty" : ""}`, t(query ? "noResults" : "libraryEmpty"))); return; }
  $("job-list").replaceChildren(...jobs.map((job) => {
    const item = element("div", `job-item${job.id === state.selected ? " selected" : ""}`);
    const button = element("button", "job-select");
    button.type = "button";
    button.title = titleFor(job);
    button.setAttribute("aria-current", job.id === state.selected ? "true" : "false");
    button.append(element("span", "job-symbol", job.status === "done" ? "≡" : job.status === "error" ? "!" : job.status === "cancelled" ? "−" : "◌"));
    const details = element("span", "job-details");
    details.append(element("strong", "", titleFor(job)));
    const meta = element("span", "job-meta");
    meta.append(element("span", job.status, statusText(job)), element("span", "", "·"), element("span", "", formatDate(job.created_at)));
    details.append(meta); button.append(details); item.append(button);
    button.addEventListener("click", () => selectJob(job.id));
    return item;
  }));
}
function renderActiveJob() {
  const job = currentJob();
  const box = $("active-job");
  box.hidden = !job;
  if (!job) return;
  const top = element("div", "active-job-top");
  top.append(element("h3", "", titleFor(job)), element("span", "job-status", statusText(job)));
  box.replaceChildren(top);
  if (!TERMINAL.has(job.status)) {
    const progress = Math.max(0, Math.min(100, Number(job.progress) || 0));
    const track = element("div", "progress-track");
    track.setAttribute("role", "progressbar"); track.setAttribute("aria-label", stageText(job));
    track.setAttribute("aria-valuenow", String(progress)); track.setAttribute("aria-valuemin", "0"); track.setAttribute("aria-valuemax", "100");
    const fill = element("div", "progress-fill"); fill.style.width = `${progress}%`; track.append(fill);
    box.append(track, element("p", "", `${stageText(job)} · ${progress}%`));
  } else { box.append(element("p", "", job.error || stageText(job))); }
  const actions = element("div", "job-controls");
  if (!TERMINAL.has(job.status)) actions.append(actionButton(t("cancel"), () => mutateJob(job, "cancel")));
  if (TERMINAL.has(job.status)) actions.append(actionButton(t("retry"), () => mutateJob(job, "retry")));
  if (TERMINAL.has(job.status)) actions.append(actionButton(t("remove"), () => deleteJob(job), "danger"));
  box.append(actions);
}
function actionButton(label, action, className = "") {
  const button = element("button", className, label); button.type = "button";
  button.addEventListener("click", async () => {
    button.disabled = true;
    try { await action(); } catch (error) { toast(error.message, true); }
    finally { button.disabled = false; }
  });
  return button;
}
function renderReaderState() {
  const job = currentJob();
  $("view-switch").hidden = true; $("document-actions").hidden = true; $("empty-export").hidden = !!job;
  $("reader-heading").textContent = t("document");
  $("reader-status").textContent = job ? statusText(job) : t("waitingSource");
  if (!job) {
    const empty = initialEmptyReader.cloneNode(true); translate(empty); $("reader-content").replaceChildren(empty); return;
  }
  const box = element("div", "reader-message");
  const titleKey = job.status === "error" ? "errorTitle" : job.status === "cancelled" ? "cancelledTitle" : job.status === "done" ? "loadingTitle" : "waitingTitle";
  const descriptionKey = job.status === "error" ? "errorDescription" : job.status === "cancelled" ? "cancelledDescription" : job.status === "done" ? "loadingDescription" : job.status === "queued" ? "queuedDescription" : "waitingDescription";
  box.append(element("span", "message-symbol", job.status === "error" ? "!" : "✳"), element("strong", "", t(titleKey)), element("p", "", t(descriptionKey)));
  if (job.error) box.append(element("p", "message-error", job.error));
  $("reader-content").replaceChildren(box);
}
async function selectJob(id) {
  const changed = state.selected !== id;
  state.selected = id;
  if (changed) { state.document = null; state.documentId = null; state.raw = false; state.readerRequest++; }
  renderLibrary(); renderActiveJob();
  const job = currentJob();
  if (state.document && state.documentId === id) { renderDocument(); return; }
  renderReaderState();
  if (job?.status === "done") await loadDocument(id);
}
async function loadDocument(id) {
  const request = ++state.readerRequest;
  try {
    const result = await api(`/api/jobs/${encodeURIComponent(id)}/document`);
    if (state.selected !== id || state.readerRequest !== request) return;
    state.document = result; state.documentId = id; renderDocument();
  } catch (error) {
    if (state.selected !== id || state.readerRequest !== request) return;
    const box = element("div", "reader-message");
    box.append(element("strong", "", t("documentError")), element("p", "message-error", error.message), actionButton(t("retryDocument"), () => loadDocument(id)));
    $("reader-content").replaceChildren(box);
  }
}
/* Build a small Markdown subset using text nodes only. Raw HTML is always literal text. */
function decodeText(value) {
  const named = { amp: "&", lt: "<", gt: ">", quot: '"', apos: "'" };
  return value.replace(/&(amp|lt|gt|quot|apos|#\d+|#x[\da-f]+);/gi, (entity, code) => {
    if (!code.startsWith("#")) return named[code.toLowerCase()];
    const point = code[1].toLowerCase() === "x" ? parseInt(code.slice(2), 16) : parseInt(code.slice(1), 10);
    return point > 0 && point <= 0x10ffff && !(point >= 0xd800 && point <= 0xdfff) ? String.fromCodePoint(point) : "\ufffd";
  });
}
function appendInline(parent, value, depth = 0) {
  if (depth > 8) { parent.append(document.createTextNode(decodeText(value))); return; }
  const pattern = /(\\[\\`*_{}\[\]()#+\-.!>|~]|`[^`\n]+`|\*\*[^*\n]+\*\*|\[[^\]\n]+\]\([^\s)]+\))/g;
  let start = 0;
  for (const match of value.matchAll(pattern)) {
    parent.append(document.createTextNode(decodeText(value.slice(start, match.index))));
    const token = match[0];
    if (token.startsWith("\\")) parent.append(document.createTextNode(token.slice(1)));
    else if (token.startsWith("`")) parent.append(element("code", "", token.slice(1, -1)));
    else if (token.startsWith("**")) {
      const strong = element("strong"); appendInline(strong, token.slice(2, -2), depth + 1); parent.append(strong);
    }
    else {
      const split = token.indexOf("](");
      const label = token.slice(1, split), target = token.slice(split + 2, -1);
      try {
        const url = new URL(decodeText(target));
        if (!["http:", "https:"].includes(url.protocol)) throw new Error("Unsupported link protocol");
        const link = element("a", "", decodeText(label)); link.href = url.href; link.target = "_blank"; link.rel = "noopener noreferrer"; parent.append(link);
      } catch (_) { parent.append(document.createTextNode(decodeText(token))); }
    }
    start = match.index + token.length;
  }
  parent.append(document.createTextNode(decodeText(value.slice(start))));
}
function renderMarkdown(markdown) {
  const article = element("article", "document-body");
  let paragraph = [], list = null, code = null;
  const flush = () => { if (paragraph.length) { const p = element("p"); appendInline(p, paragraph.join(" ")); article.append(p); paragraph = []; } };
  const readableMarkdown = String(markdown || "").replace(/\r\n/g, "\n").replace(/^---\n[\s\S]*?\n---\n/, "");
  for (const line of readableMarkdown.split("\n")) {
    if (/^\s*```/.test(line)) {
      flush(); list = null;
      if (code) code = null;
      else { const pre = element("pre"); code = element("code"); pre.append(code); article.append(pre); }
      continue;
    }
    if (code) { code.append(document.createTextNode(`${line}\n`)); continue; }
    if (!line.trim()) { flush(); list = null; continue; }
    const heading = /^(#{1,6})\s+(.+)$/.exec(line);
    if (heading) { flush(); list = null; const h = element(`h${heading[1].length}`); appendInline(h, heading[2]); article.append(h); continue; }
    if (/^\s*([-*_])(?:\s*\1){2,}\s*$/.test(line)) { flush(); list = null; article.append(element("hr")); continue; }
    const item = /^\s*(?:([-+*])|\d+[.)])\s+(.+)$/.exec(line);
    if (item) {
      flush(); const tag = item[1] ? "UL" : "OL";
      if (!list || list.tagName !== tag) { list = element(tag.toLowerCase()); article.append(list); }
      const li = element("li"); appendInline(li, item[2]); list.append(li); continue;
    }
    list = null;
    if (/^>\s?/.test(line)) { flush(); const quote = element("blockquote"); appendInline(quote, line.replace(/^>\s?/, "")); article.append(quote); continue; }
    paragraph.push(line);
  }
  flush(); return article;
}
function renderDocument() {
  if (!state.document) return;
  const { markdown, document: doc } = state.document;
  const content = state.raw ? element("pre", "document-body raw", markdown || "") : renderMarkdown(markdown);
  $("reader-content").replaceChildren(content);
  $("view-switch").hidden = false; $("document-actions").hidden = false; $("empty-export").hidden = true;
  $("read-view").classList.toggle("active", !state.raw); $("raw-view").classList.toggle("active", state.raw);
  $("read-view").setAttribute("aria-pressed", String(!state.raw)); $("raw-view").setAttribute("aria-pressed", String(state.raw));
  $("reader-heading").textContent = t("document");
  $("reader-status").textContent = `${doc?.segments?.length || 0} ${t("segments")} · ${formatDuration(doc?.duration)}`;
}
async function refreshJobs() {
  if (state.fetchingJobs) return;
  state.fetchingJobs = true;
  const revision = state.jobsRevision;
  try {
    const previous = currentJob();
    const result = await api("/api/jobs");
    if (revision !== state.jobsRevision) return;
    const nextJobs = (result.jobs || []).sort((a, b) => String(b.created_at).localeCompare(String(a.created_at)));
    const changed = JSON.stringify(nextJobs) !== JSON.stringify(state.jobs);
    state.jobs = nextJobs;
    if (changed) { renderLibrary(); renderActiveJob(); }
    const job = currentJob();
    if (state.selected && !job) { state.selected = null; state.document = null; state.documentId = null; state.readerRequest++; renderReaderState(); }
    else if (job && previous?.status !== job.status) {
      if (job.status === "done") await loadDocument(job.id);
      else if (!state.document) renderReaderState();
    }
  } catch (_) { /* Health indicator reports an unavailable runtime without repetitive toasts. */ }
  finally { state.fetchingJobs = false; }
}
function mergeJobs(jobs) {
  state.jobsRevision++;
  const updates = new Map(state.jobs.map((job) => [job.id, job]));
  jobs.forEach((job) => updates.set(job.id, job));
  state.jobs = [...updates.values()].sort((a, b) => String(b.created_at).localeCompare(String(a.created_at)));
  renderLibrary();
}
async function mutateJob(job, action) {
  const result = await api(`/api/jobs/${encodeURIComponent(job.id)}/${action}`, { method: "POST" });
  mergeJobs([result]);
  if (state.selected === job.id) await selectJob(result.id);
}
async function deleteJob(job) {
  if (!window.confirm(t("confirmDelete"))) return;
  await api(`/api/jobs/${encodeURIComponent(job.id)}`, { method: "DELETE" });
  state.jobsRevision++;
  state.jobs = state.jobs.filter((item) => item.id !== job.id);
  if (state.selected === job.id) {
    state.selected = null; state.document = null; state.documentId = null; state.readerRequest++; renderReaderState();
  }
  renderLibrary(); renderActiveJob(); toast(t("removed"));
}
function setMode(mode) {
  state.mode = mode;
  ["url", "file"].forEach((name) => {
    const active = mode === name;
    $(`${name}-tab`).classList.toggle("active", active); $(`${name}-tab`).setAttribute("aria-selected", String(active));
    $(`${name}-tab`).tabIndex = active ? 0 : -1; $(`${name}-panel`).hidden = !active;
  });
}
function renderFiles() {
  $("file-selection").replaceChildren(...state.files.map((file, index) => {
    const row = element("div", "selected-file");
    row.append(element("span", "", `${file.name} · ${(file.size / (1024 * 1024)).toFixed(1)} MB`));
    const remove = actionButton("×", () => { state.files.splice(index, 1); renderFiles(); });
    remove.setAttribute("aria-label", `${t("removeFile")}: ${file.name}`); row.append(remove); return row;
  }));
}
function addFiles(files) {
  state.files.push(...Array.from(files)); renderFiles();
  $("files").value = "";
}
async function submitConversion(event) {
  event?.preventDefault();
  if (state.submitting) return;
  const urls = $("urls").value.split(/\r?\n/).map((url) => url.trim()).filter(Boolean);
  if (state.mode === "url") {
    if (!urls.length) { toast(t("noInput"), true); $("urls").focus(); return; }
    try { urls.forEach((value) => { if (!["http:", "https:"].includes(new URL(value).protocol)) throw new Error(); }); }
    catch (_) { toast(t("invalidUrl"), true); return; }
  } else if (!state.files.length) { toast(t("noFiles"), true); return; }
  state.submitting = true; $("convert-button").disabled = true; $("convert-button").firstElementChild.textContent = t("submitting");
  const options = { language: $("language").value, model: $("model").value, notes: $("notes").checked };
  savePreferences();
  try {
    if (state.mode === "url") {
      const result = await api("/api/jobs", { method: "POST", body: JSON.stringify({ urls, ...options }) });
      mergeJobs(result.jobs || []); if (result.jobs?.length) await selectJob(result.jobs[0].id);
      $("urls").value = "";
    } else {
      // Upload sequentially; successful files are removed so a later failure cannot duplicate them.
      const pending = [...state.files];
      for (const file of pending) {
        const body = new FormData(); body.append("file", file);
        Object.entries(options).forEach(([key, value]) => body.append(key, String(value)));
        const job = await api("/api/upload", { method: "POST", body });
        mergeJobs([job]); await selectJob(job.id);
        state.files = state.files.filter((item) => item !== file); renderFiles();
      }
    }
    toast(t("added"));
  } catch (error) { toast(error.message, true); }
  finally { state.submitting = false; $("convert-button").disabled = false; $("convert-button").firstElementChild.textContent = t("convert"); }
}

$("conversion-form").addEventListener("submit", submitConversion);
$("url-tab").addEventListener("click", () => setMode("url"));
$("file-tab").addEventListener("click", () => setMode("file"));
document.querySelector(".source-tabs").addEventListener("keydown", (event) => {
  if (["ArrowRight", "ArrowLeft", "Home", "End"].includes(event.key)) {
    event.preventDefault(); setMode(event.key === "Home" ? "url" : event.key === "End" ? "file" : state.mode === "url" ? "file" : "url"); $(`${state.mode}-tab`).focus();
  }
});
$("locale-toggle").addEventListener("click", () => setLocale(state.locale === "en" ? "zh" : "en"));
$("search").addEventListener("input", renderLibrary);
$("files").addEventListener("change", (event) => addFiles(event.target.files));
$("dropzone").addEventListener("keydown", (event) => { if (event.key === "Enter" || event.key === " ") { event.preventDefault(); $("files").click(); } });
["dragenter", "dragover"].forEach((name) => $("dropzone").addEventListener(name, (event) => { event.preventDefault(); $("dropzone").classList.add("dragging"); }));
["dragleave", "drop"].forEach((name) => $("dropzone").addEventListener(name, (event) => { event.preventDefault(); $("dropzone").classList.remove("dragging"); }));
$("dropzone").addEventListener("drop", (event) => { addFiles(event.dataTransfer.files); });
["language", "model", "notes"].forEach((id) => $(id).addEventListener("change", () => { savePreferences(); renderModels(true); }));
$("read-view").addEventListener("click", () => { state.raw = false; renderDocument(); });
$("raw-view").addEventListener("click", () => { state.raw = true; renderDocument(); });
$("copy-button").addEventListener("click", async () => {
  if (!state.document) return;
  try { await navigator.clipboard.writeText(state.document.markdown); toast(t("copied")); }
  catch (_) { toast(t("copyFailed"), true); }
});
$("download-button").addEventListener("click", () => {
  if (!state.documentId) return;
  const link = document.createElement("a"); link.href = `/api/jobs/${encodeURIComponent(state.documentId)}/download?format=${encodeURIComponent($("export-format").value)}`;
  link.download = ""; document.body.append(link); link.click(); link.remove();
});
$("demo-button").addEventListener("click", async () => {
  $("demo-button").disabled = true;
  try { const job = await api("/api/demo", { method: "POST" }); mergeJobs([job]); await selectJob(job.id); toast(t("added")); }
  catch (error) { toast(error.message, true); }
  finally { $("demo-button").disabled = false; }
});
$("new-document").addEventListener("click", () => {
  state.selected = null; state.document = null; state.documentId = null; state.raw = false; state.readerRequest++;
  renderLibrary(); renderActiveJob(); renderReaderState();
  $("conversion-form").scrollIntoView({ behavior: "smooth", block: "center" });
  if (state.mode === "url") $("urls").focus({ preventScroll: true });
});
function openSettings() { if (!$("settings-dialog").open) $("settings-dialog").showModal(); refreshHealth(); refreshModels(); }
$("settings-open").addEventListener("click", openSettings);
$("health-status").addEventListener("click", openSettings);
$("health-status").setAttribute("role", "button"); $("health-status").tabIndex = 0;
$("health-status").addEventListener("keydown", (event) => { if (event.key === "Enter" || event.key === " ") { event.preventDefault(); openSettings(); } });
$("settings-close").addEventListener("click", () => $("settings-dialog").close());
$("settings-done").addEventListener("click", () => $("settings-dialog").close());
$("settings-dialog").addEventListener("click", (event) => {
  if (event.target === $("settings-dialog")) { const r = $("settings-dialog").getBoundingClientRect(); if (event.clientX < r.left || event.clientX > r.right || event.clientY < r.top || event.clientY > r.bottom) $("settings-dialog").close(); }
});
document.addEventListener("keydown", (event) => {
  if ((event.metaKey || event.ctrlKey) && event.key === "Enter" && !$("settings-dialog").open) { event.preventDefault(); submitConversion(); }
  if (event.key === "/" && !["INPUT", "TEXTAREA", "SELECT"].includes(document.activeElement.tagName) && !$("settings-dialog").open) { event.preventDefault(); $("search").focus(); }
});
if (preferences.language && Array.from($("language").options).some((item) => item.value === preferences.language)) $("language").value = preferences.language;
if (preferences.model && Array.from($("model").options).some((item) => item.value === preferences.model)) $("model").value = preferences.model;
$("notes").checked = preferences.notes === true;
if (!/Mac|iPhone|iPad/.test(navigator.platform)) { $("shortcut-hint").textContent = "Ctrl Enter"; document.querySelector(".new-button kbd").textContent = "Ctrl ↵"; }
setMode("url"); setLocale(state.locale);
state.preferenceBaseline = state.preferenceRevision;
refreshHealth(); refreshJobs(); refreshModels();
setInterval(() => { if (!document.hidden) refreshJobs(); }, 2500);
setInterval(() => { if (!document.hidden) refreshHealth(); }, 30000);
document.addEventListener("visibilitychange", () => { if (!document.hidden) { refreshJobs(); refreshHealth(); } });


function modelStatusText(model) {
  return t({ready: "modelReady", downloading: "modelDownloading", verifying: "modelVerifying", paused: "modelPaused", error: "modelError"}[model.status] || "modelMissing");
}
function modelBytes(bytes) { return bytes >= 1024 ** 3 ? `${(bytes / 1024 ** 3).toFixed(2)} GiB` : `${(bytes / 1024 ** 2).toFixed(1)} MiB`; }
function renderModels(force = false) {
  const signature = JSON.stringify([state.models, state.locale, state.health?.whisper, $("model").value]);
  if (!force && state.modelSignature === signature) return;
  state.modelSignature = signature;
  const selected = state.models.find((model) => model.name === $("model").value);
  const banner = $("model-setup-status");
  banner.replaceChildren();
  banner.append(element("strong", "", selected ? `${selected.name.toUpperCase()} · ${modelStatusText(selected)}` : t("checking")));
  banner.append(element("span", "", state.health && !state.health.whisper ? t("engineMissing") : selected?.status === "ready" ? t("modelCaption") : t("modelAuto")));
  if (selected && ["downloading", "verifying"].includes(selected.status)) {
    banner.append(element("span", "model-byte-count", `${modelBytes(selected.downloaded_bytes)} / ${modelBytes(selected.total_bytes)}`));
  }
  $("model-list").replaceChildren(...state.models.map((model) => {
    const row = element("div", "model-card"); row.dataset.model = model.name;
    const header = element("div", "model-card-heading");
    header.append(element("strong", "", model.name.toUpperCase()), element("span", "", `${modelBytes(model.total_bytes)} ${t("modelSize")}`));
    const status = element("p", "model-status", modelStatusText(model));
    row.append(header, status);
    if (["downloading", "verifying"].includes(model.status)) {
      const progress = element("progress"); progress.max = model.total_bytes; progress.value = model.downloaded_bytes;
      progress.setAttribute("aria-label", modelStatusText(model));
      row.append(progress, element("span", "model-byte-count", `${modelBytes(model.downloaded_bytes)} / ${modelBytes(model.total_bytes)}`));
      if (!model.can_cancel) row.append(element("small", "", t("modelBusy")));
    }
    if (model.error) row.append(element("p", "model-error", model.error));
    if (model.status !== "ready") {
      const active = ["downloading", "verifying"].includes(model.status);
      if (!active || model.can_cancel) {
        const button = element("button", "model-action", t(active ? "cancel" : ["error", "paused"].includes(model.status) ? "modelResume" : "modelDownload"));
        button.type = "button"; button.disabled = !state.health?.whisper;
        button.addEventListener("click", async () => {
          button.disabled = true;
          try {
            const result = await api(`/api/models/${encodeURIComponent(model.name)}/${active ? "cancel" : "download"}`, {method: "POST"});
            state.models = state.models.map((m) => m.name === model.name ? result : m);
            renderModels(true);
          } catch (error) { toast(error.message, true); button.disabled = false; }
        });
        row.append(button);
      }
    }
    return row;
  }));
}
async function refreshModels() {
  if (state.fetchingModels) return;
  state.fetchingModels = true;
  try { state.models = (await api("/api/models")).models; renderModels(); }
  catch (_) { /* Runtime status already reports connection failures. */ }
  finally { state.fetchingModels = false; }
}
$("model-manage").addEventListener("click", () => { openSettings(); });
setInterval(() => { if (!document.hidden) refreshModels(); }, 2500);
