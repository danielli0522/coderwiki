#!/bin/bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUT_BASE="$PROJECT_ROOT/coderwiki-output-docs"
TEMP_BASE="$PROJECT_ROOT/temp/ai-generate-doc"

mkdir -p "$OUT_BASE/ai-generate-doc" "$OUT_BASE/mkdocs-site" "$OUT_BASE/repos"

echo "Promoting docs from temp to coderwiki-output-docs..."
if [ -d "$TEMP_BASE" ]; then
  for d in "$TEMP_BASE"/*; do
    [ -d "$d" ] || continue
    run_name="$(basename "$d")"
    rsync -a --delete "$d"/ "$OUT_BASE/ai-generate-doc/$run_name/"
  done
else
  echo "No temp runs found at $TEMP_BASE"
fi

echo "Building MkDocs sites for promoted runs..."
python3 - <<'PY'
import os
from pathlib import Path

base = Path(os.environ.get('OUT_BASE', 'coderwiki-output-docs'))
ai_dir = base / 'ai-generate-doc'
mkdocs_service_path = Path('backend/app/services/mkdocs_service.py')

print(f"AI docs base: {ai_dir}")
print(f"MkDocs service at: {mkdocs_service_path}")

if not ai_dir.exists():
    raise SystemExit(0)

print("Hint: Build via backend service endpoint or CLI if available.")
PY

echo "Done. Promoted docs to $OUT_BASE/ai-generate-doc."


