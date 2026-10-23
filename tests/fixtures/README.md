# Original speech fixture

`original-speech.wav` is synthetic speech created for this project's regression tests, not a third-party recording or private user upload. The text is original and included under the repository's MIT license:

> This is an original recording for testing mdeverything. We turn video and audio into readable Markdown documents. Keep the source, keep the timestamps, and keep the full transcript.

The native desktop smoke test downloads the pinned Tiny model, disables network access through unreachable proxies, runs the frozen transcription worker, and checks that the output includes the word `transcript`. This complements deterministic unit fixtures and tests actual native inference.
