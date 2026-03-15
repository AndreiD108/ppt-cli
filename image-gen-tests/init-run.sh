#!/usr/bin/env bash
#
# Initialize a new benchmark run directory.
#
# Creates the next numbered run folder with guided/unguided subdirs,
# writes skeleton metadata.json, copies the results template with
# run number and date substituted, and prints the path.
#
# Usage:  ./init-run.sh
# Output: /absolute/path/to/image-gen-tests/NNN
#
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
TESTS_DIR="$SCRIPT_DIR"

# ── Next run number ────────────────────────────────────────────────
last=$(ls -1d "$TESTS_DIR"/[0-9][0-9][0-9] 2>/dev/null | sort | tail -1 | xargs -r basename)
if [ -z "${last:-}" ]; then
  next="001"
else
  next=$(printf "%03d" $((10#$last + 1)))
fi

RUN_DIR="$TESTS_DIR/$next"
mkdir -p "$RUN_DIR/guided" "$RUN_DIR/unguided"

# ── Stock images check ─────────────────────────────────────────────
STOCK_DIR="$TESTS_DIR/stock"
STOCK_FILES=(portrait.png product.png photo-event.png photo-office.png photo-street.png style-ref.png)
stock_ok=true
for f in "${STOCK_FILES[@]}"; do
  if [ ! -f "$STOCK_DIR/$f" ]; then
    echo "WARNING: Missing stock image: stock/$f" >&2
    stock_ok=false
  fi
done
if [ "$stock_ok" = false ]; then
  echo "Generate stock images before running ref-image units (see docs/image-gen-benchmark.md)." >&2
fi

# ── Skill file hash ────────────────────────────────────────────────
SKILL_FILE="$SCRIPT_DIR/../ppt_cli/skill/2-image-generation.md"
if [ -f "$SKILL_FILE" ]; then
  skill_hash=$(sha256sum "$SKILL_FILE" | cut -d' ' -f1)
else
  skill_hash="NOT_FOUND"
  echo "WARNING: Skill file not found at $SKILL_FILE" >&2
fi

# ── Stock images hash ──────────────────────────────────────────────
if [ "$stock_ok" = true ]; then
  stock_hash=$(cat "${STOCK_FILES[@]/#/$STOCK_DIR/}" | sha256sum | cut -d' ' -f1)
else
  stock_hash="INCOMPLETE"
fi

# ── Skeleton metadata.json ─────────────────────────────────────────
TODAY=$(date +%Y-%m-%d)
cat > "$RUN_DIR/metadata.json" << EOF
{
  "run": "$next",
  "timestamp": "$TODAY",
  "skill_file": "ppt_cli/skill/2-image-generation.md",
  "skill_file_hash": "sha256:$skill_hash",
  "stock_images_hash": "sha256:$stock_hash",
  "resolution": "1k",
  "images_per_type": 3,
  "prompt_mode": "unique_per_image",
  "presentation_scenario": "EDIT: Describe the fictional presentation scenario here",
  "units": [
    {"unit": 1, "types": ["fullbleed"], "ratio": "16:9"},
    {"unit": 2, "types": ["halfbleed"], "ratio": "3:4"},
    {"unit": 3, "types": ["concept", "icon", "chart", "text-in-image"], "ratio": "varies"},
    {"unit": 4, "types": ["manga", "comic", "retro", "editorial", "flat-vector"], "ratio": "16:9"},
    {"unit": 5, "types": ["people"], "ratio": "3:4"},
    {"unit": 6, "types": ["icon-set-1", "icon-set-2", "icon-set-3", "icon-set-4"], "ratio": "1:1"},
    {"unit": 7, "types": ["duotone", "colorgrade", "styleadapt"], "ratio": "16:9", "ref": true},
    {"unit": 8, "types": ["bgreplace", "bgremove"], "ratio": "varies", "ref": true},
    {"unit": 9, "types": ["character"], "ratio": "16:9", "ref": true},
    {"unit": 10, "types": ["stylematch", "multiref"], "ratio": "16:9", "ref": true}
  ]
}
EOF

# ── Empty prompts.json (prevents fetch errors) ─────────────────────
echo '{}' > "$RUN_DIR/prompts.json"

# ── Copy and fill results template ─────────────────────────────────
TEMPLATE="$TESTS_DIR/results-template.html"
if [ -f "$TEMPLATE" ]; then
  sed "s/{{RUN}}/$next/g; s/{{DATE}}/$TODAY/g" "$TEMPLATE" > "$RUN_DIR/results.html"
else
  echo "WARNING: results-template.html not found, skipping HTML copy" >&2
fi

# ── Output ─────────────────────────────────────────────────────────
echo "$RUN_DIR"
