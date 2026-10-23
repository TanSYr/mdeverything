# Contributing

Thanks for helping make video knowledge portable. Small, reproducible contributions are easiest to review.

## Development

Use Python 3.11+, create a virtual environment and run:

```bash
pip install -e ".[dev]"
pytest
ruff check .
ruff format --check .
python -m build
mde serve
```

The frontend is packaged plain HTML/CSS/JavaScript under `src/mdeverything/static`; no Node build or CDN is needed. Browser tests can use Playwright against a running app. Test both desktop and a 390px viewport. Run the committed browser smoke test with `pip install playwright`, `playwright install chromium`, then `python tests/browser_smoke.py` against a running default-port app (override with `MDE_TEST_URL`). API-changing calls require `X-MDE-Client: web`.

## Good first contributions

- Add a minimal subtitle fixture that reproduces a parsing issue.
- Improve a specific installation step for your operating system.
- Improve English/Chinese interface copy or keyboard accessibility.
- Add tests for exporter interoperability with the tools you use.

For a new input format, open an issue describing the exact input → document output first. Keep adapters independent of UI and preserve the shared document model. Test failure cases and do not silently replace the full transcript with generated prose.

## Pull requests

Explain the problem and resulting behavior, include relevant verification, and keep changes focused. New features need meaningful tests. UI changes need screenshots. Never commit recordings without permission, cookies, API tokens, personal transcripts, caches or model weights. Do not add telemetry or cloud processing without explicit product discussion.

## Community

Be respectful, assume good intent and focus on reproducible behavior. Report security issues using SECURITY.md. Star requests must remain optional; no star-gated features, fake stars or misleading benchmarks.
