OBS_USER := "caiobruno"
OBS_API  := "https://api.opensuse.org"
REGISTRY := "registry.opensuse.org"
OSC_WORK := home_directory() / "obs"
repo := justfile_directory()

default:
    @just --list --unsorted

proj pkg:
    #!/usr/bin/env bash
    IFS=/ read -r category _ <<< "{{pkg}}"
    echo "home:{{OBS_USER}}:${category}"

image-ref pkg:
    #!/usr/bin/env bash
    IFS=/ read -r category name <<< "{{pkg}}"
    echo "{{REGISTRY}}/home:{{OBS_USER}}:${category}/${name}"

bootstrap:
    @command -v podman && podman --version || echo "podman MISSING"
    @command -v osc && osc --version || echo "osc MISSING -> install osc and run 'just osc-config'"
    @command -v just && just --version

osc-config:
    #!/usr/bin/env bash
    set -e
    if [ -f "$HOME/.oscrc" ]; then
      echo "~/.oscrc exists"
      grep -q "api.opensuse.org" "$HOME/.oscrc" && echo "  has api.opensuse.org section" || true
    else
      echo "~/.oscrc MISSING -> run: osc -A {{OBS_API}} ls home:{{OBS_USER}}"
      echo "(prompts for user/password and writes ~/.oscrc with mode 0600)"
    fi

create-project category="tools":
    #!/usr/bin/env bash
    set -euo pipefail
    project="home:{{OBS_USER}}:{{category}}"
    tmp="$(mktemp)"
    sed -e "s|@@PROJECT@@|${project}|g" -e "s|@@CATEGORY@@|{{category}}|g" "{{repo}}/_project.meta.xml" > "$tmp"
    osc -A {{OBS_API}} meta prj -F "$tmp" "$project"
    rm -f "$tmp"
    echo "project ready: $project"

checkout pkg:
    #!/usr/bin/env bash
    set -euo pipefail
    IFS=/ read -r category name <<< "{{pkg}}"
    project="home:{{OBS_USER}}:${category}"
    dest="{{OSC_WORK}}/${project}/${name}"
    if [ -d "$dest/.osc" ]; then
      (cd "$dest" && osc -A {{OBS_API}} up)
    else
      mkdir -p "{{OSC_WORK}}/${project}"
      osc -A {{OBS_API}} co "$project" "$name" -o "$dest"
    fi
    echo "working copy: $dest"

new-pkg pkg:
    #!/usr/bin/env bash
    set -euo pipefail
    IFS=/ read -r category name <<< "{{pkg}}"
    project="home:{{OBS_USER}}:${category}"
    osc -A {{OBS_API}} meta pkg --create "$project" "$name"
    just checkout "{{pkg}}"

push pkg msg:
    #!/usr/bin/env bash
    set -euo pipefail
    IFS=/ read -r category name <<< "{{pkg}}"
    project="home:{{OBS_USER}}:${category}"
    src="{{repo}}/{{pkg}}"
    dest="{{OSC_WORK}}/${project}/${name}"
    [ -d "$dest/.osc" ] || just new-pkg "{{pkg}}"
    ex=(--exclude='.osc' --exclude='fetch.sh' --exclude='bump.sh' --exclude='VERSION' --exclude='*.tar.gz' --exclude='*.zip')
    [ -f "$src/.obsignore" ] && ex+=(--exclude-from="$src/.obsignore")
    rsync -a --delete "${ex[@]}" "$src/" "$dest/"
    (cd "$dest" && osc -A {{OBS_API}} addremove && osc -A {{OBS_API}} st)
    if [ "${CI:-}" = "true" ]; then ok=y; else read -r -p "Commit ${name} to ${project}? [y/N] " ok; fi
    [ "$ok" = "y" ] || { echo aborted; exit 1; }
    (cd "$dest" && osc -A {{OBS_API}} ci -m "{{msg}}")
    echo "pushed ${name} -> ${project}"

status pkg:
    #!/usr/bin/env bash
    set -euo pipefail
    IFS=/ read -r category name <<< "{{pkg}}"
    project="home:{{OBS_USER}}:${category}"
    dest="{{OSC_WORK}}/${project}/${name}"
    (cd "$dest" && osc -A {{OBS_API}} st)

fetch pkg:
    #!/usr/bin/env bash
    set -euo pipefail
    dir="{{repo}}/{{pkg}}"
    if [ -x "$dir/fetch.sh" ]; then
      "$dir/fetch.sh"
    else
      echo "no fetch.sh for {{pkg}}"
    fi

build pkg:
    #!/usr/bin/env bash
    set -euo pipefail
    dir="{{repo}}/{{pkg}}"
    [ -f "$dir/Dockerfile" ] || { echo "no Dockerfile in {{pkg}}"; exit 1; }
    [ -x "$dir/fetch.sh" ] && "$dir/fetch.sh" || true
    name="$(echo {{pkg}} | cut -d/ -f2)"
    podman build -t "$name:dev" "$dir"

run pkg +args:
    #!/usr/bin/env bash
    set -euo pipefail
    name="$(echo {{pkg}} | cut -d/ -f2)"
    if [ -t 0 ] && [ -t 1 ]; then tty=(-it); else tty=(-i); fi
    podman run --rm "${tty[@]}" --network host --userns=keep-id \
      -e HOME=/tmp -e TERM \
      -v "$PWD:$PWD" -w "$PWD" \
      "$name:dev" "$@"

bump pkg version:
    #!/usr/bin/env bash
    set -euo pipefail
    dir="{{repo}}/{{pkg}}"
    if [ -x "$dir/bump.sh" ]; then
      "$dir/bump.sh" "{{version}}"
    else
      echo "no bump.sh for {{pkg}}"
    fi
