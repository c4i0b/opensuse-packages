#!/usr/bin/env bash
# Fetch sources for the local pre-flight build (OBS fetches via _service).
# Modes:
#   ./fetch.sh          fetch Source0 only
#   ./fetch.sh --vendor regenerate requirements.txt + wheels.tar.zst
# Keep requirements.txt and wheels.tar.zst in sync with Source0 on bumps.
#
# The wheel set is the locked closure from upstream's uv.lock (exact pins +
# hashes, honoring [tool.uv] override-dependencies), exported with uv and
# downloaded for linux x86_64 / CPython 3.14 (the python314 the spec wraps).
# uv itself is not in the (older) tooling container image: a standalone uv is
# installed into a scratch dir when no uv is on PATH.
set -euo pipefail
cd "$(dirname "$0")"
version="$(sed -n 's/^Version:[[:space:]]*//p' hermes-agent.spec)"
mode="${1:-}"

# cached: just build runs fetch.sh every time; skip the re-download
[ -s "hermes-agent-$version.tar.gz" ] || \
curl -sL "https://github.com/NousResearch/hermes-agent/archive/refs/tags/v$version.tar.gz" \
    -o "hermes-agent-$version.tar.gz"

[ "$mode" = "--vendor" ] || exit 0
tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

if ! command -v uv >/dev/null 2>&1; then
    export UV_INSTALL_DIR="$tmp/uv-bin"
    curl -LsSf https://astral.sh/uv/install.sh | UV_UNMANAGED_INSTALL=1 sh >/dev/null
    # standalone install: the binary lands in UV_INSTALL_DIR itself
    export PATH="$UV_INSTALL_DIR:$UV_INSTALL_DIR/bin:$PATH"
fi
command -v uv

mkdir -p "$tmp/src"
tar zxf "hermes-agent-$version.tar.gz" -C "$tmp/src" --strip-components=1

# locked closure, no dev group, no extras; hashes included so pip download
# verifies every artifact it fetches
( cd "$tmp/src" && \
  uv export --frozen --no-dev --no-emit-project --no-emit-workspace \
      -o "$tmp/requirements.txt" )

# seeded (pip-carrying) 3.14 venv: pip download then selects the right
# linux x86_64 / cp314 wheels for the markers in requirements.txt.
# --no-deps: the lock IS the resolved closure; re-resolving would hit the
# conflicts upstream's [tool.uv] override-dependencies exist to break
# (browser-harness pins pillow==12.3.0 vs the direct 13.0.0 pin). Hashes
# still verify every artifact.
uv venv --python 3.14 --seed "$tmp/dl"
"$tmp/dl/bin/python" -m pip download -r "$tmp/requirements.txt" \
    -d "$tmp/wheels" --no-deps --no-cache-dir --disable-pip-version-check -q
# build backend for the spec's --no-build-isolation install of the project
"$tmp/dl/bin/python" -m pip download "setuptools==84.1.0" wheel \
    -d "$tmp/wheels" --no-cache-dir --disable-pip-version-check -q

cp "$tmp/requirements.txt" .
rm -f wheels.tar.zst
tar -C "$tmp" --zstd -cf wheels.tar.zst wheels
du -sh wheels.tar.zst
