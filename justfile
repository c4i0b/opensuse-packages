OBS_USER      := "caiobruno"
OBS_NAME      := "Caio Bruno"
OBS_EMAIL     := "cbrunofb@gmail.com"
OBS_API       := "https://api.opensuse.org"
OBS_REPO      := "opensuse_tumbleweed"
OBS_ARCH      := "x86_64"
OSC_RUN       := env_var_or_default("OSC_RUN", "distrobox enter obs --")
OSC_WORK      := home_directory() / "obs"
repo          := justfile_directory()

default:
    @just --list --unsorted

bootstrap:
    @command -v podman && podman --version || echo "podman MISSING"
    @command -v distrobox && distrobox --version || echo "distrobox MISSING"
    @command -v rsync && rsync --version | head -1 || echo "rsync MISSING"
    @command -v just && just --version
    @echo "osc runs inside the 'obs' distrobox (just obs-create); set OSC_RUN='' to use a host osc instead"

create-project category="tools":
    #!/usr/bin/env bash
    set -euo pipefail
    project="home:{{OBS_USER}}:{{category}}"
    tmp="$(mktemp)"
    sed -e "s|@@PROJECT@@|${project}|g" -e "s|@@CATEGORY@@|{{category}}|g" -e "s|@@REPO@@|{{OBS_REPO}}|g" -e "s|@@ARCH@@|{{OBS_ARCH}}|g" "{{repo}}/_project.meta.xml" > "$tmp"
    {{OSC_RUN}} osc -A {{OBS_API}} meta prj -F "$tmp" "$project"
    rm -f "$tmp"
    echo "project ready: $project"

checkout pkg:
    #!/usr/bin/env bash
    set -euo pipefail
    IFS=/ read -r category name <<< "{{pkg}}"
    project="home:{{OBS_USER}}:${category}"
    dest="{{OSC_WORK}}/${project}/${name}"
    if [ -d "$dest/.osc" ]; then
      (cd "$dest" && {{OSC_RUN}} osc -A {{OBS_API}} up)
    else
      mkdir -p "{{OSC_WORK}}/${project}"
      {{OSC_RUN}} osc -A {{OBS_API}} co "$project" "$name" -o "$dest"
    fi
    echo "working copy: $dest"

new-pkg pkg:
    #!/usr/bin/env bash
    set -euo pipefail
    IFS=/ read -r category name <<< "{{pkg}}"
    project="home:{{OBS_USER}}:${category}"
    spec="$(ls "{{repo}}/{{pkg}}"/*.spec | head -1)"
    summary="$(awk '/^Summary:/ {sub(/^Summary:[ \t]*/,""); print; exit}' "$spec")"
    desc="$(awk '/^%description/{f=1;next}/^%/{f=0}f&&NF{print}' "$spec" | head -8)"
    esc() { sed -e 's/&/\&amp;/g' -e 's/</\&lt;/g' -e 's/>/\&gt;/g'; }
    tmp="$(mktemp)"
    {
      echo "<package name=\"${name}\" project=\"${project}\">"
      printf '  <title>%s</title>\n' "$(printf '%s' "$summary" | esc)"
      printf '  <description>%s</description>\n' "$(printf '%s' "$desc" | esc)"
      echo "</package>"
    } > "$tmp"
    {{OSC_RUN}} osc -A {{OBS_API}} meta pkg -F "$tmp" "$project" "$name"
    rm -f "$tmp"
    just checkout "{{pkg}}"

push pkg msg:
    #!/usr/bin/env bash
    set -euo pipefail
    IFS=/ read -r category name <<< "{{pkg}}"
    project="home:{{OBS_USER}}:${category}"
    src="{{repo}}/{{pkg}}"
    dest="{{OSC_WORK}}/${project}/${name}"
    [ -d "$dest/.osc" ] || just new-pkg "{{pkg}}"
    ex=(--exclude='.osc' --exclude='fetch.sh' --exclude='bump.sh' --exclude='VERSION' --exclude='BIN' --exclude='*.tar.gz' --exclude='*.zip')
    [ -f "$src/.obsignore" ] && ex+=(--exclude-from="$src/.obsignore")
    rsync -a --delete "${ex[@]}" "$src/" "$dest/"
    (cd "$dest" && {{OSC_RUN}} osc -A {{OBS_API}} addremove && {{OSC_RUN}} osc -A {{OBS_API}} st)
    if [ "${CI:-}" = "true" ]; then ok=y; else read -r -p "Commit ${name} to ${project}? [y/N] " ok; fi
    [ "$ok" = "y" ] || { echo aborted; exit 1; }
    (cd "$dest" && {{OSC_RUN}} osc -A {{OBS_API}} ci -m "{{msg}}")
    echo "pushed ${name} -> ${project}"

status pkg:
    #!/usr/bin/env bash
    set -euo pipefail
    IFS=/ read -r category name <<< "{{pkg}}"
    project="home:{{OBS_USER}}:${category}"
    dest="{{OSC_WORK}}/${project}/${name}"
    (cd "$dest" && {{OSC_RUN}} osc -A {{OBS_API}} st)

fetch pkg:
    #!/usr/bin/env bash
    set -euo pipefail
    dir="{{repo}}/{{pkg}}"
    if [ -x "$dir/fetch.sh" ]; then "$dir/fetch.sh"; else echo "no fetch.sh for {{pkg}}"; fi

build pkg:
    #!/usr/bin/env bash
    set -euo pipefail
    dir="{{repo}}/{{pkg}}"
    name="$(echo {{pkg}} | cut -d/ -f2)"
    [ -x "$dir/fetch.sh" ] && "$dir/fetch.sh" || true
    if [ -f "$dir/Dockerfile" ]; then
      podman build -t "$name:dev" "$dir"
    elif ls "$dir"/*.spec >/dev/null 2>&1; then
      out="{{repo}}/.build/${name}"
      mkdir -p "$out"
      podman run --rm -e HOME=/tmp -v "$dir:/src:Z" -v "$out:/out:Z" \
        registry.opensuse.org/opensuse/tumbleweed \
        bash -lc 'set -e; zypper --non-interactive install --no-recommends rpm-build tar gzip; cd /src; rpmbuild -bb -D "_topdir /tmp/rpmbuild" -D "_sourcedir /src" -D "_rpmdir /out" *.spec'
      echo "RPMs -> $out"
    else
      echo "no Dockerfile or .spec in {{pkg}}" >&2; exit 1
    fi

run pkg +args:
    #!/usr/bin/env bash
    set -euo pipefail
    dir="{{repo}}/{{pkg}}"
    name="$(echo {{pkg}} | cut -d/ -f2)"
    if [ -f "$dir/BIN" ]; then bin="$(cat "$dir/BIN")"; else bin="$name"; fi
    if [ -f "$dir/Dockerfile" ]; then
      if [ -t 0 ] && [ -t 1 ]; then tty=(-it); else tty=(-i); fi
      podman run --rm "${tty[@]}" --network host --userns=keep-id \
        -e HOME=/tmp -e TERM -v "$PWD:$PWD" -w "$PWD" "$name:dev" {{args}}
    elif ls "$dir"/*.spec >/dev/null 2>&1; then
      out="{{repo}}/.build/${name}"
      rpm="$(ls "$out"/*/*.rpm 2>/dev/null | head -1 || true)"
      [ -n "$rpm" ] || { echo "no RPM in $out -- run 'just build {{pkg}}' first" >&2; exit 1; }
      if [ -t 0 ] && [ -t 1 ]; then tty=(-it); else tty=(-i); fi
      podman run --rm "${tty[@]}" -e HOME=/tmp -e BIN="${bin}" -v "$out:/rpms:Z" \
        registry.opensuse.org/opensuse/tumbleweed \
        bash -lc 'set -e; rpm -Uvh --nodeps /rpms/*/*.rpm; exec "$BIN" "$@"' _ {{args}}
    else
      echo "no Dockerfile or .spec in {{pkg}}" >&2; exit 1
    fi

bump pkg version:
    #!/usr/bin/env bash
    set -euo pipefail
    dir="{{repo}}/{{pkg}}"
    if [ -x "$dir/bump.sh" ]; then "$dir/bump.sh" "{{version}}"; else echo "no bump.sh for {{pkg}}"; fi

obs-image := "registry.opensuse.org/opensuse/tumbleweed"
obs-home  := home_directory() / "Distrobox" / "obs"

obs-create:
    #!/usr/bin/env bash
    set -euo pipefail
    if ! podman ps -a --format '{{"{{"}}.Names}}' | grep -qx obs; then
      distrobox create --name obs --image {{obs-image}} --home {{obs-home}} --yes
    fi
    podman exec --user root obs zypper --non-interactive install osc git build >/dev/null
    echo "distrobox 'obs' ready. Run 'just obs-login' once as {{OBS_USER}}."

obs-login:
    distrobox enter obs -- osc -A {{OBS_API}} ls home:{{OBS_USER}}

obs-enter:
    distrobox enter obs

osc +args:
    {{OSC_RUN}} osc -A {{OBS_API}} {{args}}

vc pkg:
    #!/usr/bin/env bash
    set -euo pipefail
    name="$(echo {{pkg}} | cut -d/ -f2)"
    f="{{repo}}/{{pkg}}/${name}.changes"
    ts="$(date -u +"%a %b %e %H:%M:%S UTC %Y")"
    tmp="$(mktemp)"
    {
      printf -- "-------------------------------------------------------------------\n"
      printf -- "%s - %s <%s>\n\n" "$ts" "{{OBS_NAME}}" "{{OBS_EMAIL}}"
      printf -- "- \n\n"
      cat "$f"
    } > "$tmp"
    mv "$tmp" "$f"
    "${EDITOR:-vi}" "$f"

results pkg:
    #!/usr/bin/env bash
    set -euo pipefail
    IFS=/ read -r category name <<< "{{pkg}}"
    {{OSC_RUN}} osc -A {{OBS_API}} results "home:{{OBS_USER}}:${category}" "$name"

log pkg:
    #!/usr/bin/env bash
    set -euo pipefail
    IFS=/ read -r category name <<< "{{pkg}}"
    {{OSC_RUN}} osc -A {{OBS_API}} buildlog "home:{{OBS_USER}}:${category}" "$name" {{OBS_REPO}} {{OBS_ARCH}}

binaries pkg:
    #!/usr/bin/env bash
    set -euo pipefail
    IFS=/ read -r category name <<< "{{pkg}}"
    project="home:{{OBS_USER}}:${category}"
    out="{{repo}}/.binaries/${name}"
    mkdir -p "$out"
    {{OSC_RUN}} osc -A {{OBS_API}} getbinaries "$project" "$name" {{OBS_REPO}} {{OBS_ARCH}} -d "$out"
    echo "binaries -> $out"

obs-build pkg:
    #!/usr/bin/env bash
    set -euo pipefail
    IFS=/ read -r category name <<< "{{pkg}}"
    project="home:{{OBS_USER}}:${category}"
    dest="{{OSC_WORK}}/${project}/${name}"
    [ -d "$dest/.osc" ] || just checkout "{{pkg}}"
    (cd "$dest" && {{OSC_RUN}} osc -A {{OBS_API}} build {{OBS_REPO}} {{OBS_ARCH}})
