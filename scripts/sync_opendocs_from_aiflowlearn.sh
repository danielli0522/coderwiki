#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
COURSE_LIST="${SCRIPT_DIR}/opendocs_course_slugs.txt"
SOURCE_DIR="${AIFLOWLEARN_CODEX_DIR:-/Users/lshl124/openclaw-aigc-project/aiflowlearn/data/codex}"
TARGET_DIR="${REPO_ROOT}/data/opendocs"

if [[ ! -d "${SOURCE_DIR}" ]]; then
  echo "Source directory not found: ${SOURCE_DIR}" >&2
  exit 1
fi

if [[ ! -f "${COURSE_LIST}" ]]; then
  echo "Course list not found: ${COURSE_LIST}" >&2
  exit 1
fi

mkdir -p "${TARGET_DIR}"

synced_courses=()

while IFS= read -r slug; do
  if [[ -z "${slug}" || "${slug}" == \#* ]]; then
    continue
  fi

  source_path="${SOURCE_DIR}/${slug}"
  target_path="${TARGET_DIR}/${slug}"

  if [[ ! -d "${source_path}" ]]; then
    echo "Missing source course: ${source_path}" >&2
    exit 1
  fi

  mkdir -p "${target_path}"
  rsync -a --delete "${source_path}/" "${target_path}/"
  synced_courses+=("${slug}")
done < "${COURSE_LIST}"

echo "Synced ${#synced_courses[@]} interactive courses into ${TARGET_DIR}"
printf '%s\n' "${synced_courses[@]}"
