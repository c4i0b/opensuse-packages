FROM registry.opensuse.org/opensuse/tumbleweed

RUN zypper --non-interactive refresh && \
    zypper --non-interactive install --no-recommends \
      ca-certificates \
      coreutils findutils grep diffutils patch \
      tar gzip bzip2 xz unzip \
      git ripgrep fd make gcc gcc-c++ \
      curl which file openssh-clients && \
    zypper clean --all

ADD opencode-linux-x64.tar.gz /usr/local/bin/
RUN chmod 0755 /usr/local/bin/opencode

RUN useradd --create-home --shell /bin/bash --uid 1000 opencode

WORKDIR /workspace
USER opencode

LABEL org.opencontainers.image.title="opencode" \
      org.opencontainers.image.description="OpenCode AI coding agent on openSUSE Tumbleweed" \
      org.opencontainers.image.source="https://github.com/anomalyco/opencode" \
      org.opencontainers.image.url="https://opencode.ai" \
      org.opencontainers.image.licenses="MIT" \
      org.opensuse.lifecycle-url="https://en.opensuse.org/Lifetime"

ENTRYPOINT ["/usr/local/bin/opencode"]
CMD ["--help"]
