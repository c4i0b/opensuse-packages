# Tooling image for the opensuse-packages repo — the environment every `just`
# recipe runs in (see compose.yml). openSUSE Tumbleweed to match the OBS
# project's repository. -bin only: nothing compiles; package-specific
# BuildRequires are installed on demand at build time (tools/build.sh).
FROM registry.opensuse.org/opensuse/tumbleweed:latest

RUN zypper --non-interactive install --no-recommends \
        rpm-build rpmlint \
        osc build \
        python3 rsync tar gzip xz unzip zstd \
        git curl ca-certificates \
    && zypper clean -a

WORKDIR /app
