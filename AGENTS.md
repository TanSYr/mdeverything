# mdeverything contributor instructions

Read README.md and docs/design.md before changes. The shared document model is in src/mdeverything/models.py; CLI and web workers must use the same pipeline/exporters. Keep adapter work independent of UI.

Validate relevant changes with pytest, ruff check ., ruff format --check ., and python -m build. For UI changes, run tests/browser_smoke.py against a running local server with Playwright installed; test a 390px viewport as well as desktop. Never silently weaken CSP to make a test pass.

The app is a trusted single-user local workspace, not a public hosted service. Preserve same-origin/custom-header checks, safe text rendering, UUID-scoped job paths, and subprocess cancellation. Keep full transcript and source evidence when adding AI features. No telemetry, committed secrets, real private transcripts, browser cookies or model weights.

README feature claims must match working code. Use fixtures for deterministic CI and distinguish them from live-provider checks. Record meaningful limitations in docs/roadmap.md or docs/installation.md.
