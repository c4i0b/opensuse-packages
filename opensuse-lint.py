#!/usr/bin/env python3
"""opensuse-packages spec linter — catches CI-only mistakes locally.

Usage:
  opensuse-lint.py             DEFAULT: uncommitted working tree
  opensuse-lint.py --all       lint every spec under packages/
  opensuse-lint.py <spec>...   lint specific spec paths
"""
from __future__ import annotations
import argparse, json, re, subprocess, sys
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

# Prebuilt binary classification. OBS brp-strip runs on every prebuilt binary;
# only Bun-compiled single-file executables (app JS payload appended to the ELF)
# get corrupted by stripping. Go/Rust/Electron binaries are strip-safe and must
# NOT be flagged. Register new prebuilt packages here so the lint knows what to
# check for; unknown prebuilts get a WARN asking to be classified.
PREBUILT_ORIGIN = {
    # upstream-RPM repackage (fedora-packages model): Electron bundle under
    # %{_libdir}, strip disabled in the spec itself (stripping corrupts the
    # embedded snapshot). superfile/television/ytm-player build from source
    # since 2026-11 — no prebuilt registry entries left.
    "pear-desktop": "electron",
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
            if _SECTION_RE.match(line):
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
        if name in seen:
            out.append(Finding(FAIL, "duplicate-requires",
                f"duplicate {prefix[:-1]}: {name.split()[0]} (first at line {seen[name]})",
                line=i))
        else:
            seen[name] = str(i)
    return out


def check_tracked_archives(repo: Path) -> list[Finding]:
    result = subprocess.run(
        ["git", "ls-files"], capture_output=True, text=True, cwd=repo
    )
    bad = [f for f in result.stdout.splitlines()
           if f.endswith((".tar.gz", ".tgz", ".tar.xz", ".zip", ".rpm", ".deb", ".AppImage"))]
    if bad:
        return [Finding(FAIL, "tracked-archive",
            f"{len(bad)} archive(s) tracked in git: {', '.join(bad[:3])}"
            + ("..." if len(bad) > 3 else ""))]
    return []


# Archives are legitimately absent from a clean checkout by design: the
# upstream tarball is fetched server-side via _service, and Rust vendor
# archives (vendor.tar.zst, generated client-side by cargo_vendor) are
# gitignored and only live on OBS. Based on the check_tracked_archives
# extension list, plus .tar.zst (the vendor-archive format).
_ARCHIVE_EXTS = (".tar.gz", ".tgz", ".tar.xz", ".tar.zst", ".zip", ".rpm", ".deb", ".AppImage")


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
    check_duplicate_requires,
    check_local_sources,
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
