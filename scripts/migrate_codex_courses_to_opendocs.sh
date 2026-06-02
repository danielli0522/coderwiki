#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
SOURCE_DIR="${REPO_ROOT}/data/codex"
TARGET_DIR="${REPO_ROOT}/data/opendocs"

mkdir -p "${SOURCE_DIR}" "${TARGET_DIR}"

shopt -s nullglob
moved_courses=()

for source_path in "${SOURCE_DIR}"/*; do
  if [[ ! -d "${source_path}" ]]; then
    continue
  fi

  slug="$(basename "${source_path}")"
  target_path="${TARGET_DIR}/${slug}"

  rm -rf "${target_path}"
  mv "${source_path}" "${target_path}"
  moved_courses+=("${slug}")
done

if [[ ${#moved_courses[@]} -eq 0 ]]; then
  echo "No course directories found in ${SOURCE_DIR}"
  exit 0
fi

echo "Moved ${#moved_courses[@]} course directories into ${TARGET_DIR}"
printf '%s\n' "${moved_courses[@]}"
