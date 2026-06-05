#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
DEFAULT_SOURCE_DIR="/Users/lshl124/openclaw-aigc-project/aiflowlearn/data/codex"
SOURCE_DIR="${SOURCE_DIR:-${DEFAULT_SOURCE_DIR}}"
TARGET_DIR="${TARGET_DIR:-${REPO_ROOT}/data/opendocs}"
MAX_COURSES="${MAX_COURSES:-10}"

mkdir -p "${TARGET_DIR}"

if [[ ! -d "${SOURCE_DIR}" ]]; then
  echo "Source directory not found: ${SOURCE_DIR}"
  exit 1
fi

source_paths=()
while IFS= read -r source_path; do
  source_paths+=("${source_path}")
done < <(find "${SOURCE_DIR}" -mindepth 1 -maxdepth 1 -type d | sort)

if [[ ${#source_paths[@]} -eq 0 ]]; then
  echo "No course directories found in ${SOURCE_DIR}"
  exit 0
fi

copied_courses=()
skipped_courses=()
selected_count=0

for source_path in "${source_paths[@]}"; do
  if [[ "${selected_count}" -ge "${MAX_COURSES}" ]]; then
    break
  fi

  slug="$(basename "${source_path}")"
  target_path="${TARGET_DIR}/${slug}"
  selected_count=$((selected_count + 1))

  if [[ -e "${target_path}" ]]; then
    skipped_courses+=("${slug}")
    continue
  fi

  cp -R "${source_path}" "${target_path}"
  copied_courses+=("${slug}")
done

if [[ ${#copied_courses[@]} -eq 0 ]]; then
  echo "No new course directories copied from ${SOURCE_DIR}"
else
  echo "Copied ${#copied_courses[@]} course directories into ${TARGET_DIR}"
  printf '%s\n' "${copied_courses[@]}"
fi

if [[ ${#skipped_courses[@]} -gt 0 ]]; then
  echo "Skipped ${#skipped_courses[@]} existing course directories"
  printf '%s\n' "${skipped_courses[@]}"
fi
