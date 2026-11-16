# Template: bundled Python venv from vendored wheels (validated by
# packages/hermes-agent).
# Changelog lives in <name>.changes (OBS merges it into %changelog).
#
# MODEL — for apps that ship no installable wheels and manage their own
# dependency environment (uv/PM runtimes). Prefer per-module distro deps
# (python.spec.tpl) whenever pip can resolve them; no obs-service for
# PyPI exists (Factory has one for cargo/go_modules/node_modules, not
# PyPI), so client-side wheel vendoring is the only offline path for a
# lock that must be honored verbatim.
# - The dependency closure comes from upstream's lockfile (uv.lock), exported
#   with `uv export --frozen` and downloaded CLIENT-side for linux x86_64 /
#  the CPython the spec wraps → wheels.tar.zst (gitignored, pushed via the
#   --filter='P *.tar.zst' protection in tools/obs-rsync.sh, same as rust
#   vendor archives).
# - Source2 is the exported requirements.txt (committed: reviewable pins,
#   with hashes when upstream locks them).
# - OBS-side install is offline: uv (BuildRequires python31X-uv) creates a
#   venv under %%{_libdir} from python31X and installs from the vendored
#   wheels with --no-index --find-links --no-deps.
#
# INVARIANTS (see opensuse-lint.py checks):
# - `==` pins (e.g. setuptools==X) are identical in the spec and in
#   fetch.sh, or the offline install fails on OBS (guard:
#   vendor-pin-drift).
# - Never let pip/uv resolve at build time: no bare `pip install` /
#   `uv pip install` without --no-index (OBS workers are offline), and
#   --no-deps so upstream's [tool.uv] override-dependencies (which plain
#   resolution cannot honor) stay baked into the vendored set.
# - Building the project itself uses --no-build-isolation with the build
#   backend preinstalled from the vendored wheels (setuptools/wheel pins
#   come from upstream's [build-system]).
# - venv console scripts carry the buildroot path in shebangs and
#   pyvenv.cfg: sed it out, and %check must invoke scripts through
#   %%{buildroot}%%{_libdir}/<name>/bin/python (their shebangs point at the
#   FINAL path).
# - manylinux wheels bundle auditwheel-hashed libs: keep __requires_exclude.
# - uv venv leaves a 0666 .lock: remove it (rpmlint world-writable).
# - The CPython major must satisfy upstream's requires-python AND its dep
#   markers (hermes gates everything on python_version >= '3.14' → python314).
# - python-uv is single-spec: the binary package is python31X-uv (provides
#   /usr/bin/uv), NOT `python-uv`.

%global debug_package %{nil}
# manylinux wheels bundle auditwheel-hashed libs (libjpeg-<8hex>.so); RPM
# requires their versioned symbols but nothing provides them
%global __requires_exclude ^lib.+-[0-9a-f]{8}\\.so

Name:           __NAME__
Version:        __VERSION__
Release:        0
Summary:        __SUMMARY__
License:        __LICENSE__
URL:            https://github.com/__UPSTREAM__
Source0:        __NAME__-%{version}.tar.gz
Source1:        wheels.tar.zst
Source2:        requirements.txt
ExclusiveArch:  x86_64

BuildRequires:  python31X
BuildRequires:  python31X-uv
# rpmuncompress needs zstd for the client-side wheels.tar.zst (Source1)
BuildRequires:  zstd
Requires:       python31X

%description
__DESCRIPTION__

%prep
%autosetup -a 1 -n __NAME__-%{version}

%build
# venv assembly happens in %install; the vendored wheels need no compilation

%install
venvdir=%{buildroot}%{_libdir}/%{name}
uv venv --python /usr/bin/python3.1X "$venvdir"
vp="$venvdir/bin/python"

# build backend for the no-isolation sdist build of the project itself
# (pins from upstream's [build-system])
uv pip install --python "$vp" --no-index --find-links wheels \
    setuptools==__SETUPTOOLS__ wheel
# locked closure (Source2), then the project itself — resolution happened
# client-side against upstream's lock, so plain offline installs suffice
uv pip install --python "$vp" \
    --no-index --find-links wheels --no-deps -r %{SOURCE2}
uv pip install --python "$vp" \
    --no-index --find-links wheels --no-deps --no-build-isolation .

# uv leaves a 0666 venv lock behind (rpmlint world-writable)
rm -f "$venvdir/.lock"
# Venv scripts and pyvenv.cfg carry the buildroot path
grep -rlZ '%{buildroot}' "$venvdir/bin/" \
    | xargs -0r sed -i "s|%{buildroot}||g"
sed -i "s|%{buildroot}||g" "$venvdir/pyvenv.cfg"
# brp-mangle-shebangs aborts on ambiguous "env python" shebangs in vendored
# scripts
grep -rlZ '^#!/usr/bin/env python$' "$venvdir/" \
    | xargs -0r sed -i 's|^#!/usr/bin/env python$|#!/usr/bin/python3.1X|'

install -d -m755 %{buildroot}%{_bindir}
for b in __BINS__; do
    ln -s %{_libdir}/%{name}/bin/$b %{buildroot}%{_bindir}/$b
done

%check
# Run under a scratch HOME. Invoke the interpreter with the buildroot's
# site-packages on PYTHONPATH: console scripts' shebangs and the venv's
# bin/python symlink point at the FINAL venv location (brp-25-symlink
# relinks absolute links), so they dangle inside the buildroot and cannot
# be exec'd there.
mkdir -p "%{_builddir}/home"
sp="%{buildroot}%{_libdir}/%{name}/lib/python3.1X/site-packages"
HOME="%{_builddir}/home" /usr/bin/python3.1X -c "__IMPORT__"
HOME="%{_builddir}/home" PYTHONPATH="$sp" /usr/bin/python3.1X \
    "%{buildroot}%{_libdir}/%{name}/bin/__BIN__" --version

%files
%license LICENSE
%doc README.md
%{_bindir}/__BIN__
%{_libdir}/%{name}/

%changelog
