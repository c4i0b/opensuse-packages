#!/usr/bin/env python3
"""opensuse-packages spec linter — catches CI-only mistakes locally.

Usage:
  opensuse-lint.py             DEFAULT: uncommitted working tree
  opensuse-lint.py --all       lint every spec under packages/
  opensuse-lint.py <spec>...   lint specific spec paths
"""
from __future__ import annotations
import argparse, json, re, subprocess, sys, tempfile
from dataclasses import dataclass
from pathlib import Path

if sys.stdout.isatty():
    R, Y, G, D, N = ("\033[31m", "\033[33m", "\033[32m", "\033[2m", "\033[0m")
else:
    R = Y = G = D = N = ""

FAIL, WARN, OK = "FAIL", "WARN", "OK"
_GLYPH = {FAIL: "✗", WARN: "!", OK: "✓"}
_COLOR = {FAIL: R, WARN: Y, OK: G}


@dataclass
class Finding:
    severity: str
    code: str
    message: str
    line: int | None = None


@dataclass
class SpecModel:
    path: Path
    text: str
    lines: list[str]
    pkgdir: Path


def load(path: Path) -> SpecModel:
    path = path.resolve()
    text = path.read_text(errors="replace")
    return SpecModel(path, text, text.splitlines(), path.parent)


# --- structural checks -------------------------------------------------------

def check_summary(spec: SpecModel) -> list[Finding]:
    m = re.search(r"^Summary:\s*(.+?)\s*$", spec.text, re.M)
    if not m:
        return [Finding(FAIL, "summary", "missing `Summary:` field")]
    if m.group(1).endswith("."):
        return [Finding(WARN, "summary-period", "`Summary:` should not end with a period")]
    return []


def check_release(spec: SpecModel) -> list[Finding]:
    m = re.search(r"^Release:\s*(.+?)\s*$", spec.text, re.M)
    if not m:
        return [Finding(FAIL, "release", "missing `Release:` field")]
    val = re.sub(r"%\{.*?\}", "", m.group(1).split("#")[0]).strip()
    if not re.fullmatch(r"\d+", val):
        return [Finding(FAIL, "release", f"`Release:` must be an integer (got `{m.group(1)}`)")]
    return []


def check_url(spec: SpecModel) -> list[Finding]:
    if not re.search(r"^URL:\s*\S", spec.text, re.M):
        return [Finding(WARN, "url", "missing `URL:` field")]
    return []


def check_license(spec: SpecModel) -> list[Finding]:
    if not re.search(r"^License:\s*\S", spec.text, re.M):
        return [Finding(FAIL, "license", "missing `License:` field")]
    return []


# --- build system checks -----------------------------------------------------

_BUILDTOOL_MAP = {
    "%pyproject_wheel": ["pip", "python-rpm-macros"],
    "%pyproject_install": ["pip"],
    "%meson": ["meson"],
    "%cmake": ["cmake"],
    "%cmake_build": ["cmake"],
    "%cmake_install": ["cmake"],
    "%ctest": ["cmake"],
    "%cargo_build": ["cargo-packaging"],
    "%cargo_install": ["cargo-packaging"],
    "%goprep": ["golang-packaging"],
    "%gobuild": ["golang-packaging"],
    "%goinstall": ["golang-packaging"],
    "%gosrc": ["golang-packaging"],
    "%gem_build": ["ruby"],
    "%gem_install": ["ruby"],
}


def check_buildtool_buildreqs(spec: SpecModel) -> list[Finding]:
    buildreqs = "\n".join(
        l for l in spec.lines if l.strip().startswith("BuildRequires:")
    ).lower()
    out = []
    for macro, required in _BUILDTOOL_MAP.items():
        if macro not in spec.text:
            continue
        for pkg in required:
            if pkg.lower() not in buildreqs:
                out.append(Finding(WARN, "buildtool-buildreqs",
                    f"uses {macro} but missing BuildRequires: {pkg}"))
    if "%pyproject_wheel" in spec.text and re.search(r"^BuildArch:\s*noarch", spec.text, re.M):
        if "%python_subpackages" not in spec.text:
            out.append(Finding(WARN, "pyproject-nosubpackages",
                "noarch spec uses %pyproject_* without %python_subpackages — "
                "multi-flavor install will produce unpackaged files; "
                "use `python3 -m pip` directly or add %python_subpackages"))
    return out


def check_pyproject_flavor(spec: SpecModel) -> list[Finding]:
    if "%pyproject_wheel" not in spec.text and "%pyproject_install" not in spec.text:
        return []
    if "%python_subpackages" in spec.text and "@BUILD_FLAVOR@" in spec.text:
        return []
    return [Finding(WARN, "pyproject-flavor",
        "uses multi-flavor `%pyproject_wheel`/`%pyproject_install` without the flavor "
        "machinery (`%python_subpackages` + `%global flavor @BUILD_FLAVOR@`) — these expand "
        "to every python flavor and fail (e.g. python314 not installed); use "
        "`%python3_pyproject_wheel`/`%python3_pyproject_install` for a single default-flavor build")]


def _parse_pyproject_deps(text: str) -> list[str]:
    m = re.search(r"^dependencies\s*=\s*\[(.*?)^\]", text, re.S | re.M)
    if not m:
        return []
    out = []
    for entry in re.findall(r'"([^"]+)"', m.group(1)):
        if ";" in entry:
            continue
        name = re.split(r"[<>=!~]", entry, maxsplit=1)[0].strip()
        if name:
            out.append(name)
    return out


def _parse_cargo_deps(text: str) -> list[str]:
    m = re.search(r"^\[dependencies\]\s*\n(.*?)(?=^\[|\Z)", text, re.S | re.M)
    if not m:
        return []
    out = []
    for line in m.group(1).splitlines():
        line = line.strip()
        m2 = re.match(r"^([a-zA-Z0-9_-]+)\s*=", line)
        if m2:
            out.append(m2.group(1))
    return out


def _parse_npm_deps(text: str) -> list[str]:
    try:
        pkg = json.loads(text)
    except json.JSONDecodeError:
        return []
    return list(pkg.get("dependencies", {}).keys())


_MANIFEST_PARSERS = [
    ("pyproject.toml", _parse_pyproject_deps),
    ("Cargo.toml", _parse_cargo_deps),
    ("package.json", _parse_npm_deps),
]


def check_manifest_requires(spec: SpecModel) -> list[Finding]:
    for filename, parser in _MANIFEST_PARSERS:
        manifest = spec.pkgdir / filename
        if not manifest.exists():
            continue
        deps = parser(manifest.read_text(errors="replace"))
        if not deps:
            continue
        requires_blob = "\n".join(
            l for l in spec.lines if l.strip().startswith("Requires:")
        ).lower().replace("-", "").replace("_", "")
        out = []
        for dep in deps:
            dep_norm = dep.lower().replace("-", "").replace("_", "")
            if dep_norm not in requires_blob:
                out.append(Finding(WARN, "manifest-requires",
                    f"missing requires: {dep} (declared in {filename})"))
        return out
    return []


# --- packaging checks --------------------------------------------------------

def check_dir_ownership(spec: SpecModel) -> list[Finding]:
    DIR_PAIRS = [
        (r"%\{_datadir\}/icons/hicolor/[^/]+/apps/\S", r"%dir.*icons/hicolor", "icon"),
        (r"%\{_datadir\}/zsh/site-functions/\S", r"%dir.*zsh", "zsh completion"),
        (r"%\{_datadir\}/fish/vendor_completions\.d/\S", r"%dir.*fish", "fish completion"),
    ]
    # Dirs under /usr/share owned by the distro (filesystem and friends):
    # files there don't need %dir ownership. Anything else is package-owned
    # and OBS check-filelist FAILs on it (red: masscan /usr/share/masscan).
    SYSTEM_DATADIRS = {
        "appdata", "applications", "backgrounds", "bash-completion",
        "color", "dict", "doc", "fish", "fonts", "icons", "licenses",
        "locale", "man", "metainfo", "mime", "mime-info", "polkit-1",
        "sounds", "systemd", "themes", "wallpapers", "zsh",
    }
    out = []
    files_lines = []
    in_files = False
    for line in spec.lines:
        if _SECTION_RE.match(line):
            in_files = line.strip().startswith("%files")
        elif in_files:
            files_lines.append(line)
    for i, line in enumerate(spec.lines, 1):
        stripped = line.strip()
        if stripped.startswith("%dir") or stripped.startswith("#"):
            continue
        for file_pat, dir_pat, label in DIR_PAIRS:
            if re.search(file_pat, stripped):
                if not re.search(dir_pat, spec.text, re.M):
                    out.append(Finding(FAIL, "dir-ownership",
                        f"{label} file without any %dir ownership — "
                        f"OBS check-filelist will FAIL", line=i))
                break
    for line in files_lines:
        stripped = line.strip()
        if stripped.startswith(("%dir", "%doc", "%license", "#")):
            continue
        m = re.match(r"%\{_datadir\}/([a-zA-Z0-9._+-]+)/\S", stripped)
        if not m or m.group(1) in SYSTEM_DATADIRS:
            continue
        if not re.search(rf"%dir\s+.*%\{{_datadir\}}/?{re.escape(m.group(1))}\b", spec.text):
            out.append(Finding(FAIL, "dir-ownership",
                f"%{{_datadir}}/{m.group(1)}/ file without %dir ownership — "
                f"the dir is package-owned, OBS check-filelist will FAIL"))
    return out


_SECTION_RE = re.compile(r"^%([a-zA-Z]+)\b")

# rpm pseudo-sections that terminate the previous section while scanning
# %build. Build-system macros (%meson, %meson_build, %cmake, ...) are also
# bare %-words at line start and must NOT count as section ends, or a real
# meson/cmake %build looks like "no real build" (red: mangojuice flagged
# as unclassified prebuilt).
_SECTION_NAMES = frozenset({
    "prep", "build", "install", "check", "files", "changelog", "clean",
    "package", "description", "pre", "post", "preun", "postun",
    "pretrans", "posttrans", "verifyscript", "triggerin", "triggerun",
    "triggerpostun", "triggerprein", "end",
})


def _is_section(line: str) -> bool:
    m = _SECTION_RE.match(line)
    return bool(m) and m.group(1).lower() in _SECTION_NAMES

# Prebuilt binary classification. OBS brp-strip runs on every prebuilt binary;
# only Bun-compiled single-file executables (app JS payload appended to the ELF)
# get corrupted by stripping. Go/Rust/Electron binaries are strip-safe and must
# NOT be flagged. Register new prebuilt packages here so the lint knows what to
# check for; unknown prebuilts get a WARN asking to be classified.
PREBUILT_ORIGIN = {
    # upstream-RPM repackage: Electron bundle under
    # %{_libdir}, strip disabled in the spec itself (stripping corrupts the
    # embedded snapshot). superfile/television/ytm-player build from source
    # since 2026-11 — no prebuilt registry entries left.
    "pear-desktop": "electron",
    # rpm-repackage of the upstream Electron bundles (strip disabled in each
    # spec: stripping corrupts the embedded snapshot)
    "opencode-desktop": "electron",
    "desktop-plus": "electron",
    "hydra-launcher": "electron",
    # upstream-RPM repackage of the official Rust/Tauri binary: strip-safe
    "limusic": "rust",
    # upstream-RPM repackage bundling a JVM + Skiko (Skia) tree: strip off,
    # tree kept byte-identical
    "spotube": "native",
    # upstream release tarball with mixed C/Go prebuilt ELFs (32-bit
    # Ventoy2Disk, Go web UI): strip-safe, spec disables strip to keep the
    # upstream tree byte-identical
    "ventoy": "native",
    # bun-compiled single-file executables (payload appended after the ELF
    # section strip removes): spec carries __os_install_post %{nil}
    "omo": "bun",
    # npm prebuilds (@lydell/node-pty ELF addons): strip-safe native ELFs
    "rea-agents": "native",
    # manylinux wheels installed into the vendored venv: strip-safe .so
    # payloads (openclaw is noarch, exempt from this check)
    "hermes-agent": "native",
}

_STRIP_GUARD = re.compile(
    r"^%(?:global|define)\s+__os_install_post\s+%\{nil\}", re.M
)


def _real_build(lines: list[str]) -> bool:
    has_build = False
    in_build = False
    for line in lines:
        if re.match(r"^%build\b", line):
            in_build = True
            continue
        if in_build:
            if _is_section(line):
                in_build = False
            elif line.strip():
                has_build = True
    return has_build


def _infer_origin(spec: SpecModel) -> str | None:
    has_desktop = re.search(r"^Source\d+:\s*\S+\.desktop\s*$", spec.text, re.M)
    installs_libdir = r"%\{_libdir\}" in spec.text
    if has_desktop and installs_libdir:
        return "electron"
    return None


def check_prebuilt_strip(spec: SpecModel) -> list[Finding]:
    if re.search(r"^BuildArch:\s*noarch\s*$", spec.text, re.M):
        return []
    if _real_build(spec.lines):
        return []
    sources_line = next((l for l in spec.lines if re.match(r"^Source0:", l)), "")
    if not any(ext in sources_line.lower() for ext in (".tar.gz", ".tar.xz", ".tgz", ".zip")):
        return []
    name = spec.path.parent.name
    origin = PREBUILT_ORIGIN.get(name) or _infer_origin(spec)
    if origin is None:
        return [Finding(WARN, "prebuilt-unclassified",
            f"prebuilt binary Source + no real %build: classify `{name}` in PREBUILT_ORIGIN "
            "(opensuse-lint.py) — 'bun' needs %global __os_install_post %{nil}, "
            "any other origin (go/rust/electron) is strip-safe")]
    if origin != "bun":
        return []
    if _STRIP_GUARD.search(spec.text):
        return []
    return [Finding(FAIL, "prebuilt-strip",
        "Bun-compiled prebuilt binary missing `%global __os_install_post %{nil}` — "
        "OBS brp-strip would corrupt the appended payload")]


def check_exclusivearch(spec: SpecModel) -> list[Finding]:
    if re.search(r"^ExclusiveArch:\s*%\{go_arches\}", spec.text, re.M):
        # red: superfile excluded on every arch — %{go_arches} is no longer
        # defined in the Tumbleweed prjconf, so the macro expands empty
        return [Finding(FAIL, "go-arches-undefined",
            "`ExclusiveArch: %{go_arches}` — the macro is not defined in the "
            "Tumbleweed prjconf and expands empty (excludes every arch); "
            "list arches explicitly")]
    if re.search(r"^BuildArch:\s*noarch\s*$", spec.text, re.M):
        return []
    if _real_build(spec.lines):
        return []
    if not re.search(r"^ExclusiveArch:", spec.text, re.M):
        return [Finding(WARN, "no-exclusivearch",
            "no `ExclusiveArch:` — prebuilt packages should restrict to their arch")]
    return []


# --- hygiene checks ----------------------------------------------------------

# Only same-prefix repeats are duplicates: BuildRequires + Requires of the
# same name is a legitimate pattern (interpreter needed in %check and at
# runtime, e.g. nodejs24 in devcontainers-cli, libusb-1_0 in
# python3-libusb-package).
def check_duplicate_requires(spec: SpecModel) -> list[Finding]:
    PREFIXES = ("Requires:", "BuildRequires:", "Recommends:", "Suggests:")
    out: list[Finding] = []
    seen: dict[str, str] = {}
    for i, line in enumerate(spec.lines, 1):
        stripped = line.strip()
        prefix = next((p for p in PREFIXES if stripped.startswith(p)), None)
        if not prefix:
            continue
        name = stripped[len(prefix):].strip().lower()
        if not name:
            continue
        key = f"{prefix}:{name}"
        if key in seen:
            out.append(Finding(FAIL, "duplicate-requires",
                f"duplicate {prefix[:-1]}: {name.split()[0]} (first at line {seen[key]})",
                line=i))
        else:
            seen[key] = str(i)
    return []


def check_tracked_archives(repo: Path) -> list[Finding]:
    result = subprocess.run(
        ["git", "ls-files"], capture_output=True, text=True, cwd=repo
    )
    bad = [f for f in result.stdout.splitlines()
           if f.endswith((".tar.gz", ".tgz", ".tar.xz", ".zip", ".rpm", ".deb", ".AppImage", ".obscpio", ".whl"))]
    if bad:
        return [Finding(FAIL, "tracked-archive",
            f"{len(bad)} archive(s) tracked in git: {', '.join(bad[:3])}"
            + ("..." if len(bad) > 3 else ""))]
    return []


# Scripts CI executes directly (tools/*.sh, .github/scripts/*.sh, per-
# package bump.sh/fetch.sh) must carry the exec bit: a lost +x aborts the
# autoupdate bot's bump loop with "Permission denied" (red: tools/bump.sh
# lost it and every central-bump package skipped its update).
def check_script_exec_bits(repo: Path) -> list[Finding]:
    result = subprocess.run(
        ["git", "ls-files", "-s"], capture_output=True, text=True, cwd=repo
    )
    out = []
    for entry in result.stdout.splitlines():
        meta, _, path = entry.partition("\t")
        if (path.endswith(".sh") or path.split("/")[-1] in ("bump.sh", "fetch.sh")) \
                and meta.startswith("100644"):
            out.append(Finding(FAIL, "script-exec-bit",
                f"{path} is tracked without the exec bit — CI runs it "
                f"directly and fails with 'Permission denied'"))
    return out


# Files a blind `git add -A` would swallow must stay tiny: committable
# content in this repo tops out ~35 KB (specs/docs), so anything over
# 5 MB — two orders of magnitude above the norm — is a fetched payload
# that lost its ignored extension (GitHub warns at 50 MB and rejects
# the push at 100 MB). Gitignored files (vendor archives, fetched
# tarballs, .rpm payloads) can never be committed, so only committable
# ones are flagged.
# Red: the omo Bun payload (202 MB, no extension) entered the aarch64-drop
# commit and the push bounced with GH001 until filter-branch removed it.
_GITHUB_SIZE_LIMIT = 5 * 1024 * 1024

def check_oversize_payloads(repo: Path) -> list[Finding]:
    out = []
    for f in (repo / "packages").rglob("*"):
        if not f.is_file() or f.stat().st_size <= _GITHUB_SIZE_LIMIT:
            continue
        r = subprocess.run(
            ["git", "check-ignore", "-q", str(f)],
            cwd=repo, capture_output=True,
        )
        if r.returncode == 0:
            continue  # ignored: can never reach a commit
        out.append(Finding(FAIL, "oversize-payload",
            f"{f.relative_to(repo)} is {f.stat().st_size // 1024} KB — over "
            f"the 5 MB ceiling for committable files (norm here is ~35 KB; "
            f"GitHub rejects pushes at 100 MB). It is almost certainly a "
            f"fetched payload without an ignored extension: fetch it under "
            f"an ignored name or remove it."))
    return out


# Archives are legitimately absent from a clean checkout by design: the
# upstream tarball is fetched server-side via _service, and Rust vendor
# archives (vendor.tar.zst, generated client-side by cargo_vendor) are
# gitignored and only live on OBS. Based on the check_tracked_archives
# extension list, plus .tar.zst (the vendor-archive format).
_ARCHIVE_EXTS = (".tar.gz", ".tgz", ".tar.xz", ".tar.zst", ".zip", ".rpm", ".deb", ".AppImage", ".obscpio", ".whl")


def check_local_sources(spec: SpecModel) -> list[Finding]:
    name_m = re.search(r"^Name:\s*(\S+)", spec.text, re.M)
    ver_m = re.search(r"^Version:\s*(\S+)", spec.text, re.M)
    subs = {"name": name_m.group(1) if name_m else spec.path.stem,
            "version": ver_m.group(1) if ver_m else ""}
    out = []
    for i, line in enumerate(spec.lines, 1):
        m = re.match(r"^Source\d*:\s*(\S+)", line)
        if not m:
            continue
        value = m.group(1)
        if "://" in value:
            continue
        value = re.sub(r"%\{(name|version)\}", lambda mm: subs[mm.group(1)], value)
        if "%{" in value:
            continue  # unresolvable macro — cannot check statically
        if value.endswith(_ARCHIVE_EXTS):
            continue  # _service fetch / client-side vendor archive, never local
        if not (spec.pkgdir / value).is_file():
            out.append(Finding(FAIL, "local-source",
                f"`{value}` declared as Source but missing from the package dir — "
                f"rpmbuild fails on a missing source at build time", line=i))
    return out


# --- registry + runner -------------------------------------------------------

def check_source_version_macro(spec: SpecModel) -> list[Finding]:
    m = re.search(r"^Version:\s*(\S+)", spec.text, re.M)
    if not m:
        return []
    ver = m.group(1)
    out = []
    for i, line in enumerate(spec.lines, 1):
        if re.match(r"^Source\d*:", line) and ver in line and "%{version}" not in line.lower():
            out.append(Finding(WARN, "source-version-macro",
                f"Source contains hardcoded version `{ver}` — use `%{{version}}` macro for auto-update compatibility",
                line=i))
    return []


# Highest Go the OBS go_modules source-service host runs. A go.mod "go"
# directive above this breaks the _service stage ("go mod download failed",
# package broken before rpmbuild, no logfile) — GOTOOLCHAIN is local on the
# service host, no toolchain auto-download. Bump after confirming on OBS
# (e.g. re-enable go_modules on a canary package). Red: nexttrace 1.7.6.
OBS_GO_MODULES_GO = (1, 26)


def check_go_modules_toolchain(spec: SpecModel) -> list[Finding]:
    m = re.search(r"^BuildRequires:\s*golang\(API\)\s*>=\s*(\d+)\.(\d+)",
                  spec.text, re.M)
    if not m:
        return []
    floor = (int(m.group(1)), int(m.group(2)))
    if floor <= OBS_GO_MODULES_GO:
        return []
    i = spec.lines.index(next(l for l in spec.lines if "golang(API)" in l)) + 1
    # Above the service ceiling the server-side go_modules cannot run: the
    # vendor archive must come client-side (vendor.tar.zst + BuildRequires:
    # zstd, see dnscontrol/nexttrace), not from the service.
    if "Source1:        vendor.tar.zst" in spec.text:
        if not re.search(r"^BuildRequires:\s*zstd\s*$", spec.text, re.M):
            return [Finding(FAIL, "go-modules-toolchain",
                "client-side vendor.tar.zst needs `BuildRequires: zstd` "
                "(rpmuncompress), the build fails in %prep without it", line=i)]
        return []
    if re.search(r"^Source1:\s*vendor\.tar\.gz\s*$", spec.text, re.M):
        return [Finding(FAIL, "go-modules-toolchain",
            f"golang(API) >={floor[0]}.{floor[1]} but Source1 is "
            "vendor.tar.gz (server-side go_modules): the OBS source-service "
            f"host runs go {'.'.join(map(str, OBS_GO_MODULES_GO))} with "
            "GOTOOLCHAIN=local, so `go mod download` fails before rpmbuild "
            "(package broken, no logfile). Generate vendor.tar.zst "
            "client-side (`go mod vendor && tar --zstd -cf vendor.tar.zst "
            "vendor`), drop go_modules from _service and add "
            "`BuildRequires: zstd`", line=i)]
    return []


def check_go_directive_clamp(spec: SpecModel) -> list[Finding]:
    # red: crush 0.102.0 — upstream bumped go.mod to `go 1.27.4` while the
    # slowroll build worker runs go 1.27.3 (GOTOOLCHAIN=local, offline: no
    # toolchain download), so %build died with "go.mod requires go >= 1.27.4"
    # on slowroll while Tumbleweed stayed green. Any client-side vendored go
    # package hits this on the next upstream bump; the %prep clamp pins the
    # directive to the buildroot toolchain.
    if not re.search(r"go build -mod=vendor", spec.text):
        return []
    if "go env GOVERSION" in spec.text:
        return []
    i = spec.lines.index(next(l for l in spec.lines
                              if "go build -mod=vendor" in l)) + 1
    return [Finding(FAIL, "go-directive-clamp",
        "client-side vendored go build without a go.mod directive clamp: "
        "upstream bumps the `go` directive past the oldest build worker's Go "
        "(slowroll lags Tumbleweed; GOTOOLCHAIN=local cannot download a "
        "toolchain) and %build dies with `go.mod requires go >= X` (red: "
        "crush 0.102.0). Clamp the floors in %prep after %autosetup — DOWN "
        "only, never up (raising an old go.mod directive activates go >= 1.17 "
        "module-graph pruning and breaks stale vendored trees; red: ctop "
        "0.7.7), deps' floors in vendor/modules.txt included: copy the "
        "clamp() block from packages/crush/crush.spec.",
        line=i)]


def check_date_tag_service(spec: SpecModel) -> list[Finding]:
    # red: hand-written _service files put the dot-sanitized Version into the
    # download path, but upstream tags carry dashes (2026-08-10 vs 2026.08.10)
    # and the fetch 404s server-side. The raw tag belongs in %global tag and
    # in the _service path; only the filename param uses the dot form.
    m = re.search(r"^%global\s+tag\s+(\d{4}-\d{2}-\d{2})\s*$", spec.text, re.M)
    if not m:
        return []
    tag = m.group(1)
    svc = spec.path.parent / "_service"
    if not svc.is_file():
        return []
    text = svc.read_text()
    dots = tag.replace("-", ".")
    if f"tags/{dots}" in text:
        return [Finding(FAIL, "date-tag-path",
            f"_service download path uses the dot form `{dots}` — upstream "
            f"tags are dashed ({tag}); the fetch 404s server-side. Keep the "
            "raw tag in the path and the dot form only in filename/Version.")]
    if f"tags/{tag}" not in text:
        return [Finding(WARN, "date-tag-path",
            f"_service path does not reference the raw tag `{tag}` — "
            "verify the URL matches the tag exactly.")]
    return []


def check_service_download_url(spec: SpecModel) -> list[Finding]:
    # red: dropping a multi-arch source left a <service name="download_url">
    # stub with protocol/host but no path — the OBS source-service stage dies
    # with "ERROR: need url or host, path" and the package goes broken with
    # no buildlog. Removing an arch means removing the whole service block.
    svc = spec.path.parent / "_service"
    if not svc.is_file():
        return []
    text = svc.read_text()
    out = []
    for i, block in enumerate(
        re.findall(r"<service name=\"download_url\">.*?</service>", text, re.S), 1
    ):
        for param in ("path", "filename"):
            if f'<param name="{param}">' not in block:
                out.append(Finding(FAIL, "service-download-url",
                    f"_service download_url entry #{i} lacks `{param}` — the "
                    "source service fails on OBS with 'need url or host, path' "
                    "and the package breaks with no buildlog. Leftover stub "
                    "from a dropped arch? Delete the whole service block."))
    return out


def check_offline_installs(spec: SpecModel) -> list[Finding]:
    # red: OBS build workers are offline — any dependency install that
    # resolves against a registry/index at build time fails there. Two
    # sanctioned offline models exist in this repo (see templates/):
    # npm-bundle (local-npm-registry serving vendored node_modules/ tarballs)
    # and python-venv-wheels (uv/pip with --no-index --find-links).
    script = re.sub(r"\\\n\s*", " ", spec.text)
    out = []
    for cmd in re.findall(r"^.*(?:npm|pip|uv)\b.*$", script, re.M):
        if cmd.lstrip().startswith("#"):
            continue  # comment, not a build command
        # npm ci/add resolve against the registry exactly like npm install
        is_npm = re.search(r"(?<![\w-])npm(?:-\d+)?\s+((?:-\S+\s+|\S+=\S+\s+)*)(?:install|ci|add)\b", cmd)
        is_npm = is_npm and "local-npm-registry" not in cmd
        is_pip = re.search(r"(?:uv\s+)?pip\s+(?:-\S+\s+)*(?:install|sync)\b", cmd)
        is_uv_sync = re.search(r"(?<![\w-])uv\s+sync\b", cmd)
        if is_uv_sync and "--offline" not in cmd:
            out.append(Finding(FAIL, "offline-build",
                f"`uv sync` at build time ({cmd.strip()[:60]}...) resolves "
                "against PyPI — OBS workers are offline. Use the "
                "python-venv-wheels model (templates/"
                "python-venv-wheels.spec.tpl): vendored wheels + "
                "--no-index --find-links."))
        if is_npm and "local-npm-registry" not in script:
            out.append(Finding(FAIL, "offline-build",
                f"`npm install` at build time ({cmd.strip()[:60]}...) resolves "
                "against registry.npmjs.org — OBS workers are offline. Use the "
                "npm-bundle model (templates/npm-bundle.spec.tpl): vendor "
                "node_modules/ client-side and install through "
                "BuildRequires: local-npm-registry."))
        if is_pip and "--no-index" not in cmd:
            out.append(Finding(FAIL, "offline-build",
                f"`pip/uv install` without --no-index ({cmd.strip()[:60]}...) "
                "resolves against PyPI at build time — OBS workers are offline. "
                "Use the python-venv-wheels model (templates/"
                "python-venv-wheels.spec.tpl): vendored wheels + "
                "--no-index --find-links."))
    return out


def check_vendor_pin_drift(spec: SpecModel) -> list[Finding]:
    # red class: python-venv-wheels specs pin build-backend wheels (e.g.
    # setuptools==X) that fetch.sh --vendor must download into wheels.tar.zst.
    # Bumping one side without the other fails the OBS build late and
    # confusingly ("no matching distribution found" from --no-index). The
    # same == pins must appear verbatim in the spec and in fetch.sh.
    if "wheels.tar.zst" not in spec.text:
        return []
    fetch = spec.pkgdir / "fetch.sh"
    if not fetch.is_file():
        return []
    ftext = fetch.read_text(errors="replace")
    pin_re = r"[A-Za-z0-9_.-]+==[A-Za-z0-9_.!+*-]+"
    spec_code = "\n".join(l for l in spec.lines if not l.lstrip().startswith("#"))
    fetch_code = "\n".join(
        l for l in ftext.splitlines() if not l.lstrip().startswith("#")
    )
    out = []
    for pin in sorted(set(re.findall(pin_re, spec_code))):
        if pin not in fetch_code:
            out.append(Finding(FAIL, "vendor-pin-drift",
                f"`{pin}` pinned in the spec but absent from fetch.sh — the "
                "wheel is not in wheels.tar.zst and the offline install "
                "fails on OBS. Re-run `fetch.sh --vendor` and keep the pins "
                "identical in both files."))
    for pin in sorted(set(re.findall(pin_re, fetch_code))):
        if pin not in spec_code:
            out.append(Finding(FAIL, "vendor-pin-drift",
                f"`{pin}` downloaded by fetch.sh but not pinned in the spec "
                "— the spec's offline install asks for a different version "
                "than the vendored wheel. Keep the pins identical in both "
                "files."))
    return out


def check_upstream_vendored(spec: SpecModel) -> list[Finding]:
    # red: solidcraft 0.43.0 — an `upstream` file on a package whose bump
    # needs a client-side re-vendor (cargo_vendor/go vendor manual
    # vendor.tar.*, npm node_modules.obscpio, wheels.tar.zst, package-lock)
    # lets the autoupdate bot bump the spec while the vendor archive keeps
    # the OLD Cargo.lock/dependency tree. The OBS build then either fails
    # on a missing crate (cap-std) or, worse, builds the new source
    # against the old dependency tree. Since tools/revendor.sh the bot
    # re-vendors automatically (and reverts the bump when the re-vendor
    # fails), so `upstream` is allowed only when revendor.sh handles the
    # package's model: fetch.sh present, client-side go vendor, or
    # cargo_build. Packages with no revendor model (pinvendor overlays,
    # server-side go_modules needs none) stay manual.
    vendored = bool(re.search(r"^Source[0-9]+:.*vendor\.tar", spec.text, re.M)) or any(
        (spec.pkgdir / n).exists()
        for n in ("node_modules.obscpio", "wheels.tar.zst", "package-lock.json")
    )
    if not vendored or not (spec.pkgdir / "upstream").is_file():
        return []
    revendorable = (spec.pkgdir / "fetch.sh").is_file() or bool(
        re.search(r"go build -mod=vendor", spec.text)
        and (spec.pkgdir / "_service").is_file()
        and not re.search(r'service name="go_modules"',
                          (spec.pkgdir / "_service").read_text())
    ) or bool(re.search(r"cargo_build|__cargo", spec.text))
    # pinvendor overlays (pdfcraft/photocraft): duplicate git crates
    if (spec.pkgdir.parent.parent / "tools" / f"pinvendor-{spec.pkgdir.name}.py").is_file():
        revendorable = True
    # server-side go_modules: OBS regenerates the vendor archive itself,
    # the bot needs no client-side model
    if (spec.pkgdir / "_service").is_file() and re.search(
            r'service name="go_modules"',
            (spec.pkgdir / "_service").read_text()):
        revendorable = True
    if revendorable:
        return []
    return [Finding(FAIL, "upstream-on-vendored",
        "package needs a client-side re-vendor on bump that tools/revendor.sh "
        "does not model but also has an `upstream` file — the autoupdate bot "
        "would bump the spec without regenerating the vendor archive (stale "
        "Cargo.lock; red: solidcraft 0.43.0 missing cap-std). Remove the "
        "`upstream` file or teach revendor.sh the model.")]



def check_lockfile_version(spec: SpecModel) -> list[Finding]:
    # red: a version bump that does not re-vendor — the spec moves to the new
    # version while package-lock.json (and node_modules.obscpio / wheels
    # vendor) still pin the old one. The OBS build then fails late and
    # confusingly (npm resolves the old tree, %check sees the old --version).
    # Catch it at lint/validate time instead: re-run fetch.sh --vendor.
    lock = spec.pkgdir / "package-lock.json"
    if not lock.is_file():
        return []
    m = re.search(r"^Version:\s*(\S+)", spec.text, re.M)
    if not m:
        return []
    try:
        locked = json.loads(lock.read_text()).get("version")
    except (OSError, ValueError):
        return []
    if locked and locked != m.group(1):
        return [Finding(FAIL, "lockfile-version-drift",
            f"package-lock.json pins `{locked}` but the spec says "
            f"`{m.group(1)}` — a bump without re-vendoring. Re-run the "
            "package's `fetch.sh --vendor` so the lock, the vendor archive "
            "and the spec stay in sync.")]
    return []


def check_rpm_payload_extract(spec: SpecModel) -> list[Finding]:
    # red: pear-desktop 3.12.1 (fedora-packages twin) — electron-builder
    # ships RPMv4 containers that libarchive/bsdtar cannot parse, and old
    # cpio misreads payload sizes; %prep died on "Unrecognized archive
    # format" in every chroot. rpm2archive streams a tar on every rpm
    # version, so bundled .rpm payloads must go through it.
    if not re.search(r"^Source\d*:\s*\S*\.rpm", spec.text, re.M):
        return []
    hits = [i for i, l in enumerate(spec.lines, 1)
            if not l.lstrip().startswith("#")
            and re.search(r"(bsdtar\s+-|rpm2cpio)", l)]
    return [Finding(FAIL, "rpm-payload-extract",
        "bundled .rpm payload extracted with bsdtar/rpm2cpio — use "
        "`rpm2archive %{SOURCE0} > payload.tgz && tar -xzf payload.tgz` "
        "(libarchive cannot parse RPMv4 containers, cpio misreads payload "
        "sizes)", line=i) for i in hits]


# Templates must render into conforming packages: fill every placeholder
# with dummy values and run the same invariants over the rendered spec
# (render-pass inherited from the original port). local-source
# is waived: scaffolds ship their local Source files at creation time.
def check_templates_render(repo: Path) -> list[Finding]:
    out = []
    for tpl in sorted((repo / "templates").glob("*.spec.tpl")):
        rendered = re.sub(r"__[A-Z0-9_]+__", "dummy", tpl.read_text())
        rendered = rendered.replace("python3.1X", "python3.14")
        with tempfile.TemporaryDirectory() as td:
            pkgdir = Path(td) / "tplpkg"
            pkgdir.mkdir()
            spec_path = pkgdir / (tpl.stem.replace(".spec", "") + ".spec")
            spec_path.write_text(rendered)
            spec = load(spec_path)
            fails = [f for check in _CHECKS for f in check(spec)
                     if f.severity == FAIL and f.code != "local-source"]
        for f in fails:
            out.append(Finding(FAIL, "template-render",
                f"{tpl.name} renders non-conforming: [{f.code}] {f.message}"))
    return out


_CHECKS = [
    check_summary,
    check_release,
    check_url,
    check_license,
    check_source_version_macro,
    check_buildtool_buildreqs,
    check_pyproject_flavor,
    check_manifest_requires,
    check_dir_ownership,
    check_prebuilt_strip,
    check_exclusivearch,
    check_go_modules_toolchain,
    check_go_directive_clamp,
    check_duplicate_requires,
    check_local_sources,
    check_date_tag_service,
    check_service_download_url,
    check_rpm_payload_extract,
    check_offline_installs,
    check_lockfile_version,
    check_upstream_vendored,
    check_vendor_pin_drift,
]


def lint_spec(spec_path: Path) -> list[Finding]:
    spec = load(spec_path)
    out = []
    for check in _CHECKS:
        out.extend(check(spec))
    return out


def lint_repo(repo: Path, specs: list[Path]) -> int:
    all_findings: list[tuple[str, list[Finding]]] = []
    for sp in specs:
        findings = lint_spec(sp)
        all_findings.append((str(sp.relative_to(repo)), findings))

    archive_findings = check_tracked_archives(repo)
    if archive_findings:
        all_findings.append(("git", archive_findings))

    oversize_findings = check_oversize_payloads(repo)
    if oversize_findings:
        all_findings.append(("git", oversize_findings))

    execbit_findings = check_script_exec_bits(repo)
    if execbit_findings:
        all_findings.append(("git", execbit_findings))

    template_findings = check_templates_render(repo)
    if template_findings:
        all_findings.append(("templates", template_findings))

    has_fail = False
    for name, findings in all_findings:
        if not findings:
            print(f"{G}✓{N} {D}{name}{N}")
            continue
        for f in findings:
            glyph = _GLYPH.get(f.severity, "?")
            color = _COLOR.get(f.severity, "")
            loc = f"{D}:{f.line}{N}" if f.line else ""
            print(f"{color}{glyph}{N} {D}[{f.code}]{N} {name}{loc} {f.message}")
            if f.severity == FAIL:
                has_fail = True

    total = sum(len(fs) for _, fs in all_findings)
    fails = sum(1 for _, fs in all_findings for f in fs if f.severity == FAIL)
    warns = sum(1 for _, fs in all_findings for f in fs if f.severity == WARN)
    print(f"\n{D}{total} finding(s): {fails} FAIL, {warns} WARN{N}")
    return 1 if has_fail else 0


def find_specs(repo: Path, changed: bool = False) -> list[Path]:
    if changed:
        result = subprocess.run(
            ["git", "diff", "--name-only", "HEAD"], capture_output=True, text=True, cwd=repo
        )
        files = [repo / f for f in result.stdout.splitlines()]
        return sorted(f for f in files if f.suffix == ".spec" and f.exists())
    return sorted(repo.glob("packages/*/*.spec"))


def main():
    p = argparse.ArgumentParser(description="opensuse-packages spec linter")
    p.add_argument("specs", nargs="*", type=Path, help="specific spec files")
    p.add_argument("--all", action="store_true", help="lint every spec")
    args = p.parse_args()

    repo = Path.cwd()
    if args.specs:
        specs = [s.resolve() for s in args.specs]
    elif args.all:
        specs = find_specs(repo)
    else:
        specs = find_specs(repo, changed=True)
        if not specs:
            specs = find_specs(repo)

    if not specs:
        print(f"{Y}!{N} no specs found")
        return 0

    return lint_repo(repo, specs)


if __name__ == "__main__":
    sys.exit(main())
