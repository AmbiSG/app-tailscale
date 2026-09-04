# Ambi second-tailnet instance

This fork exists to install a second Tailscale app alongside the community app.
Keep the source in upstream's `tailscale/` directory. The installed app keeps
the `ambi_support_tailscale` slug; the source directory is not its identity.

Baseline: `hassio-addons/app-tailscale` commit
`55c88fe8c6b60b572d8776b7fb3ff99f7e9c8c09`.

## Intentional differences

- `tailscale/config.yaml`: Ambi name, slug and repository URL; default
  `userspace_networking: true` and `accept_dns: false` for the second instance.
- `tailscale/rootfs/etc/s6-overlay/s6-rc.d/web/run` and
  `tailscale/rootfs/etc/nginx/includes/upstream.conf`: use local web backend
  port `25900`, leaving upstream's `25899` available to the first instance.
- Repository metadata and this document describe the fork.

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

Merge upstream normally and review the three intentional app-file differences
above. Preserve executable file modes when moving files on Windows. Keeping
the original paths allows Git to apply upstream changes directly. Merge upstream
history as well as its file changes so Git records which updates are included.
