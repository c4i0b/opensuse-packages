# Build image for openSUSE Tumbleweed RPMs (-bin only: nothing compiles).
# Package-specific BuildRequires: are installed on demand by `just build`.
FROM registry.opensuse.org/opensuse/tumbleweed:latest

RUN zypper --non-interactive install --no-recommends \
        rpm-build rpmlint tar gzip xz unzip curl zstd git ca-certificates \
    && zypper clean -a
