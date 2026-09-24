# Ambi second-tailnet instance

This fork exists to install a second Tailscale app alongside the community app.
Keep the source in upstream's `tailscale/` directory. The installed app keeps
the `ambi_support_tailscale` slug; the source directory is not its identity.

Baseline: `hassio-addons/app-tailscale` commit
`2f295975bcd52e0ffaf722ae43bae34bf7b8633f`.

## Intentional differences

- `tailscale/config.yaml`: Ambi name, slug and repository URL; default
  `userspace_networking: true` and `accept_dns: false` for the second instance.
- `tailscale/rootfs/etc/s6-overlay/s6-rc.d/web/run` and
  `tailscale/rootfs/etc/nginx/includes/upstream.conf`: use local web backend
  port `25900`, leaving upstream's `25899` available to the first instance.
- Repository metadata and documentation describe the stable Ambi fork.
- A scheduled sync records the upstream baseline, derives an immutable Ambi
  version, validates both architectures, signs and publishes the image, and
  creates the matching GitHub release without a reviewer gate.
- The upstream deploy workflow and generated upstream README template are
  intentionally absent.

All other app code, startup hooks, option schemas and dependency pins match
the baseline. Do not replace the service graph or remove upstream migrations.

## Running beside the community app

Keep userspace networking enabled on the Ambi instance. Both apps use host
networking; a distinct slug alone does not isolate their network interfaces or
listening ports. Userspace mode permits inbound access from the second tailnet
to Home Assistant without creating another host `tailscale0` interface. It does
not give host applications ordinary outbound routing into the second tailnet.

Set `login_server` in the Ambi app's configuration to the desired control server
(for example, `https://headscale.ambi.sg`), then use upstream's login flow. The
custom `auth_key` option has been removed. New installations use upstream's
Tailscale control server unless configured otherwise.

Leave the UDP network setting empty for automatic port selection, or configure
a different host UDP port for each instance. The upstream `41641/udp` option
key is retained so it matches the daemon script.

For an existing installation, explicitly set `userspace_networking: true` and
`accept_dns: false`; changing defaults does not replace saved options. Remove
the old `auth_key` option and retain your desired `login_server`. Check the UDP
network setting because the previous fork used the key `41642/udp`. Back up
the app before upgrading. Validate simultaneous startup, both web UIs and
remote access through both tailnets on a Home Assistant machine before release.

## Updating upstream

The sync-upstream workflow is the normal release path. It merges upstream
history, applies the small declarative coexistence overlay, verifies that
tailscale/Dockerfile and tailscale/build.yaml remain upstream-identical, then
validates, signs, publishes, and verifies AMD64 and ARM64 images before
creating the GitHub release. A failed build or publish retries on the next
scheduled run because the versioned release tag is created last.

The reconciliation script only accepts the declared slug/default/port
structure. A merge conflict, missing expected field, changed port structure,
or upstream build-file divergence stops the run instead of choosing ours or
theirs. That is the sole exceptional maintenance path; normal compatible
upstream releases require no approval.

The publish workflow remains manually dispatchable with publish disabled for
diagnostics. Do not hardcode base image versions or rewrite the Dockerfile for
publishing.
