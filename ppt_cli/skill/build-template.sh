#!/usr/bin/env bash
set -euo pipefail

# ── COMMAND COMPOSITION PATTERNS ────────────────────────────────────────
# Read these before writing slide functions. Patterns are organized by
# use case, not by design direction — use whichever ones the slide needs.
# Direction affinity is noted in parentheses where a pattern is
# predominantly used in one direction, but any pattern can appear anywhere.
#
# ─────────────────────────── LAYOUT & BACKGROUND ───────────────────────
#
# @pattern dark-background
#   # Full-slide background fill. Add FIRST so content layers on top.
#   SID=$(shape_id ppt-cli add-textbox "$PPTX" N "" \
#     --x 0in --y 0in --w 13.333in --h 7.5in)
#   ppt-cli set-fill "$PPTX" N --shape-id "$SID" --color "$DARK_BG"
#   # Then add content shapes — they layer on top automatically.
#   # Remember to use light font colors on dark backgrounds.
#
# @pattern semi-transparent-overlay (creative)
#   # No opacity control in ppt-cli. Two alternatives:
#   # 1. Generate image with natural dark region (prompt: "dark gradient
#   #    fading to black on the left third") and place text in that area.
#   # 2. Add a narrow colored bar as a text backing:
#   SID=$(shape_id ppt-cli add-textbox "$PPTX" N "" \
#     --x 0in --y 5in --w 13.333in --h 2.5in)
#   ppt-cli set-fill "$PPTX" N --shape-id "$SID" --color "$DARK_BG"
#   # Then place text on top of the bar.
#
# ─────────────────────────── IMAGE PLACEMENT ───────────────────────────
#
# @pattern full-bleed-image
#   # Image fills entire slide. Add BEFORE text shapes (layer order).
#   ppt-cli add-image "$PPTX" N --prompt "..." --resolution 2k --ratio 16:9 \
#     --x 0in --y 0in --w 13.333in --h 7.5in
#   # MUST specify negative space in prompt when text will overlay.
#   SID=$(shape_id ppt-cli add-textbox "$PPTX" N "TITLE" \
#     --x 0.5in --y 5.5in --w 8in --h 1.5in)
#   ppt-cli set-font "$PPTX" N --shape-id "$SID" --color '#FFFFFF' --bold --size 44
#
# @pattern half-bleed-image (left or right)
#   # Image fills one half; content in the other half.
#   # Left image:
#   ppt-cli add-image "$PPTX" N --prompt "..." --resolution 2k \
#     --x 0in --y 0in --w 6.666in --h 7.5in
#   SID=$(shape_id ppt-cli add-textbox "$PPTX" N "$CONTENT" \
#     --x 7.2in --y 1.2in --w 5.5in --h 5.5in)
#   # Right image: swap x coordinates (content at 0.5in, image at 6.666in).
#
# @pattern two-column-text-image
#   ppt-cli add-textbox "$PPTX" N "$TEXT" \
#     --x 0.5in --y 1.2in --w 5.5in --h 5.5in
#   ppt-cli add-image "$PPTX" N --prompt "..." \
#     --x 6.5in --y 0.5in --w 6.333in --h 6.5in
#
# ─────────────────────────── DECORATIVE ELEMENTS ───────────────────────
#
# @pattern accent-bar (business, technical)
#   # Thin vertical or horizontal divider — accent-colored empty textbox.
#   # Vertical (side border on a card or section):
#   SID=$(shape_id ppt-cli add-textbox "$PPTX" N "" \
#     --x 0.5in --y 1in --w 0.08in --h 5.5in)
#   ppt-cli set-fill "$PPTX" N --shape-id "$SID" --color "$ACCENT"
#   # Horizontal (top/bottom edge of slide — high-coverage anchor motif):
#   SID=$(shape_id ppt-cli add-textbox "$PPTX" N "" \
#     --x 0in --y 7.35in --w 13.333in --h 0.15in)
#   ppt-cli set-fill "$PPTX" N --shape-id "$SID" --color "$ACCENT"
#
# @pattern logo-every-slide
#   # Add last on each slide so it layers on top.
#   # Use identical coordinates on every slide for consistency.
#   ppt-cli add-image "$PPTX" N logo.png \
#     --x 11.8in --y 6.9in --w 1in --h 0.5in
#
# ─────────────────────────── DATA & STATS ──────────────────────────────
#
# @pattern stat-callout (3 across)
#   for i in 0 1 2; do
#     x=$(echo "0.5 + $i * 4.1" | bc)
#     SID=$(shape_id ppt-cli add-textbox "$PPTX" N "$NUMBER" \
#       --x "${x}in" --y 2.5in --w 3.8in --h 1.5in)
#     ppt-cli set-font "$PPTX" N --shape-id "$SID" \
#       --size 66 --bold --color "$ACCENT"
#     # Label directly below the number:
#     LID=$(shape_id ppt-cli add-textbox "$PPTX" N "$LABEL" \
#       --x "${x}in" --y 4in --w 3.8in --h 0.5in)
#     ppt-cli set-font "$PPTX" N --shape-id "$LID" \
#       --size 14 --color "$MUTED"
#   done
#
# @pattern oversized-stat-number (creative)
#   # The number IS the visual element — no image needed.
#   SID=$(shape_id ppt-cli add-textbox "$PPTX" N "$NUMBER" \
#     --x 1in --y 1.5in --w 6in --h 3in)
#   ppt-cli set-font "$PPTX" N --shape-id "$SID" \
#     --size 90 --bold --color "$ACCENT"
#   # Small label below:
#   LID=$(shape_id ppt-cli add-textbox "$PPTX" N "$LABEL" \
#     --x 1in --y 4.5in --w 6in --h 0.5in)
#   ppt-cli set-font "$PPTX" N --shape-id "$LID" \
#     --size 13 --color "$MUTED"
#
# ─────────────────────────── CONTAINERS & CODE ─────────────────────────
#
# @pattern code-container (technical)
#   # Outer container: slightly larger, dark fill for padding effect.
#   BG=$(shape_id ppt-cli add-textbox "$PPTX" N "" \
#     --x 0.4in --y 1.4in --w 5.7in --h 3.2in)
#   ppt-cli set-fill "$PPTX" N --shape-id "$BG" --color "$CARD_BG"
#   # Inner content: monospace font, light text.
#   SID=$(shape_id ppt-cli add-textbox "$PPTX" N "$CODE" \
#     --x 0.6in --y 1.6in --w 5.3in --h 2.8in)
#   ppt-cli set-font "$PPTX" N --shape-id "$SID" \
#     --name Consolas --color "$TEXT_LIGHT" --size 13
#
# @pattern colored-callout-box (educational)
#   # Background container for key takeaways / definitions.
#   BG=$(shape_id ppt-cli add-textbox "$PPTX" N "" \
#     --x 0.5in --y 5in --w 9in --h 1.2in)
#   ppt-cli set-fill "$PPTX" N --shape-id "$BG" --color "$ACCENT_TINT"
#   SID=$(shape_id ppt-cli add-textbox "$PPTX" N "$TAKEAWAY" \
#     --x 0.7in --y 5.1in --w 8.6in --h 1in)
#   ppt-cli set-font "$PPTX" N --shape-id "$SID" --size 14 --bold
#
# @pattern diagram-nodes (technical)
#   # Build simple diagrams from positioned textboxes.
#   # Each node: textbox with label + fill.
#   NODE=$(shape_id ppt-cli add-textbox "$PPTX" N "$LABEL" \
#     --x 1in --y 2in --w 2in --h 0.6in)
#   ppt-cli set-fill "$PPTX" N --shape-id "$NODE" --color "$CARD_BG"
#   ppt-cli set-font "$PPTX" N --shape-id "$NODE" \
#     --size 12 --color "$TEXT_LIGHT" --bold
#   # Connecting lines: thin empty textboxes filled with accent color.
#   LINE=$(shape_id ppt-cli add-textbox "$PPTX" N "" \
#     --x 3in --y 2.25in --w 1in --h 0.04in)
#   ppt-cli set-fill "$PPTX" N --shape-id "$LINE" --color "$ACCENT"
#
# ─────────────────────────── NAVIGATION & STRUCTURE ────────────────────
#
# @pattern progress-indicator (educational)
#   # Consistent corner position on every slide. Same x/y each time.
#   SID=$(shape_id ppt-cli add-textbox "$PPTX" N "Section $SEC of $TOTAL" \
#     --x 11in --y 7in --w 2in --h 0.3in)
#   ppt-cli set-font "$PPTX" N --shape-id "$SID" \
#     --size 10 --color "$MUTED"
#
# @pattern numbered-step-marker (educational)
#   # Colored square with number — acts as a step indicator.
#   BG=$(shape_id ppt-cli add-textbox "$PPTX" N "" \
#     --x 0.5in --y 1.5in --w 0.4in --h 0.4in)
#   ppt-cli set-fill "$PPTX" N --shape-id "$BG" --color "$PRIMARY"
#   SID=$(shape_id ppt-cli add-textbox "$PPTX" N "$STEP_NUM" \
#     --x 0.5in --y 1.5in --w 0.4in --h 0.4in)
#   ppt-cli set-font "$PPTX" N --shape-id "$SID" \
#     --size 16 --bold --color '#FFFFFF'
#
# ─────────────────────────── CREATIVE TYPOGRAPHY ───────────────────────
#
# @pattern asymmetric-text (creative)
#   # Large left margin for visual tension. Title does NOT start at 0.5in.
#   SID=$(shape_id ppt-cli add-textbox "$PPTX" N "$TITLE" \
#     --x 3in --y 2.5in --w 9.5in --h 1.5in)
#   ppt-cli set-font "$PPTX" N --shape-id "$SID" \
#     --size 48 --bold --color '#FFFFFF'
#
# ─────────────────────────── TEMPLATE & STYLING ────────────────────────
#
# @pattern build-from-template
#   # Create deck from a saved template, then fill placeholders.
#   # ppt-cli create "$PPTX" --template "$TEMPLATE_NAME"
#   # ppt-cli add-slide "$PPTX" --layout "Title Slide"
#   # ppt-cli set-title "$PPTX" 1 "Slide Title"
#   # ppt-cli add-slide "$PPTX" --layout "bg_white"
#   # ppt-cli set-text "$PPTX" 2 --shape-id <placeholder_id> "Body content"
#   # ppt-cli add-image "$PPTX" 2 chart.png --x 1in --y 2in --w 8in
#   # ppt-cli add-table "$PPTX" 3 data.csv --x 1in --y 1.5in
#   # ppt-cli set-notes "$PPTX" 1 "Speaker notes"
#
# @pattern template-layout-slide
#   # For slides using a branded template layout with placeholders:
#   # Only delete freehand shapes; PRESERVE placeholder shapes.
#   for sid in $(ppt-cli dump "$PPTX" N 2>/dev/null \
#     | python3 -c "import sys,json
#   for s in json.load(sys.stdin).get('shapes',[]):
#       if 'placeholder_idx' not in s: print(s['id'])" 2>/dev/null); do
#     ppt-cli delete-shape "$PPTX" N --shape-id "$sid" > /dev/null
#   done
#   ppt-cli set-title "$PPTX" N "Slide Title"
#   ppt-cli set-text "$PPTX" N --shape-id <body_placeholder_id> "Body content"
#   # Add freehand shapes only for elements the layout doesn't provide.
#
#   # WARNING: set-title + set-text into placeholders is the STARTING POINT,
#   # not the complete slide. For any content slide with structure (lists,
#   # categories, workflows, multi-section), add freehand shapes ON TOP of
#   # placeholders: accent bars, callout panels, stat numbers, extra textboxes
#   # with independent styling. Placeholder-only slides are text dumps.
#   # Use placeholders for the title and maybe a short subtitle, then compose
#   # the actual content from freehand shapes. Or use team-review/blank layouts
#   # and compose everything from scratch.
#
# @pattern fine-tune-styling
#   # Post-build styling adjustments — font, fill, position.
#   ppt-cli set-font "$PPTX" N --shape-id "$SID" \
#     --bold --size 28 --color "$ACCENT"
#   ppt-cli set-fill "$PPTX" N --shape-id "$SID" --color "$CARD_BG"
#   ppt-cli set-position "$PPTX" N --shape-id "$SID" \
#     --x 2in --y 1in --w 6in
#
# ────────────────────────────────────────────────────────────────────────

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
