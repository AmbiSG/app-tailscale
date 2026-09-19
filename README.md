# Ambi Support Tailscale for Home Assistant

[![Release](https://img.shields.io/github/v/release/AmbiSG/app-tailscale)](https://github.com/AmbiSG/app-tailscale/releases)
[![CI](https://github.com/AmbiSG/app-tailscale/actions/workflows/ci.yaml/badge.svg)](https://github.com/AmbiSG/app-tailscale/actions/workflows/ci.yaml)
[![License](https://img.shields.io/github/license/AmbiSG/app-tailscale)](LICENSE.md)

This Home Assistant custom app provides Ambi's separate support tailnet. It is
designed to run beside the official/community Tailscale app: the client keeps
their own tailnet, while Ambi receives an independent support connection.

## Install

Add this custom repository in **Settings → Apps → App store → Repositories**:

```text
https://github.com/AmbiSG/app-tailscale
```

The published multi-architecture image is
`ghcr.io/ambisg/ambi-support-tailscale`. Package releases are immutable and the
Home Assistant repository is pinned to a released version.

See [the app documentation](tailscale/DOCS.md) for configuration options and
[FORK.md](FORK.md) for the maintained differences from upstream.

## Maintenance

- The sync-upstream workflow merges compatible upstream changes, regenerates
  the immutable Ambi version, and runs the complete validated, signed release
  path without reviewer approval.
- The CI workflow validates stable app metadata on pull requests and as the
  sync release gate.
- The publish workflow builds, signs, publishes, and verifies the AMD64/ARM64
  GHCR manifest; it is reusable from sync and manually dispatchable for
  diagnostics.

## Attribution

This repository is derived from
[`hassio-addons/app-tailscale`](https://github.com/hassio-addons/app-tailscale),
originally maintained by Franck Nijhof and its contributors. The upstream
copyright and MIT license are retained in [LICENSE.md](LICENSE.md).
