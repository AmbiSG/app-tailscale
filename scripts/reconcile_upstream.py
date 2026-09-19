#!/usr/bin/env python3
"""Apply and validate Ambi's small, declarative overlay after an upstream merge.

The upstream tree remains authoritative.  This script changes only the values
required to run a second Tailscale instance, records the merged upstream SHA,
and derives a unique immutable Ambi release version from the nearest upstream
stable tag.  A changed upstream structure is an error, never an implicit
ours/theirs resolution.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path


class ReconcileError(RuntimeError):
    """Raised when an upstream change invalidates a declared fork invariant."""


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "tailscale" / "config.yaml"
WEB_RUN = ROOT / "tailscale" / "rootfs" / "etc" / "s6-overlay" / "s6-rc.d" / "web" / "run"
NGINX_UPSTREAM = ROOT / "tailscale" / "rootfs" / "etc" / "nginx" / "includes" / "upstream.conf"
FORK_DOC = ROOT / "FORK.md"
UPSTREAM_OWNED = ("tailscale/Dockerfile", "tailscale/build.yaml")


def git(*args: str) -> str:
    completed = subprocess.run(
        ("git", *args),
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


def replace_exact(text: str, pattern: str, replacement: str, label: str) -> str:
    updated, count = re.subn(pattern, replacement, text, count=1, flags=re.MULTILINE)
    if count != 1:
        raise ReconcileError(f"Expected one {label}; upstream structure changed")
    return updated


def replace_or_insert_image(text: str) -> str:
    updated, count = re.subn(
        r"^image: .*$",
        "image: ghcr.io/ambisg/ambi-support-tailscale",
        text,
        count=1,
        flags=re.MULTILINE,
    )
    if count == 1:
        return updated
    if count > 1:
        raise ReconcileError("Expected at most one image declaration")
    return replace_exact(
        text,
        r"^(url: https://github\.com/AmbiSG/app-tailscale\n)",
        r"\1image: ghcr.io/ambisg/ambi-support-tailscale\n",
        "Ambi repository URL before the image declaration",
    )


def release_version(upstream_ref: str) -> str:
    tag = git("describe", "--tags", "--abbrev=0", "--match", "v[0-9]*", upstream_ref)
    match = re.fullmatch(r"v(\d+\.\d+\.\d+)", tag)
    if match is None:
        raise ReconcileError(f"Nearest upstream tag {tag!r} is not a stable MAJOR.MINOR.PATCH release")
    distance = int(git("rev-list", "--count", f"{tag}..{upstream_ref}"))
    return f"{match.group(1)}-ambi.{distance + 1}"


def ensure_upstream_owned_files(upstream_ref: str) -> None:
    check = subprocess.run(
        ("git", "diff", "--quiet", upstream_ref, "--", *UPSTREAM_OWNED),
        cwd=ROOT,
    )
    if check.returncode == 1:
        raise ReconcileError("Dockerfile or build.yaml diverges from upstream")
    if check.returncode != 0:
        raise ReconcileError("Could not compare upstream-owned build files")


def reconcile(upstream_ref: str) -> tuple[str, dict[Path, str]]:
    upstream_sha = git("rev-parse", upstream_ref)
    version = release_version(upstream_ref)
    ensure_upstream_owned_files(upstream_ref)

    config = CONFIG.read_text(encoding="utf-8")
    config = replace_exact(config, r"^name: .*$", "name: Ambi Support Tailscale", "app name")
    config = replace_exact(config, r"^version: .*$", f"version: {version}", "app version")
    config = replace_exact(config, r"^slug: .*$", "slug: ambi_support_tailscale", "app slug")
    config = replace_exact(
        config,
        r"^url: .*$",
        "url: https://github.com/AmbiSG/app-tailscale",
        "app URL",
    )
    config = replace_or_insert_image(config)
    config = replace_exact(
        config,
        r"^  accept_dns: (?:true|false)$",
        "  accept_dns: false",
        "accept_dns default",
    )
    config = replace_exact(
        config,
        r"^  userspace_networking: (?:true|false)$",
        "  userspace_networking: true",
        "userspace_networking default",
    )

    web_run = WEB_RUN.read_text(encoding="utf-8")
    web_run = replace_exact(
        web_run,
        r"^options\+=\(--listen 127\.0\.0\.1:(?:25899|25900)\)$",
        "options+=(--listen 127.0.0.1:25900)",
        "web listener port",
    )

    nginx_upstream = NGINX_UPSTREAM.read_text(encoding="utf-8")
    nginx_upstream = replace_exact(
        nginx_upstream,
        r"^    server 127\.0\.0\.1:(?:25899|25900);$",
        "    server 127.0.0.1:25900;",
        "nginx upstream port",
    )

    fork_doc = FORK_DOC.read_text(encoding="utf-8")
    fork_doc = replace_exact(
        fork_doc,
        r"(?m)(Baseline: `hassio-addons/app-tailscale` commit\n`)[0-9a-f]{40}(`\.)",
        rf"\g<1>{upstream_sha}\g<2>",
        "recorded upstream baseline",
    )

    return version, {
        CONFIG: config,
        WEB_RUN: web_run,
        NGINX_UPSTREAM: nginx_upstream,
        FORK_DOC: fork_doc,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--upstream-ref", required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    try:
        version, updates = reconcile(args.upstream_ref)
        if not args.dry_run:
            for path, content in updates.items():
                path.write_text(content, encoding="utf-8", newline="\n")
    except (OSError, ReconcileError, subprocess.CalledProcessError) as error:
        print(f"reconcile_upstream: {error}", file=sys.stderr)
        return 1

    print(version)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
