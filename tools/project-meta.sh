#!/usr/bin/env bash
# Render the OBS project meta to stdout (repos/arch table inline). Single source
# of truth for the build targets: setup-obs.sh and the push-to-obs workflow
# both call this, so the repo table lives in exactly one place.
#
# Repo table format: name|path project|path repository|arches
# x86_64 only: aarch64 was dropped project-wide.

set -euo pipefail

project="home:${OBS_USER:?OBS_USER unset}"
REPOS=(
  "opensuse_tumbleweed|openSUSE:Tumbleweed|standard|x86_64"
  "opensuse_slowroll|openSUSE:Slowroll|standard|x86_64"
)

{
  echo " <project name=\"${project}\">"
  echo "  <title>Personal openSUSE packages</title>"
  echo "  <description>RPMs for openSUSE Tumbleweed and Slowroll.</description>"
  for entry in "${REPOS[@]}"; do
    IFS='|' read -r name path_project path_repo arches <<<"$entry"
    echo "  <repository name=\"${name}\">"
    echo "    <path project=\"${path_project}\" repository=\"${path_repo}\"/>"
    for a in $arches; do
      echo "    <arch>${a}</arch>"
    done
    echo "  </repository>"
  done
  echo "</project>"
}
