#!/usr/bin/env bash
set -euo pipefail
source_dir="$1"
output_dir="$2"
if command -v cygpath >/dev/null 2>&1; then
  source_dir="$(cygpath -u "$source_dir")"
  output_dir="$(cygpath -u "$output_dir")"
fi
cd "$source_dir"
platform_flags=()
if [[ "$(uname -s)" == Darwin ]]; then
  platform_flags+=(--enable-securetransport)
else
  platform_flags+=(--enable-schannel --extra-ldflags=-static)
fi
# Use only FFmpeg's own LGPL code and operating-system libraries. No third-party codecs.
./configure --prefix="$output_dir" --disable-autodetect --disable-gpl --disable-nonfree \
  --disable-version3 --disable-shared --enable-static --disable-doc --disable-debug \
  --disable-ffplay --disable-x86asm "${platform_flags[@]}"
make -j4
make install
