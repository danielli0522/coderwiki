#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
MIGRATE_SCRIPT="${REPO_ROOT}/scripts/migrate_codex_courses_to_opendocs.sh"

tmpdir="$(mktemp -d)"
trap 'rm -rf "${tmpdir}"' EXIT

source_dir="${tmpdir}/source"
target_dir="${tmpdir}/target"
mkdir -p "${source_dir}" "${target_dir}"

for slug in course-01 course-02 course-03 course-04 course-05 course-06 course-07 course-08 course-09 course-10 course-11 course-12; do
  mkdir -p "${source_dir}/${slug}/modules"
  printf '%s\n' "${slug}" > "${source_dir}/${slug}/modules/index.txt"
done

mkdir -p "${target_dir}/course-02/modules" "${target_dir}/course-10/modules"
printf 'existing\n' > "${target_dir}/course-02/modules/index.txt"
printf 'existing\n' > "${target_dir}/course-10/modules/index.txt"

output="$(
  SOURCE_DIR="${source_dir}" \
  TARGET_DIR="${target_dir}" \
  MAX_COURSES=10 \
  bash "${MIGRATE_SCRIPT}"
)"

printf '%s\n' "${output}" | grep -F "Copied 8 course directories into ${target_dir}" >/dev/null
printf '%s\n' "${output}" | grep -F "Skipped 2 existing course directories" >/dev/null
printf '%s\n' "${output}" | grep -F "course-02" >/dev/null
printf '%s\n' "${output}" | grep -F "course-10" >/dev/null

for slug in course-01 course-02 course-03 course-04 course-05 course-06 course-07 course-08 course-09 course-10; do
  test -d "${target_dir}/${slug}"
done

test ! -d "${target_dir}/course-11"
test ! -d "${target_dir}/course-12"
test -d "${source_dir}/course-01"
test -d "${source_dir}/course-12"

echo "test_migrate_codex_courses_to_opendocs: PASS"
