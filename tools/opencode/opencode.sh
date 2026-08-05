#!/usr/bin/env bash
set -euo pipefail

IMAGE="${OPENCODE_IMAGE:-registry.opensuse.org/home:caiobruno:tools/opencode-image}"
podman image exists "$IMAGE" 2>/dev/null || podman pull "$IMAGE" >/dev/null 2>&1 || true

WORKDIR="$(pwd)"
CHOME="$(mktemp -d -t opencode-home.XXXXXX)"

mkdir -p "$CHOME"/.config "$CHOME"/.cache "$CHOME"/.local/share "$CHOME"/.local/state
mkdir -p "$HOME/.config/opencode" "$HOME/.local/share/opencode"
MOUNTS=(
  -v "$CHOME:$CHOME:rw"
  -v "$WORKDIR:$WORKDIR:rw"
  -v "$HOME/.config/opencode:$CHOME/.config/opencode:rw"
  -v "$HOME/.local/share/opencode:$CHOME/.local/share/opencode:rw"
)
[ -f "$HOME/.gitconfig" ] && MOUNTS+=(-v "$HOME/.gitconfig:$CHOME/.gitconfig:ro")

if [ -t 0 ] && [ -t 1 ]; then
  TTY_FLAGS=(-it)
else
  TTY_FLAGS=(-i)
fi

ENV_VARS=(TERM SHELL OPENCODE_API_KEY ANTHROPIC_API_KEY OPENAI_API_KEY GEMINI_API_KEY XAI_API_KEY DEEPSEEK_API_KEY MISTRAL_API_KEY GROQ_API_KEY)
ENV_FLAGS=(-e HOME="$CHOME")
for var in "${ENV_VARS[@]}"; do
  value="${!var:-}"
  [ -n "$value" ] && ENV_FLAGS+=(-e "$var=$value")
done

set +e
podman run --rm "${TTY_FLAGS[@]}" \
  --network host \
  --userns=keep-id \
  "${ENV_FLAGS[@]}" \
  "${MOUNTS[@]}" \
  -w "$WORKDIR" \
  "$IMAGE" "$@"
status=$?
set -e
rm -rf "$CHOME"
exit $status
