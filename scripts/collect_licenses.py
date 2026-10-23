"""Collect redistributed runtime license texts and pinned PyAV vendor source materials."""

import concurrent.futures
import importlib.metadata
import json
import platform
import shutil
import subprocess
import tarfile
import urllib.request
from pathlib import Path

from prepare_runtime import ROOT, fetch


def collect(output, cache):
    licenses = output / "licenses"
    shutil.copyfile(ROOT / "THIRD_PARTY_NOTICES.md", licenses / "THIRD_PARTY_NOTICES.md")
    sources = licenses / "pyav-vendor-sources"
    sources.mkdir(parents=True, exist_ok=True)
    manifest = json.loads((ROOT / "desktop/vendor-sources.json").read_text())

    def vendor(item):
        name, record = item
        content = fetch(record, cache)
        plain = name.endswith("-license") or record.get("kind") == "text"
        archive = sources / (name + (".txt" if plain else ".tar.source"))
        archive.write_bytes(content)
        if not plain:
            with tarfile.open(archive, "r:*") as package:
                # Extract only regular license/notice text; retain full archives for source/patches.
                for index, member in enumerate(package.getmembers()):
                    basename = Path(member.name).name
                    if (
                        member.isfile()
                        and member.size < 2 * 1024**2
                        and any(word in basename.upper() for word in ("COPYING", "LICENSE", "NOTICE"))
                    ):
                        destination = sources / "license-texts" / name
                        destination.mkdir(parents=True, exist_ok=True)
                        (destination / f"{index}-{basename}").write_bytes(package.extractfile(member).read())
        print("Source and licenses verified:", name, flush=True)

    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        list(pool.map(vendor, manifest.items()))
    (sources / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    (sources / "README.txt").write_text(
        "These are the corresponding source archives and build recipe for PyAV 18.1.0's vendor "
        "FFmpeg 8.1.2-1 and codec dependencies, including x264/x265 GPL components. "
        "Do not infer their license from avcodec_license() alone: the vendor patches "
        "FFmpeg's configure license lists. Preserve each source's license terms. "
        "The pyav-ffmpeg-build archive contains patches, dependency hashes and build scripts. "
        "Archives keep original tar compression and can be opened with tar -xf. "
        "The native libraries are outside app.asar and may be replaced/relinked. "
        "Windows wheel inspection identifies libiconv 1.19, zlib 1.3.2 and GCC 16.1.0 (MSYS2 Rev5). "
        "The MSYS2 winpthreads recipe is the last historical snapshot before the vendor build; "
        "the exact winpthreads revision is not encoded in the DLL and cannot be byte-proven. "
        "Its MIT/BSD license text is retained. GCC runtime exception text is also retained. "
        "This is separate from our standalone FFmpeg 7.1.1 LGPL build.\n"
    )
    # electron-builder does not copy the distribution-root license files into a macOS app.
    electron = ROOT / "desktop/node_modules/electron"
    node = output / "bin" / ("node.exe" if platform.system() == "Windows" else "node")
    subprocess.run([str(node), "-e", "require(process.argv[1])", str(electron)], check=True)
    for filename in ("LICENSE", "LICENSES.chromium.html"):
        shutil.copyfile(electron / "dist" / filename, licenses / ("Electron-" + filename))
    packages = licenses / "python-packages"
    packages.mkdir(exist_ok=True)
    copied = []
    for distribution in importlib.metadata.distributions():
        name = distribution.metadata.get("Name", "unknown")
        found = []
        for file in distribution.files or []:
            if not any(word in Path(str(file)).name.upper() for word in ("LICENSE", "COPYING", "NOTICE")):
                continue
            original = Path(distribution.locate_file(file))
            if not original.is_file() or original.stat().st_size > 2 * 1024**2:
                continue
            safe = str(file).replace("..", "_").lstrip("/\\").replace("/", "__").replace("\\", "__")
            folder = packages / name
            folder.mkdir(exist_ok=True)
            shutil.copyfile(original, folder / safe)
            found.append(safe)
        if found:
            copied.append({"package": name, "version": distribution.version, "license_files": found})
    (packages / "manifest.json").write_text(json.dumps(copied, indent=2) + "\n")
    # Python's installer does not consistently retain LICENSE in its filesystem layout.
    python_url = f"https://raw.githubusercontent.com/python/cpython/v{platform.python_version()}/LICENSE"
    with urllib.request.urlopen(python_url, timeout=60) as response:
        (licenses / "CPython-LICENSE.txt").write_bytes(response.read())
    (licenses / "CPython-source.txt").write_text(python_url + "\n")


if __name__ == "__main__":
    collect(ROOT / "desktop/runtime", ROOT / "desktop/.build/downloads")
