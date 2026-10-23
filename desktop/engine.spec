# PyInstaller one-directory bundle; run scripts/build_engine.py from any directory.
from pathlib import Path
from PyInstaller.utils.hooks import collect_all, collect_data_files, copy_metadata

root = Path(SPECPATH).parent
binaries = []
datas = collect_data_files('mdeverything')
hiddenimports = ['mdeverything.worker', 'mdeverything.speech_models']
for package in ('faster_whisper', 'ctranslate2', 'av', 'onnxruntime', 'tokenizers', 'yt_dlp', 'yt_dlp_ejs'):
    data, binary, hidden = collect_all(package)
    datas += data
    binaries += binary
    hiddenimports += hidden
for distribution in ('mdeverything', 'faster-whisper', 'ctranslate2', 'av', 'onnxruntime',
                     'yt-dlp', 'yt-dlp-ejs', 'huggingface-hub', 'tokenizers'):
    datas += copy_metadata(distribution)
a = Analysis([str(root / 'src/mdeverything/desktop.py')], pathex=[str(root / 'src')],
             binaries=binaries, datas=datas, hiddenimports=hiddenimports,
             excludes=['torch', 'tensorflow', 'matplotlib', 'IPython', 'pytest', 'tkinter'],
             noarchive=False)
pyz = PYZ(a.pure)
exe = EXE(pyz, a.scripts, [], exclude_binaries=True, name='mde-engine', debug=False,
          bootloader_ignore_signals=False, strip=False, upx=False, console=True,
          argv_emulation=False, codesign_identity=None)
coll = COLLECT(exe, a.binaries, a.datas, strip=False, upx=False, name='mde-engine')
