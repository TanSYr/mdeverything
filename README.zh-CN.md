<div align="center">

# mdeverything

### 把看过的视频，变成用得上的知识。

**视频链接、本地录音、字幕 → 带来源和时间戳的 Markdown。**

[![CI](https://github.com/TanSYr/mdeverything/actions/workflows/ci.yml/badge.svg)](https://github.com/TanSYr/mdeverything/actions/workflows/ci.yml)
[![MIT](https://img.shields.io/badge/license-MIT-232323.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.11%2B-e76a41.svg)](https://www.python.org/downloads/)

[English](README.md) · **简体中文**<br>
[快速开始](#快速开始) · [产物示例](examples/demo.md) · [路线图](docs/roadmap.md) · [参与贡献](CONTRIBUTING.md)

![mdeverything 工作台：内置原创字幕的真实转换结果](docs/screenshot.png)

</div>

收藏了很多视频，真正用到时却找不到那句话。mdeverything 把视频里的内容变成你能检索、引用、编辑、交给 AI 的文档，同时保留回到原视频的线索。

**不注册账号，不要求付费 API Key，文件由你自己保存。**

> **v0.1.0 早期版本。** 已提供本地 Web 工作台和命令行；原生桌面安装包尚未发布。名称中的 everything 是方向，不代表现在支持所有网站、所有文件格式。网站可用性取决于 yt-dlp 和平台变化。

### 看一次真实转换

![Original subtitles → document preview → raw Markdown](docs/demo.gif)

## 为什么做这个？

- **字幕优先，少等一步。** 能读取字幕就直接转换，跳过媒体下载与语音识别。
- **无字幕也能转。** 使用 faster-whisper 在本机 CPU 上转录；首次使用需下载模型。
- **保留证据。** 来源、时间戳、平台提供的章节、完整原文一起保存。YouTube 和 B 站的时间戳带回跳链接，其他站点链接回原页面。
- **完整工作台。** 批量链接、拖入文件、实时进度、取消、重试、搜索历史、文档预览。
- **文件自由流动。** 导出 Markdown、SRT、JSON，可交给 Obsidian、编辑器、Git 或 AI 工具。
- **可选本地 AI 笔记。** 接入你自己的 Ollama 模型；笔记单独标注，生成失败也不丢原文。
- **先试再配环境。** 内置原创字幕走真实转换流程，不下载模型也能试用。

## 快速开始

推荐 Python **3.11–3.13**，处理媒体建议安装 FFmpeg。仅转换 `.srt` / `.vtt` 无需 FFmpeg 或语音模型。

```bash
git clone https://github.com/TanSYr/mdeverything.git
cd mdeverything
python -m venv .venv
source .venv/bin/activate       # Windows：.venv\Scripts\activate
pip install -e ".[transcribe]"
mde serve
```

打开 **http://127.0.0.1:8765**，点击 **Try the demo**。右上角可切换中文界面。

转换 YouTube 建议先安装 **Deno 2.3+ 或 Node.js 22+** 并加入 PATH，应用会自动检测。详见[运行时配置](docs/installation.md#youtube-javascript-runtime)。

只想先试字幕转换：安装命令换成 `pip install -e .`。之后可补装 `pip install -e ".[transcribe]"`。

使用 uv：

```bash
uv sync --extra transcribe
uv run mde serve
```

### Docker

```bash
docker compose up --build -d
```

从当前仓库构建，包含 FFmpeg 和本地转录依赖。打开 **http://127.0.0.1:8765**。任务与模型使用命名卷保存；`docker compose down` 停止服务，加 `-v` 会删除卷内数据。默认仅监听本机，请勿公开暴露端口。

### 命令行

```bash
# 内置字幕示例，不下载模型
mde convert examples/demo.vtt -o ./notes

# 视频链接，优先取字幕
mde convert "https://www.youtube.com/watch?v=VIDEO_ID" -o ./notes

# 本地视频或录音
mde convert meeting.mp4 --language zh --model small -o ./notes

# 批量，每行一个链接或文件路径
mde convert --batch inputs.txt -o ./notes

# 检查依赖
mde doctor
```

每个输入生成独立文件夹，包含 `document.md`、`document.srt`、`document.json`，不会覆盖已有结果。语言选项用于选择字幕/识别语言，不是翻译功能。

[安装、模型下载、登录内容与排错 →](docs/installation.md)

## 能处理什么？

| 输入 | 转换方式 | 当前边界 |
| --- | --- | --- |
| 视频链接 | yt-dlp 字幕 → 音频 → 本地转录 | 单条视频；每次最多提交 20 个链接 |
| MP4 / MOV / MKV / WebM 等视频 | 本地语音识别 | CPU 推理，速度取决于模型和硬件 |
| MP3 / WAV / M4A / FLAC / OGG 等音频 | 本地语音识别 | 模型首次使用需下载 |
| SRT / WebVTT | 字幕解析、滚动字幕去重、导出 | UTF-8，无需模型 |

网站列表以 [yt-dlp 上游文档](https://github.com/yt-dlp/yt-dlp/blob/master/supportedsites.md)为参考，**不等于本项目已经逐站验证**。部分网站需要登录或限制访问；仅处理你有权访问的内容。不支持 DRM 保护内容或正在进行的直播。

当前尚无：原生桌面安装包、播放列表展开、说话人区分、翻译、画面 OCR、PDF/网页转换、公开多用户服务。功能状态见[路线图](docs/roadmap.md)。

## 可选的本地 AI 笔记

安装 [Ollama](https://ollama.com/) 后：

```bash
ollama pull qwen3:8b
MDE_OLLAMA_MODEL=qwen3:8b mde serve
```

在工作台启用「本地 AI 笔记」。默认连接 `http://127.0.0.1:11434`；可用 `MDE_OLLAMA_URL` 指定服务。长原文分块生成笔记，可能出现重复，需对照原文核验。配置远程 Ollama 服务会把原文发送到该服务。

## 数据在哪？

默认保存在 `~/.mdeverything`；可通过 `--data-dir` 或 `MDE_DATA_DIR` 修改。删除任务会移除该任务的上传文件和产物。无埋点、无遥测。访问视频链接需要连接源网站，首次使用语音模型需要连接模型仓库；本地录音在本机处理。

## 一起把它做好

```bash
pip install -e ".[dev]"
pytest
ruff check .
ruff format --check .
python -m build
```

欢迎提交可复现的问题、字幕边界案例、中文体验改进、安装说明或新的输入适配器。[贡献指南](CONTRIBUTING.md) · [架构](docs/design.md) · [安全边界](SECURITY.md)。

如果它帮你省下了时间，欢迎点一个 **Star**，让更多人找到它。更欢迎带着具体输入和报错回来，我们一起改进。

## 致谢

作者：[TanSYr](https://github.com/TanSYr)。项目延续作者原有 **Video2Text** 工作流，借鉴 [DownVid](https://github.com/Downvid/downvid) 把复杂视频工具做得易用的产品思路。独立实现，不是 DownVid 的分支或关联产品。

感谢 [yt-dlp](https://github.com/yt-dlp/yt-dlp)、[faster-whisper](https://github.com/SYSTRAN/faster-whisper)、[FastAPI](https://github.com/fastapi/fastapi)、[FFmpeg](https://ffmpeg.org/)。[第三方说明](THIRD_PARTY_NOTICES.md)。

[MIT 开源协议](LICENSE)。
