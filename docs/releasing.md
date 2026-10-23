# Release process

1. Run the test suite, Ruff and wheel build. Verify installation from the built wheel in a fresh environment and ensure static assets/demo data are included.
2. Run the real demo through the UI and CLI. Check desktop and narrow-screen layouts. Test a local recording with Whisper when changing the media path.
3. Verify README feature claims against current implementation. Distinguish live-provider tests from fixtures.
4. Update version in `pyproject.toml` and `src/mdeverything/__init__.py`; update CHANGELOG.
5. Tag the verified commit. Upload wheel and source archive to a GitHub prerelease while the project remains alpha. Do not present wheels as native desktop installers.
6. Let CI verify supported operating systems/Python versions. Record failures and fix before promoting a release.

No PyPI publishing token, hosted service or registry credentials are included. Docker images are built from source; there is no prebuilt official registry image yet.
