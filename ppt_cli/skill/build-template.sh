#!/usr/bin/env bash
set -euo pipefail

# ── ppt-cli build script ──────────────────────────────────────────────
# Generated from a presentation build plan. Each slide is a function;
# run all slides or specific ones by number.
#
# Usage:
#   bash build.sh          # build all slides in order
#   bash build.sh all      # same
#   bash build.sh 3 7 12   # rebuild only slides 3, 7, and 12
# ──────────────────────────────────────────────────────────────────────

PPTX=""      # ← SET THIS to the deck's absolute path
TEMPLATE=""  # ← optional: set to a template name

if [[ -z "$PPTX" ]]; then
  echo "Error: set the PPTX variable at the top of this script." >&2
  exit 1
fi

# ── helpers ───────────────────────────────────────────────────────────

# Capture the shape ID from a ppt-cli command that returns JSON.
# Usage:  SID=$(shape_id ppt-cli add-textbox "$PPTX" 1 "Hello" --x 1in ...)
shape_id() {
  "$@" | python3 -c "import sys,json; print(json.load(sys.stdin)['shape_id'])"
}

# ── layout map ────────────────────────────────────────────────────────
# Map slide numbers to layout names. Slides not listed default to Blank.
# When using a template, set these to match the template's layout names.
declare -A LAYOUTS=(
  # [1]="Title Slide"
  # [5]="Section Header"
)

# ── slides ────────────────────────────────────────────────────────────

# Replace this example with actual slide functions from the build plan.
#
# IMPORTANT: each slide function must be idempotent — safe to re-run on
# a slide that already has content (for rebuilds after QA). How to
# achieve this depends on the slide type:
#
#   Blank-layout slides: delete all shapes first, then rebuild from
#   scratch (background first, then panels, then text/images on top).
#
#   Template-layout slides (with placeholders): delete only freehand
#   shapes (those without "placeholder_idx" in dump output), then use
#   set-title / set-text for placeholders and add-textbox for the rest.
#
# Use shape_id to capture IDs for subsequent set-font/set-fill calls.

slide_1() {
  # Example: Blank-layout slide — full-bleed image + subtitle text.
  # Delete all existing shapes to make this function re-runnable.
  for sid in $(ppt-cli dump "$PPTX" 1 2>/dev/null \
    | python3 -c "import sys,json
for s in json.load(sys.stdin).get('shapes',[]):
    print(s['id'])" 2>/dev/null); do
    ppt-cli delete-shape "$PPTX" 1 --shape-id "$sid" > /dev/null
  done

  ppt-cli add-image "$PPTX" 1 --prompt "..." --resolution 2k --ratio 16:9 \
    --x 0in --y 0in --w 13.333in --h 7.5in

  SID=$(shape_id ppt-cli add-textbox "$PPTX" 1 "SUBTITLE TEXT" \
    --x 0.5in --y 6.5in --w 12.333in --h 0.5in \
    --font-size 14 --font-color '#6A6A85' --bold)
  ppt-cli set-font "$PPTX" 1 --shape-id "$SID" --name Arial

  ppt-cli set-notes "$PPTX" 1 "Speaker notes for slide 1."
}

# slide_2() { ... }
# slide_3() { ... }
# ...

# ── dispatcher ────────────────────────────────────────────────────────

# Create the deck if it doesn't exist yet.
if [[ ! -f "$PPTX" ]]; then
  if [[ -n "$TEMPLATE" ]]; then
    ppt-cli create "$PPTX" --template "$TEMPLATE"
  else
    ppt-cli create "$PPTX"
  fi
fi

# Count the slide_N functions defined in this script.
SLIDE_COUNT=$(declare -F | awk '$3 ~ /^slide_[0-9]+$/{print $3}' | wc -l)

# Ensure the deck has enough slides. Uses the LAYOUTS map for slides
# that need a specific layout; defaults to Blank for the rest.
CURRENT=$(ppt-cli info "$PPTX" | python3 -c "import sys,json; print(json.load(sys.stdin)['slides'])")
while (( CURRENT < SLIDE_COUNT )); do
  N=$(( CURRENT + 1 ))
  LAYOUT="${LAYOUTS[$N]:-Blank}"
  ppt-cli add-slide "$PPTX" --layout "$LAYOUT" > /dev/null
  CURRENT=$(( CURRENT + 1 ))
done

build_slide() {
  local fn="slide_${1}"
  if declare -f "$fn" > /dev/null 2>&1; then
    echo "Building slide ${1}..." >&2
    "$fn"
  else
    echo "Error: no function for slide ${1}" >&2
    exit 1
  fi
}

if [[ $# -eq 0 || "${1}" == "all" ]]; then
  for fn in $(declare -F | awk '$3 ~ /^slide_[0-9]+$/{print $3}' | sort -t_ -k2 -n); do
    n="${fn#slide_}"
    echo "Building slide ${n}..." >&2
    "$fn"
  done
else
  for n in "$@"; do
    build_slide "$n"
  done
fi

echo "Done." >&2
