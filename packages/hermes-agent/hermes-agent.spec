# Bundled-venv model: upstream ships no installable wheels (setup.py blocks
# non-Nix builds) and manages deps via its own uv/PM runtime. The locked
# dependency closure (from upstream's uv.lock, exact pins + hashes) is
# vendored client-side as wheels.tar.zst (see fetch.sh --vendor); the
# OBS-side install is fully offline: python-uv builds a venv under
# %%{_libdir} from python314 and the vendored wheels.
%global debug_package %{nil}
# manylinux wheels bundle auditwheel-hashed libs (libjpeg-<8hex>.so); RPM
# requires their versioned symbols but nothing (not even this package)
# provides them, making the rpm uninstallable
%global __requires_exclude ^lib.+-[0-9a-f]{8}\\.so

Name:           hermes-agent
Version:        0.23.1
Release:        0
Summary:        The self-improving AI agent by Nous Research
License:        MIT
URL:            https://github.com/NousResearch/hermes-agent
Source0:        hermes-agent-%{version}.tar.gz
Source1:        wheels.tar.zst
Source2:        requirements.txt
# the vendored wheel set is x86_64-only (manylinux builds); re-vendor for
# more arches before widening this
ExclusiveArch:  x86_64

BuildRequires:  python314
BuildRequires:  python314-uv
# rpmuncompress needs zstd for the client-side wheels.tar.zst (Source1)
BuildRequires:  zstd
Requires:       python314

%description
Hermes Agent is a self-improving AI agent: it creates skills from experience,
improves them during use, and builds a persistent memory across sessions. It
runs locally on your own devices and answers on the channels you already use.

%prep
%autosetup -a 1 -n hermes-agent-%{version}

%build
# venv assembly happens in %install; the vendored wheels need no compilation

%install
venvdir=%{buildroot}%{_libdir}/%{name}
# (uv venvs never seed pip — no --without-pip flag needed)
uv venv --python /usr/bin/python3.14 "$venvdir"
vp="$venvdir/bin/python"

# build backend for the no-isolation sdist build of the project itself
uv pip install --python "$vp" --no-index --find-links wheels \
    setuptools==84.1.0 wheel
# locked closure (Source2), then the project itself — resolution happened
# client-side against upstream's uv.lock ([tool.uv] override-dependencies are
# baked into it), so plain pip-level offline installs suffice here
# HERMES_NIX_BUILD bypasses upstream's "no wheels outside Nix" guard
HERMES_NIX_BUILD=1 uv pip install --python "$vp" \
    --no-index --find-links wheels --no-deps -r %{SOURCE2}
HERMES_NIX_BUILD=1 uv pip install --python "$vp" \
    --no-index --find-links wheels --no-deps --no-build-isolation .

# uv leaves a 0666 venv lock behind (rpmlint world-writable; recreated by
# uv wherever it can write at runtime)
rm -f "$venvdir/.lock"

# Venv scripts and pyvenv.cfg carry the buildroot path
grep -rlZ '%{buildroot}' "$venvdir/bin/" \
    | xargs -0r sed -i "s|%{buildroot}||g"
sed -i "s|%{buildroot}||g" "$venvdir/pyvenv.cfg"
# brp-mangle-shebangs aborts on ambiguous "env python" shebangs in vendored
# test scripts (croniter)
grep -rlZ '^#!/usr/bin/env python$' "$venvdir/" \
    | xargs -0r sed -i 's|^#!/usr/bin/env python$|#!/usr/bin/python3.14|'

install -d -m755 %{buildroot}%{_bindir}
for b in hermes hermes-agent hermes-acp; do
    ln -s %{_libdir}/%{name}/bin/$b %{buildroot}%{_bindir}/$b
done

install -d -m755 %{buildroot}%{_datadir}/%{name}
cp -a skills locales optional-mcps optional-skills plugin-catalog \
    cli-config.yaml.example %{buildroot}%{_datadir}/%{name}/

%check
# Run under a scratch HOME: hermes writes ~/.hermes on first run.
# --version short-circuits before the full import chain: exercise it too,
# or missing venv deps pass silently.
# Invoke the interpreter with the buildroot's site-packages on PYTHONPATH:
# the venv's bin/python symlink is relative to its FINAL location
# (brp-25-symlink relinks absolute links), so it dangles inside the
# buildroot and cannot be exec'd there.
mkdir -p "%{_builddir}/home"
sp="%{buildroot}%{_libdir}/%{name}/lib/python3.14/site-packages"
HOME="%{_builddir}/home" PYTHONPATH="$sp" /usr/bin/python3.14 \
    -c "import hermes_cli.main"
HOME="%{_builddir}/home" PYTHONPATH="$sp" /usr/bin/python3.14 \
    "%{buildroot}%{_libdir}/%{name}/bin/hermes" --version

%files
%license LICENSE
%doc README.md
%{_bindir}/hermes
%{_bindir}/hermes-agent
%{_bindir}/hermes-acp
%{_libdir}/%{name}/
%{_datadir}/%{name}/

%changelog
