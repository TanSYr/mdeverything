# Release process

1. Run the test suite, Ruff and wheel build. Verify installation from the built wheel in a fresh environment and ensure static assets/demo data are included.
2. Run the real demo through the UI and CLI. Check desktop and narrow-screen layouts. Test a local recording with Whisper when changing the media path.
3. Verify README feature claims against current implementation. Distinguish live-provider tests from fixtures.
4. Update version in `pyproject.toml` and `src/mdeverything/__init__.py` and `desktop/package.json`/lockfile; update CHANGELOG.
5. Tag the verified commit. Upload wheel and source archive to a GitHub prerelease while the project remains alpha. Do not present wheels as native desktop installers.
6. Let CI verify supported operating systems/Python versions. Record failures and fix before promoting a release.

No PyPI publishing token, hosted service or registry credentials are included. Docker images are built from source; there is no prebuilt official registry image yet.

## Desktop artifacts

Follow [desktop build instructions](desktop.md). Run the desktop workflow on the release candidate and inspect all three architecture jobs before publishing. Verify that FFmpeg's build does not enable nonfree components, and retain source/license notices. Run the frozen engine with the smoke script, then launch the packaged app and exercise conversion, export, model preparation, preferences and quit. Publish `.dmg` files for macOS arm64/x64, an `.exe` installer for Windows x64, and checksums. Disclose unsigned/not-notarized preview status. A CI build and backend smoke are not evidence of manual testing on every physical device; distinguish those in release notes.
