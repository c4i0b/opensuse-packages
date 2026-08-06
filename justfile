OBS_USER      := "caiobruno"
OBS_NAME      := "Caio Bruno"
OBS_EMAIL     := "cbrunofb@gmail.com"
OBS_API       := "https://api.opensuse.org"
OBS_REPO   := "opensuse_tumbleweed"
OBS_ARCHES := "x86_64 aarch64"
OBS_ARCH   := "x86_64"
OSC_RUN       := env_var_or_default("OSC_RUN", "distrobox enter obs --")
OSC_WORK      := home_directory() / "obs"
repo          := justfile_directory()

default:
    @just --list --unsorted

bootstrap:
    @command -v docker && docker --version || echo "docker MISSING"
    @command -v distrobox && distrobox --version || echo "distrobox MISSING"
    @command -v rsync && rsync --version | head -1 || echo "rsync MISSING"
    @command -v just && just --version
    @echo "osc runs inside the 'obs' distrobox (just obs-create); set OSC_RUN='' to use a host osc instead"

create-project category="tools" force="0":
    #!/usr/bin/env bash
    set -euo pipefail
    project="home:{{OBS_USER}}"
    tmp="$(mktemp)"
    if {{OSC_RUN}} osc -A {{OBS_API}} meta prj "$project" >/dev/null 2>&1; then
      if [ "{{force}}" != "1" ]; then
        echo "project $project already exists (force=1 to re-apply _project.meta.xml)"
        rm -f "$tmp"
        exit 0
      fi
    fi
    arches=""
    for a in {{OBS_ARCHES}}; do
      [ -n "$arches" ] && arches+="\\n"
      arches+="    <arch>$a</arch>"
    done
    sed -e "s|@@PROJECT@@|${project}|g" -e "s|@@REPO@@|{{OBS_REPO}}|g" -e "s|@@ARCHES@@|${arches}|g" \
      "{{repo}}/_project.meta.xml" > "$tmp"
    {{OSC_RUN}} osc -A {{OBS_API}} meta prj -F "$tmp" "$project"
    rm -f "$tmp"
    echo "project ready: $project"

checkout pkg:
    #!/usr/bin/env bash
    set -euo pipefail
    IFS=/ read -r category name <<< "{{pkg}}"
    project="home:{{OBS_USER}}"
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
    project="home:{{OBS_USER}}"
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
    project="home:{{OBS_USER}}"
    src="{{repo}}/{{pkg}}"
    dest="{{OSC_WORK}}/${project}/${name}"
    python3 "{{repo}}/opensuse-lint.py" "$src"/*.spec || { echo "lint FAILED — fix before push" >&2; exit 1; }
    [ -d "$dest/.osc" ] || just new-pkg "{{pkg}}"
    if [ -x "$src/bump.sh" ]; then ver="$(awk '/^Version:/{print $2; exit}' "$src"/*.spec)"; "$src/bump.sh" "$ver" || true; fi
    ex=(--exclude='.osc' --exclude='fetch.sh' --exclude='bump.sh' --exclude='VERSION' --exclude='BIN' --exclude='*.tar.gz' --exclude='*.zip')
    [ -f "$src/.obsignore" ] && ex+=(--exclude-from="$src/.obsignore")
    rsync -a --delete "${ex[@]}" "$src/" "$dest/"
    (cd "$dest" && {{OSC_RUN}} osc -A {{OBS_API}} addremove && {{OSC_RUN}} osc -A {{OBS_API}} st)
    if [ "${CI:-}" = "true" ]; then ok=y; else read -r -p "Commit ${name} to ${project}? [y/N] " ok; fi
    [ "$ok" = "y" ] || { echo aborted; exit 1; }
    (cd "$dest" && {{OSC_RUN}} osc -A {{OBS_API}} ci -m "{{msg}}")
    echo "pushed ${name} -> ${project}"

fetch pkg:
    #!/usr/bin/env bash
    set -euo pipefail
    dir="{{repo}}/{{pkg}}"
    if [ -x "$dir/fetch.sh" ]; then "$dir/fetch.sh"; else echo "no fetch.sh for {{pkg}}"; fi

build-image:
    docker build -f "{{repo}}/tools/build.Dockerfile" -t opensuse-packaging:dev "{{repo}}/tools"
    echo "image 'opensuse-packaging:dev' ready"

build pkg:
    #!/usr/bin/env bash
    set -euo pipefail
    dir="{{repo}}/{{pkg}}"
    name="$(echo {{pkg}} | cut -d/ -f2)"
    [ -x "$dir/fetch.sh" ] && "$dir/fetch.sh" || true
    if [ -f "$dir/Dockerfile" ]; then
      docker build -t "$name:dev" "$dir"
    elif ls "$dir"/*.spec >/dev/null 2>&1; then
      out="{{repo}}/.build/${name}"
      mkdir -p "$out"
      docker image inspect opensuse-packaging:dev >/dev/null 2>&1 || just build-image
      buildreqs=$(grep '^BuildRequires:' "$dir"/*.spec | sed 's/BuildRequires:\s*//;s/\s*$//' | tr '\n' ' ' || true)
      docker run --rm -e HOME=/tmp -v "$dir:/src" -v "$out:/out" -v "{{repo}}/tools/rpmlintrc:/rpmlintrc.local:ro" \
        opensuse-packaging:dev \
        bash -lc 'set -e; reqs="'"$buildreqs"'"; [ -n "$reqs" ] && zypper --non-interactive install --no-recommends $reqs >/dev/null 2>&1; cd /src; rpmbuild -bb -D "_topdir /tmp/rpmbuild" -D "_sourcedir /src" -D "_rpmdir /out" -D "debug_package %{nil}" *.spec; echo "--- rpmlint ---"; rint=(); for f in /src/*.rpmlintrc; do [ -f "$f" ] && rint+=(-r "$f"); done; rint+=(-r /rpmlintrc.local); rpmlint "${rint[@]}" /out/*/*.rpm 2>&1 | tee /tmp/rpmlint.out; if grep -qE ": E: " /tmp/rpmlint.out; then echo "rpmlint ERRORS -> fix before push" >&2; exit 1; fi'
      echo "RPMs -> $out"
    else
      echo "no Dockerfile or .spec in {{pkg}}" >&2; exit 1
    fi

gen-rust crate:
    #!/usr/bin/env bash
    set -euo pipefail
    docker image inspect opensuse-packaging:dev >/dev/null 2>&1 || just build-image
    mkdir -p "{{repo}}/.build/gen"
    docker run --rm -e HOME=/tmp -v "{{repo}}/.build/gen:/gen" opensuse-packaging:dev \
      bash -lc "rust2rpm -t opensuse -o /gen '{{crate}}'"
    echo "generated spec -> {{repo}}/.build/gen"

gen-go pkg:
    #!/usr/bin/env bash
    set -euo pipefail
    docker image inspect opensuse-packaging:dev >/dev/null 2>&1 || just build-image
    mkdir -p "{{repo}}/.build/gen"
    docker run --rm -e HOME=/tmp -v "{{repo}}/.build/gen:/gen" -w /gen opensuse-packaging:dev \
      bash -lc "go2rpm '{{pkg}}'"
    echo "generated spec -> {{repo}}/.build/gen"

run pkg +args:
    #!/usr/bin/env bash
    set -euo pipefail
    dir="{{repo}}/{{pkg}}"
    name="$(echo {{pkg}} | cut -d/ -f2)"
    if [ -f "$dir/BIN" ]; then bin="$(cat "$dir/BIN")"; else bin="$name"; fi
    if [ -f "$dir/Dockerfile" ]; then
      if [ -t 0 ] && [ -t 1 ]; then tty=(-it); else tty=(-i); fi
      docker run --rm "${tty[@]}" --network host --userns=keep-id \
        -e HOME=/tmp -e TERM -v "$PWD:$PWD" -w "$PWD" "$name:dev" {{args}}
    elif ls "$dir"/*.spec >/dev/null 2>&1; then
      out="{{repo}}/.build/${name}"
      rpm="$(ls "$out"/*/*.rpm 2>/dev/null | head -1 || true)"
      [ -n "$rpm" ] || { echo "no RPM in $out -- run 'just build {{pkg}}' first" >&2; exit 1; }
      if [ -t 0 ] && [ -t 1 ]; then tty=(-it); else tty=(-i); fi
      docker run --rm "${tty[@]}" -e HOME=/tmp -e BIN="${bin}" -v "$out:/rpms" \
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

lint:
    python3 opensuse-lint.py

lint-all:
    python3 opensuse-lint.py --all

obs-image := "registry.opensuse.org/opensuse/tumbleweed"
obs-home  := home_directory() / "Distrobox" / "obs"

obs-create:
    #!/usr/bin/env bash
    set -euo pipefail
    if ! docker ps -a --format '{{"{{"}}.Names}}' | grep -qx obs; then
      distrobox create --name obs --image {{obs-image}} --home {{obs-home}} --yes
    fi
    distrobox enter obs -- true >/dev/null
    docker exec --user root obs zypper --non-interactive install osc git build opi \
      cargo-packaging golang-packaging go cargo python-rpm-macros systemd-rpm-macros cmake >/dev/null
    echo "distrobox 'obs' ready. Run 'just obs-login' once as {{OBS_USER}}."

obs-login:
    distrobox enter obs -- osc -A {{OBS_API}} ls home:{{OBS_USER}}

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
    {{OSC_RUN}} osc -A {{OBS_API}} results "home:{{OBS_USER}}" "$name"

log pkg:
    #!/usr/bin/env bash
    set -euo pipefail
    IFS=/ read -r category name <<< "{{pkg}}"
    {{OSC_RUN}} osc -A {{OBS_API}} buildlog "home:{{OBS_USER}}" "$name" {{OBS_REPO}} {{OBS_ARCH}}
