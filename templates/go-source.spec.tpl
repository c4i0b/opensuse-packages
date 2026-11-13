# Template: Go source build vendored server-side (validated by packages/superfile).
#
# Pair with a package _service like this (revision = the git tag; versionrewrite
# strips the leading "v"; go_modules generates vendor.tar.gz server-side and the
# build stays offline):
#
#   <services>
#     <service name="tar_scm">
#       <param name="url">__URL__.git</param>
#       <param name="scm">git</param>
#       <param name="exclude">.git</param>
#       <param name="revision">v__VERSION__</param>
#       <param name="versionformat">@PARENT_TAG@</param>
#       <param name="versionrewrite-pattern">v(.*)</param>
#     </service>
#     <service name="set_version"/>
#     <service name="recompress">
#       <param name="file">*.tar</param>
#       <param name="compression">gz</param>
#     </service>
#     <service name="go_modules"/>
#   </services>
#
# tar_scm produces <name>-<version>.tar.gz; go_modules produces vendor.tar.gz.
# Reference both as Source0/Source1 exactly with those names.
# Check the upstream go.mod "go" directive and set the golang(API) floor to it.
# CEILING: go_modules only works while that directive is <= the Go on the OBS
# source-service host (see OBS_GO_MODULES_GO in opensuse-lint.py — the lint
# FAILs above it). When upstream needs a newer Go: drop go_modules from
# _service, generate vendor.tar.zst client-side
#   go mod vendor && tar --zstd -cf vendor.tar.zst vendor
# and use Source1: vendor.tar.zst + `BuildRequires: zstd` (reference:
# dnscontrol, nexttrace).
# Changelog lives in <name>.changes (OBS merges it into %changelog).
Name:           __NAME__
Version:        __VERSION__
Release:        0
Summary:        __SUMMARY__
License:        __LICENSE__
URL:            __URL__
Source0:        __NAME__-%{version}.tar.gz
Source1:        vendor.tar.gz
# %{go_arches} is NOT defined in Tumbleweed's prjconf anymore: an empty
# expansion makes OBS exclude every arch. List the arches explicitly.
ExclusiveArch:  x86_64 aarch64
BuildRequires:  golang(API) >= __GOVERSION__

%description
__DESCRIPTION__

# -a 1 unpacks Source1 (vendor/) into the same dir as Source0.
%prep
%autosetup -a 1

%build
export GOFLAGS="-buildmode=pie"
go build -mod=vendor -o __BIN__ .

# Optional: generate completions by running the just-built binary
# (only if upstream's CLI actually has a completion subcommand).
#__BIN__ completion bash > __BIN__.bash
#install -Dpm644 __BIN__.bash %{buildroot}%{_datadir}/bash-completion/completions/__BIN__

%install
install -Dpm 0755 __BIN__ %{buildroot}%{_bindir}/__BIN__

%files
%doc README.md
%license LICENSE
%{_bindir}/__BIN__

%changelog
