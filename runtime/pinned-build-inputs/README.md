# Pinned build inputs (optional offline copy)

When present, files here are checked against the SHA-256 and byte length in
`runtime/source-adapter-python.json` (and the arm64 lock) before any network
fetch. They are **software build dependencies only**; no study data belong here.

Layout (optional):

- `linux-amd64/<filename>` — amd64 `.deb` archives named in the lock
- `linux-arm64/<filename>` — arm64 `.deb` archives
- `shared/<filename>` — license-notice files reused across platforms

The CI builder also falls back to Launchpad mirrors when
`snapshot.ubuntu.com` is unavailable.
