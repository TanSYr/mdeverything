"""Prepare SHA-256 pinned Node plus LGPL FFmpeg built from bundled official source."""

import hashlib
import io
import json
import os
import platform
import shutil
import subprocess
import tarfile
import urllib.request
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def fetch(item, cache):
    destination = cache / item["sha256"]
    if not destination.exists():
        with urllib.request.urlopen(item["url"], timeout=180) as response:
            destination.write_bytes(response.read())
    content = destination.read_bytes()
    if hashlib.sha256(content).hexdigest() != item["sha256"]:
        destination.unlink()
        raise RuntimeError("SHA256 mismatch: " + item["url"])
    return content


def build_ffmpeg(item, cache, output):
    source = fetch(item, cache)
    work = ROOT / "desktop/.build/ffmpeg"
    work.mkdir(parents=True, exist_ok=True)
    # The archive is pinned and only relative paths under its version directory are allowed.
    with tarfile.open(fileobj=io.BytesIO(source), mode="r:xz") as archive:
        for member in archive.getmembers():
            path = Path(member.name)
            if path.is_absolute() or ".." in path.parts or member.issym() or member.islnk():
                raise RuntimeError("Unsafe FFmpeg source archive member")
        if not (work / "ffmpeg-7.1.1/configure").exists():
            archive.extractall(work, filter="data")
    source_dir = work / "ffmpeg-7.1.1"
    prefix = work / "installed"
    bash = os.environ.get("MDE_BASH") or shutil.which("bash")
    if not bash:
        raise RuntimeError("FFmpeg build needs Bash and a native C compiler (MSYS2 on Windows)")
    subprocess.run([bash, str(ROOT / "scripts/build_ffmpeg.sh"), str(source_dir), str(prefix)], check=True)
    extension = ".exe" if os.name == "nt" else ""
    for name in ("ffmpeg", "ffprobe"):
        shutil.copy2(prefix / "bin" / (name + extension), output / "bin" / (name + extension))
    licenses = output / "licenses"
    (licenses / "ffmpeg-7.1.1-source.tar.xz").write_bytes(source)
    for name in ("COPYING.LGPLv2.1", "LICENSE.md", "README.md"):
        shutil.copyfile(source_dir / name, licenses / ("FFmpeg-" + name))
    shutil.copyfile(ROOT / "scripts/build_ffmpeg.sh", licenses / "FFmpeg-build.sh")
    configuration = subprocess.run(
        [str(output / "bin" / ("ffmpeg" + extension)), "-buildconf"],
        check=True,
        capture_output=True,
        text=True,
    )
    (licenses / "FFmpeg-buildconf.txt").write_text(configuration.stdout + configuration.stderr)
    assert "--enable-nonfree" not in configuration.stderr
    assert "--enable-gpl" not in configuration.stderr


def main():
    system = {"Darwin": "darwin", "Windows": "win32"}[platform.system()]
    machine = platform.machine().lower()
    arch = "arm64" if machine in ("arm64", "aarch64") else "x64"
    target = system + "-" + arch
    manifest = json.loads((ROOT / "desktop/runtime-manifest.json").read_text())
    items = manifest[target]
    output = ROOT / "desktop/runtime"
    cache = ROOT / "desktop/.build/downloads"
    cache.mkdir(parents=True, exist_ok=True)
    # Never preserve binaries or license claims from a previous build.
    if output.exists():
        shutil.rmtree(output)
    binary = output / "bin"
    licenses = output / "licenses"
    binary.mkdir(parents=True)
    licenses.mkdir(parents=True)
    build_ffmpeg(manifest["ffmpeg_source"], cache, output)
    node = fetch(items["node"], cache)
    if system == "win32":
        with zipfile.ZipFile(io.BytesIO(node)) as archive:
            for filename, destination in (
                ("node.exe", binary / "node.exe"),
                ("LICENSE", licenses / "Node-LICENSE.txt"),
            ):
                match = next(name for name in archive.namelist() if name.endswith("/" + filename))
                destination.write_bytes(archive.read(match))
    else:
        with tarfile.open(fileobj=io.BytesIO(node), mode="r:gz") as archive:
            for filename, destination in (
                ("bin/node", binary / "node"),
                ("LICENSE", licenses / "Node-LICENSE.txt"),
            ):
                member = next(
                    member for member in archive.getmembers() if member.name.endswith("/" + filename)
                )
                destination.write_bytes(archive.extractfile(member).read())
        (binary / "node").chmod(0o755)
    shutil.copyfile(ROOT / "THIRD_PARTY_NOTICES.md", licenses / "THIRD_PARTY_NOTICES.md")
    (licenses / "runtime-manifest.json").write_text(
        json.dumps({target: items, "ffmpeg_source": manifest["ffmpeg_source"]}, indent=2) + "\n"
    )
    extension = ".exe" if system == "win32" else ""
    for name, flag in (("node", "--version"), ("ffmpeg", "-version"), ("ffprobe", "-version")):
        result = subprocess.run(
            [str(binary / (name + extension)), flag], check=True, capture_output=True, text=True
        )
        print(result.stdout.splitlines()[0])
    from collect_licenses import collect

    collect(output, cache)
    print("Verified runtime prepared:", output)


if __name__ == "__main__":
    main()
