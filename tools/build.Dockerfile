# Build image for openSUSE Tumbleweed RPMs.
# Tumbleweed-native build macros (*-packaging) + spec generators (rust2rpm/go2rpm).
# Generators are pip-installed only because they exist in no openSUSE repository;
# they generate .spec files, they are not used at build time.
FROM registry.opensuse.org/opensuse/tumbleweed:latest

RUN zypper --non-interactive install --no-recommends \
        rpm-build rpmlint tar gzip xz unzip curl zstd \
        cargo-packaging cargo golang-packaging go \
        python-rpm-macros systemd-rpm-macros cmake \
        python3-pip git ca-certificates \
    && zypper clean -a \
    && python3 -m pip install --quiet --break-system-packages \
        go2rpm \
        "rust2rpm @ git+https://codeberg.org/rust2rpm/rust2rpm.git"

# rust2rpm calls `git config user.*` when generating specs; go2rpm needs the
# askalono license detector (Rust binary, no distro package).
RUN git config --system user.name "opensuse-packaging" \
    && git config --system user.email "opensuse-packaging@localhost" \
    && curl -fsSL -o /tmp/askalono.zip https://github.com/jpeddicord/askalono/releases/download/0.5.0/askalono-Linux.zip \
    && mkdir -p /tmp/askalono \
    && unzip -o /tmp/askalono.zip -d /tmp/askalono >/dev/null \
    && install -m 755 "$(find /tmp/askalono -type f -name 'askalono*' | head -1)" /usr/local/bin/askalono \
    && rm -rf /tmp/askalono /tmp/askalono.zip
