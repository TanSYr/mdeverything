# Security and privacy

mdeverything v0.1 is a **trusted, single-user local application**. It has no user accounts or multi-tenant isolation. Keep it bound to loopback; Docker Compose binds the published port to 127.0.0.1. Do not expose it to the internet or use it as a service for untrusted users.

The API does not accept arbitrary local filesystem paths. Uploads are copied into UUID job directories. Writes require a custom header and same-origin checks; Host validation limits local DNS rebinding entry points. Public HTTP(S) URL syntax checks reject literal private addresses, alternate numeric loopback spellings and embedded credentials. **These checks are not a complete SSRF sandbox:** DNS responses and redirects handled by yt-dlp can change the destination. Only submit links you trust. A future hosted mode needs authenticated users, a constrained fetch proxy, egress isolation and per-user storage before launch.

Uploaded recordings and exported documents remain on the user's filesystem. There is no application telemetry. URL conversion contacts source websites. Initial model installation contacts model hosts. Optional notes contact the configured Ollama endpoint; configuring a remote endpoint sends transcript text there. Other applications/users with access to the same OS account may read job data.

Dependencies process untrusted media. Keep Python, yt-dlp, PyAV, FFmpeg and faster-whisper updated. Do not use this application to bypass DRM or access restrictions.

For a suspected vulnerability, use the repository's private vulnerability reporting feature if enabled. Otherwise open a minimal issue requesting a private contact without exploit details, recordings, credentials or private URLs. Do not post secrets in public reports.
