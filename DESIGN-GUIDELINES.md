# ppt-cli Design Guidelines

A reference for building professional, well-designed presentations using `ppt-cli`. These guidelines cover typography, color, layout, spacing, content structure, and quality assurance. Each section includes the corresponding `ppt-cli` commands.

---

## Table of Contents

1. [Slide Dimensions and Setup](#slide-dimensions-and-setup)
2. [Color Palette](#color-palette)
3. [Typography](#typography)
4. [Layout Principles](#layout-principles)
5. [Spacing and Margins](#spacing-and-margins)
6. [Content Structure](#content-structure)
7. [Images and Visual Elements](#images-and-visual-elements)
8. [Tables and Data Display](#tables-and-data-display)
9. [Text Formatting](#text-formatting)
10. [Slide Backgrounds and Fills](#slide-backgrounds-and-fills)
11. [Common Mistakes to Avoid](#common-mistakes-to-avoid)
12. [Quality Assurance Workflow](#quality-assurance-workflow)
13. [Template Workflow](#template-workflow)
14. [Reference: Color Palettes](#reference-color-palettes)
15. [Reference: Font Pairings](#reference-font-pairings)

---

## Slide Dimensions and Setup

### Choose the right aspect ratio

Standard widescreen (16:9) is the default for modern presentations. Use `--widescreen` for the wider 13.333" x 7.5" format when projecting on large screens.

```bash
# Standard 10" x 7.5" (default)
ppt-cli create deck.pptx

# Widescreen 16:9 (13.333" x 7.5")
ppt-cli create deck.pptx --widescreen

# Custom dimensions
ppt-cli create deck.pptx --width 10in --height 5.625in
```

### Common dimension reference

| Format | Width | Height | Use case |
|--------|-------|--------|----------|
| Default | 10" | 7.5" | General purpose |
| Widescreen | 13.333" | 7.5" | Conference screens, webinars |
| 16:9 narrow | 10" | 5.625" | Standard HD monitors |
| 4:3 | 10" | 7.5" | Older projectors |

All positioning in ppt-cli uses these dimensions as the coordinate space. Plan your layouts accordingly.

---

## Color Palette

### Pick a bold, content-informed palette

The palette should feel designed for the specific topic. If swapping your colors into a completely different presentation would still "work," you have not made specific enough choices. Do not default to generic blue.

### Dominance over equality

One color should dominate (60-70% visual weight), with 1-2 supporting tones and one sharp accent. Never give all colors equal weight.

- **Primary (60-70%)**: Backgrounds, large shape fills
- **Secondary (20-30%)**: Supporting elements, cards, section dividers
- **Accent (5-10%)**: Key stats, callout highlights, important labels

### Dark/light contrast structure

Use dark backgrounds for title and conclusion slides, light backgrounds for content slides ("sandwich" structure). Or commit to dark throughout for a premium feel.

### Applying colors with ppt-cli

```bash
# Set a shape's fill color (backgrounds, cards, accent bars)
ppt-cli set-fill deck.pptx 1 --shape-id 5 --color "#1E2761"

# Set font color for contrast against background
ppt-cli set-font deck.pptx 1 --shape-id 5 --color "#FFFFFF"

# Add a textbox with a specific font color
ppt-cli add-textbox deck.pptx 1 "Key Metric" \
  --font-color "#F96167" --font-size 60 --bold \
  --x 1in --y 2in --w 8in --h 1.5in

# Add a colored accent shape
ppt-cli add-textbox deck.pptx 1 "" \
  --x 0.5in --y 0.5in --w 0.08in --h 3in
# Then fill it:
ppt-cli set-fill deck.pptx 1 --shape-id <id> --color "#F96167"
```

---

## Typography

### Choose an interesting font pairing

Do not default to Arial. Pick a header font with personality and pair it with a clean body font.

| Header Font | Body Font | Character |
|-------------|-----------|-----------|
| Georgia | Calibri | Classic and warm |
| Arial Black | Arial | Bold and corporate |
| Calibri | Calibri Light | Clean and modern |
| Cambria | Calibri | Traditional with modern body |
| Trebuchet MS | Calibri | Friendly and approachable |
| Impact | Arial | High-impact headlines |
| Palatino | Garamond | Elegant and editorial |
| Consolas | Calibri | Technical, developer-focused |

### Size hierarchy

Maintain strong size contrast so titles stand out from body text. Titles need 36pt+ to visually separate from 14-16pt body copy.

| Element | Size | Weight |
|---------|------|--------|
| Slide title | 36-44pt | Bold |
| Section header | 20-24pt | Bold |
| Body text | 14-16pt | Regular |
| Captions / footnotes | 10-12pt | Regular, muted color |
| Large stat callouts | 60-72pt | Bold |

### Applying typography with ppt-cli

```bash
# Set font family and size on a shape
ppt-cli set-font deck.pptx 1 --shape-id 5 \
  --name "Georgia" --size 40 --bold --color "#1E2761"

# Body text: lighter weight, smaller size
ppt-cli set-font deck.pptx 1 --shape-id 8 \
  --name "Calibri" --size 15 --no-bold --color "#363636"

# Caption text: small, muted
ppt-cli set-font deck.pptx 1 --shape-id 12 \
  --name "Calibri" --size 11 --color "#999999"

# Add a title textbox with font properties inline
ppt-cli add-textbox deck.pptx 1 "Quarterly Results" \
  --font-size 40 --bold --font-color "#1E2761" \
  --x 0.5in --y 0.3in --w 9in --h 1in

# Italic text for accent/taglines
ppt-cli set-font deck.pptx 1 --shape-id 7 --italic --size 16

# Remove bold from body text that inherited it
ppt-cli set-font deck.pptx 1 --shape-id 9 --no-bold --no-italic
```

### Bold everything that is a header or label

Bold all of these:
- Slide titles
- Section headers within a slide
- Inline labels (e.g., "Status:", "Revenue:") at the start of a line

```bash
ppt-cli set-font deck.pptx 2 --shape-id 5 --bold
```

---

## Layout Principles

### Use varied layouts

Monotonous presentations are a common failure mode. Do not repeat the same layout slide after slide. Actively vary the structure.

**Layout options to rotate through:**
- Two-column (text left, image/illustration right)
- Icon + text rows (icon in colored circle, bold header, description)
- 2x2 or 2x3 grid (image on one side, grid of content blocks on other)
- Half-bleed image (full left or right half) with content overlay
- Full-bleed background image with text overlay
- Large stat callout (big number 60-72pt with small label below)
- Comparison columns (before/after, pros/cons, side-by-side)
- Timeline or process flow (numbered steps)
- Quote or callout slides
- Section divider slides

### Match content type to layout style

- Key points -> bullet slide or icon + text rows
- Team info -> multi-column with images
- Testimonials -> quote slide
- Metrics -> stat callout or comparison columns
- Processes -> timeline or numbered steps

### Commit to a visual motif

Pick ONE distinctive element and repeat it across every slide: rounded image frames, icons in colored circles, thick single-side borders, etc. Consistency builds a professional feel.

### Implementing layouts with ppt-cli

```bash
# Use template layouts when available
ppt-cli add-slide deck.pptx --layout "Title Slide"
ppt-cli add-slide deck.pptx --layout "Two Content"
ppt-cli add-slide deck.pptx --layout "Blank"

# See available layouts in a template
ppt-cli info deck.pptx

# Build a two-column layout manually on a blank slide
# Left column: text
ppt-cli add-textbox deck.pptx 2 "Key Findings" \
  --x 0.5in --y 0.5in --w 4.5in --h 1in \
  --font-size 28 --bold --font-color "#1E2761"

ppt-cli add-textbox deck.pptx 2 "Finding details here..." \
  --x 0.5in --y 1.8in --w 4.5in --h 4in \
  --font-size 15 --font-color "#363636"

# Right column: image
ppt-cli add-image deck.pptx 2 chart.png \
  --x 5.5in --y 0.5in --w 4in --h 5in

# Large stat callout
ppt-cli add-textbox deck.pptx 3 "42%" \
  --x 1in --y 1.5in --w 8in --h 2in \
  --font-size 72 --bold --font-color "#F96167"

ppt-cli add-textbox deck.pptx 3 "increase in customer retention" \
  --x 1in --y 3.5in --w 8in --h 1in \
  --font-size 18 --font-color "#666666"
```

---

## Spacing and Margins

### Minimum margins

Maintain at least 0.5" margins from all slide edges. Content that is too close to the edge looks cramped and unprofessional.

### Gaps between content blocks

Use 0.3-0.5" between content blocks. Choose one gap size and use it consistently throughout the deck. Do not mix spacing randomly.

### Breathing room

Leave breathing room. Do not fill every inch of the slide. White space is a design element, not wasted space.

### Positioning with ppt-cli

```bash
# Move a shape with precise positioning
ppt-cli set-position deck.pptx 1 --shape-id 5 \
  --x 0.5in --y 0.5in --w 9in --h 1in

# Resize a shape
ppt-cli set-position deck.pptx 1 --shape-id 5 \
  --w 4in --h 3in

# Place elements with consistent margins (0.5" from edges on a 10" x 7.5" slide)
# Left column starts at x=0.5in
# Right edge at x=9.5in (0.5in margin from 10in width)
# Top content at y=0.5in
# Bottom limit at y=7.0in (0.5in margin from 7.5in height)

# Two-column layout with 0.5in gap between columns:
# Left column:  x=0.5in, w=4.25in  (ends at 4.75in)
# Right column: x=5.25in, w=4.25in (ends at 9.5in)
# Gap: 5.25 - 4.75 = 0.5in

# Three-column layout with 0.3in gaps:
# Col 1: x=0.5in, w=2.8in   (ends at 3.3in)
# Col 2: x=3.6in, w=2.8in   (ends at 6.4in)
# Col 3: x=6.7in, w=2.8in   (ends at 9.5in)
```

### Supported units

ppt-cli supports multiple units: `1in`, `2.5cm`, `72pt`, `100px`, `914400emu`. Default is inches. Use inches for consistency with standard slide dimensions.

---

## Content Structure

### Every slide needs a visual element

Text-only slides are forgettable. Every slide should include at least one of: image, chart, icon, shape, or table. Even a simple colored rectangle or accent bar adds visual interest.

### Left-align body text

Left-align paragraphs and lists. Center only titles and short callout text. Never center body text or long paragraphs.

### Separate items into distinct elements

When content has multiple items (numbered lists, steps, sections), create separate text elements for each. Never concatenate everything into one block of text.

```bash
# Each step gets its own textbox for clean layout
ppt-cli add-textbox deck.pptx 2 "Step 1: Research" \
  --x 0.5in --y 1.5in --w 9in --h 0.5in \
  --font-size 18 --bold --font-color "#1E2761"

ppt-cli add-textbox deck.pptx 2 "Conduct market analysis and competitor review." \
  --x 0.5in --y 2.0in --w 9in --h 0.5in \
  --font-size 15 --font-color "#363636"

ppt-cli add-textbox deck.pptx 2 "Step 2: Design" \
  --x 0.5in --y 2.8in --w 9in --h 0.5in \
  --font-size 18 --bold --font-color "#1E2761"

ppt-cli add-textbox deck.pptx 2 "Create wireframes and prototypes." \
  --x 0.5in --y 3.3in --w 9in --h 0.5in \
  --font-size 15 --font-color "#363636"
```

### Use newlines for multi-line text in a single shape

When a single text shape needs multiple lines, use `\n` in the text argument.

```bash
ppt-cli set-text deck.pptx 1 --shape-id 5 \
  "Line one\nLine two\nLine three"
```

### Speaker notes

Add speaker notes for context that should not appear on screen.

```bash
ppt-cli set-notes deck.pptx 1 "Mention the new product line here"
```

---

## Images and Visual Elements

### Add images with explicit positioning

Always specify position and size for images. Let them anchor to the layout grid.

```bash
# Full-width image below a title
ppt-cli add-image deck.pptx 2 photo.png \
  --x 0.5in --y 1.5in --w 9in --h 5in

# Half-bleed image (left half of slide)
ppt-cli add-image deck.pptx 3 hero.jpg \
  --x 0in --y 0in --w 5in --h 7.5in

# Small image in a grid position
ppt-cli add-image deck.pptx 4 icon.png \
  --x 1in --y 2in --w 1.5in --h 1.5in
```

### AI-generated images

Generate contextual images directly with `--prompt` (requires GEMINI_API_KEY).

```bash
# Generate and place in one command
ppt-cli add-image deck.pptx 2 \
  --prompt "modern office workspace, minimalist, soft lighting" \
  --x 5in --y 0.5in --w 4.5in --h 6in \
  --resolution 2k --ratio 3:4

# Generate standalone for reuse
ppt-cli image-gen "abstract geometric pattern, teal and navy" \
  --resolution 2k --ratio 16:9 -o /tmp/bg.png

# Then place it
ppt-cli add-image deck.pptx 1 /tmp/bg.png \
  --x 0in --y 0in --w 10in --h 7.5in
```

### Image sizing guidelines

- **Full-bleed background**: `--x 0in --y 0in --w <slide_width> --h <slide_height>`
- **Half-bleed**: Cover exactly half the slide width or height
- **Inline images**: Keep proportional; calculate aspect ratio manually
- **Icons**: Small sizes (0.4-0.6in square) next to text

---

## Tables and Data Display

### Add tables from CSV

Prepare data as CSV, then place the table with explicit positioning.

```bash
# Create a CSV file first, then add the table
ppt-cli add-table deck.pptx 3 data.csv \
  --x 0.5in --y 1.5in --w 9in --h 4in
```

### Data display alternatives

Not everything needs a table. Consider these alternatives:

- **Large stat callouts**: Big numbers (60-72pt) with small labels below
- **Comparison columns**: Side-by-side textboxes for before/after or pros/cons
- **Timeline**: Numbered steps with connecting visual elements

```bash
# Stat callout approach
ppt-cli add-textbox deck.pptx 3 "2.4M" \
  --x 1in --y 2in --w 3in --h 1.5in \
  --font-size 60 --bold --font-color "#028090"

ppt-cli add-textbox deck.pptx 3 "Active Users" \
  --x 1in --y 3.5in --w 3in --h 0.5in \
  --font-size 14 --font-color "#666666"

ppt-cli add-textbox deck.pptx 3 "$18.2M" \
  --x 5in --y 2in --w 3in --h 1.5in \
  --font-size 60 --bold --font-color "#028090"

ppt-cli add-textbox deck.pptx 3 "Annual Revenue" \
  --x 5in --y 3.5in --w 3in --h 0.5in \
  --font-size 14 --font-color "#666666"
```

---

## Text Formatting

### Bulk text replacement

Use `replace-text` for rebranding or fixing recurring text across all slides.

```bash
ppt-cli replace-text deck.pptx "Acme Corp" "NewCo Inc."
ppt-cli replace-text deck.pptx "FY2025" "FY2026"
```

### Set titles consistently

Use `set-title` for slide titles (targets the title placeholder specifically).

```bash
ppt-cli set-title deck.pptx 1 "Q1 2026 Results"
ppt-cli set-title deck.pptx 2 "Market Overview"
ppt-cli set-title deck.pptx 3 "Financial Summary"
```

### Use italic sparingly for accent

Italic text works for key stats, taglines, or callout quotes. Do not italicize body paragraphs.

```bash
ppt-cli set-font deck.pptx 1 --shape-id 7 --italic --size 16 --color "#666666"
```

---

## Slide Backgrounds and Fills

### Dark backgrounds for impact slides

Use dark fills on title, section divider, and conclusion slides for visual weight.

```bash
# After adding shapes, set dark fills
# For slide-level background: use template layouts with dark backgrounds,
# or add a full-slide rectangle as a background shape

# Full-slide background rectangle
ppt-cli add-textbox deck.pptx 1 "" \
  --x 0in --y 0in --w 10in --h 7.5in
# Then peek to get its shape ID, and fill it
ppt-cli set-fill deck.pptx 1 --shape-id <id> --color "#1E2761"
# Ensure text shapes are layered on top with light font colors
ppt-cli set-font deck.pptx 1 --shape-id <text_id> --color "#FFFFFF"
```

### Accent bars and colored shapes

Use thin colored rectangles as accent elements (side borders on cards, section dividers).

```bash
# Vertical accent bar on a card
ppt-cli add-textbox deck.pptx 2 "" \
  --x 0.5in --y 1.5in --w 0.08in --h 2in
ppt-cli set-fill deck.pptx 2 --shape-id <id> --color "#F96167"
```

**Warning**: Never use accent lines directly under titles. This is a hallmark of generic, low-effort slides. Use whitespace or background color contrast instead.

---

## Common Mistakes to Avoid

### Layout mistakes

| Mistake | Fix |
|---------|-----|
| Repeating the same layout on every slide | Vary columns, cards, callouts, and image placements across slides |
| Centering body text | Left-align paragraphs and lists; center only titles |
| Text-only slides | Add images, icons, charts, or shapes to every slide |
| Styling one slide and leaving the rest plain | Commit fully to a style throughout the deck |

### Spacing mistakes

| Mistake | Fix |
|---------|-----|
| Elements too close to slide edges | Maintain 0.5" minimum margins |
| Inconsistent gaps between blocks | Choose 0.3" or 0.5" and use consistently |
| Cramming content without breathing room | Leave white space; it is a design element |
| Elements nearly touching or overlapping | Keep at least 0.3" gap between distinct elements |

### Typography mistakes

| Mistake | Fix |
|---------|-----|
| Insufficient size contrast | Titles need 36pt+ to stand out from 14-16pt body |
| Defaulting to Arial for everything | Pick a header font with personality |
| Using italic on body text | Reserve italic for accents, taglines, and quotes |

### Color mistakes

| Mistake | Fix |
|---------|-----|
| Defaulting to generic blue | Pick colors that reflect the specific topic |
| Low-contrast text on backgrounds | Ensure strong contrast (light on dark, dark on light) |
| Low-contrast icons | Place icons on contrasting circles or use high-contrast colors |
| Equal weight across all colors | One color dominates (60-70%), others support |

### Content mistakes

| Mistake | Fix |
|---------|-----|
| Concatenating multiple items into one text block | Create separate elements for each item |
| Leaving placeholder text from templates | Search and replace all placeholder content |
| Forgetting speaker notes | Add notes for key talking points |
| Text overflow from longer replacements | Check with screenshot after text changes |

---

## Quality Assurance Workflow

### Assume there are problems

Your first output is almost never correct. Approach QA as a bug hunt, not a confirmation step.

### Content QA

```bash
# Inspect all slides for text content
ppt-cli peek deck.pptx --all

# Check specific slides in detail
ppt-cli dump deck.pptx 3

# List all slides with titles
ppt-cli list deck.pptx
```

### Visual QA

```bash
# Render all slides as PNG images
ppt-cli screenshot deck.pptx --all

# Render specific slides
ppt-cli screenshot deck.pptx 1 3 5

# Higher resolution for detailed inspection
ppt-cli screenshot deck.pptx --all --dpi 300
```

### What to look for

- Overlapping elements (text through shapes, stacked elements)
- Text overflow or cut off at edges/box boundaries
- Elements too close (< 0.3" gaps) or nearly touching
- Uneven gaps (large empty area in one place, cramped in another)
- Insufficient margin from slide edges (< 0.5")
- Columns or similar elements not aligned consistently
- Low-contrast text (light text on light background)
- Text boxes too narrow causing excessive wrapping
- Leftover placeholder content

### Verification loop

1. Build slides
2. Screenshot and inspect: `ppt-cli screenshot deck.pptx --all`
3. List issues found
4. Fix issues using `set-position`, `set-font`, `set-text`, `set-fill`, `delete-shape`
5. Re-screenshot affected slides: `ppt-cli screenshot deck.pptx 3 5`
6. Repeat until a full pass reveals no new issues

### Structural inspection

```bash
# Analyze template structure
ppt-cli internals analyze deck.pptx

# Fingerprint shape positions and sizes per slide
ppt-cli internals fingerprint deck.pptx

# Fingerprint a specific slide
ppt-cli internals fingerprint deck.pptx --slide 3
```

---

## Template Workflow

### Using templates for consistency

Templates ensure consistent styling across presentations. Build a template once, reuse it.

```bash
# Save a polished deck as a template
ppt-cli template save quarterly-report deck.pptx \
  --description "Q report with corporate branding"

# Set as default
ppt-cli template default quarterly-report

# Create new decks from the template
ppt-cli create q1-report.pptx --template quarterly-report

# Or, if default is set:
ppt-cli create q1-report.pptx

# List available templates
ppt-cli template list

# Inspect a template's layouts
ppt-cli template show quarterly-report
```

### Building from a template

```bash
# Create deck from template
ppt-cli create deck.pptx --template my-template

# Add slides using template layouts
ppt-cli add-slide deck.pptx --layout "Title Slide"
ppt-cli add-slide deck.pptx --layout "Two Content"
ppt-cli add-slide deck.pptx --layout "Blank"

# Fill in content
ppt-cli set-title deck.pptx 1 "Presentation Title"
ppt-cli set-text deck.pptx 2 --shape-id 3 "Body content here"
ppt-cli add-image deck.pptx 2 chart.png --x 5in --y 1.5in --w 4in
ppt-cli add-table deck.pptx 3 data.csv --x 0.5in --y 1.5in --w 9in
ppt-cli set-notes deck.pptx 1 "Opening remarks go here"
```

### Evolving templates

When branding changes, update the template rather than fixing individual decks.

```bash
# Stage the template for editing
ppt-cli internals stage /path/to/template.pptx

# Make structural changes
ppt-cli internals delete layout <staged-dir> --layout "unused-layout"
ppt-cli internals add layout <staged-dir> --name "new-section" --master 1
ppt-cli internals duplicate layout <staged-dir> \
  --source "finance-green" --name "finance-red"

# Rebuild template
ppt-cli internals build-template <staged-dir> \
  --name quarterly-report --description "Updated branding" -f
```

### Reverse-engineering existing decks

When given an existing presentation to analyze or replicate:

```bash
# Full structural analysis
ppt-cli internals analyze source.pptx

# Shape-level fingerprint (positions, sizes, colors)
ppt-cli internals fingerprint source.pptx

# Quick text/shape overview
ppt-cli peek source.pptx --all

# Visual overview
ppt-cli screenshot source.pptx --all
```

---

## Reference: Color Palettes

Choose colors that match your topic. Each palette has a dominant primary, a supporting secondary, and a sharp accent.

| Theme | Primary | Secondary | Accent |
|-------|---------|-----------|--------|
| **Midnight Executive** | `#1E2761` (navy) | `#CADCFC` (ice blue) | `#FFFFFF` (white) |
| **Forest & Moss** | `#2C5F2D` (forest) | `#97BC62` (moss) | `#F5F5F5` (cream) |
| **Coral Energy** | `#F96167` (coral) | `#F9E795` (gold) | `#2F3C7E` (navy) |
| **Warm Terracotta** | `#B85042` (terracotta) | `#E7E8D1` (sand) | `#A7BEAE` (sage) |
| **Ocean Gradient** | `#065A82` (deep blue) | `#1C7293` (teal) | `#21295C` (midnight) |
| **Charcoal Minimal** | `#36454F` (charcoal) | `#F2F2F2` (off-white) | `#212121` (black) |
| **Teal Trust** | `#028090` (teal) | `#00A896` (seafoam) | `#02C39A` (mint) |
| **Berry & Cream** | `#6D2E46` (berry) | `#A26769` (dusty rose) | `#ECE2D0` (cream) |
| **Sage Calm** | `#84B59F` (sage) | `#69A297` (eucalyptus) | `#50808E` (slate) |
| **Cherry Bold** | `#990011` (cherry) | `#FCF6F5` (off-white) | `#2F3C7E` (navy) |

**Usage pattern**: Use the primary for large areas (backgrounds, header bars). Use the secondary for cards, content area backgrounds, and supporting shapes. Use the accent sparingly for emphasis -- stat callouts, key labels, active states.

---

## Reference: Font Pairings

| Header Font | Body Font | Best For |
|-------------|-----------|----------|
| Georgia | Calibri | Business reports, formal decks |
| Arial Black | Arial | Corporate presentations |
| Calibri | Calibri Light | Clean, modern decks |
| Cambria | Calibri | Traditional content with modern readability |
| Trebuchet MS | Calibri | Friendly, approachable topics |
| Impact | Arial | High-impact, attention-grabbing titles |
| Palatino | Garamond | Elegant, editorial presentations |
| Consolas | Calibri | Technical, developer-focused content |

Apply consistently across the entire deck:

```bash
# Title shapes on every slide: header font, bold, 40pt
ppt-cli set-font deck.pptx 1 --shape-id <title_id> \
  --name "Georgia" --size 40 --bold

# Body shapes on every slide: body font, regular, 15pt
ppt-cli set-font deck.pptx 1 --shape-id <body_id> \
  --name "Calibri" --size 15 --no-bold
```

---

## Slide-by-Slide Build Checklist

For each slide you create, verify:

1. **Layout variety**: Is this layout different from the previous slide?
2. **Visual element**: Does the slide have at least one non-text element?
3. **Title prominence**: Is the title 36pt+ and bold?
4. **Body alignment**: Is body text left-aligned (not centered)?
5. **Margins**: Is everything at least 0.5" from slide edges?
6. **Gaps**: Are gaps between elements consistent (0.3" or 0.5")?
7. **Color contrast**: Is text readable against its background?
8. **Font consistency**: Are fonts matching the chosen pairing?
9. **Content completeness**: No placeholder text remaining?
10. **Speaker notes**: Added where needed?

```bash
# Quick verification commands
ppt-cli peek deck.pptx --all           # Text content check
ppt-cli screenshot deck.pptx --all     # Visual check
ppt-cli list deck.pptx                 # Slide order and titles
ppt-cli dump deck.pptx 3               # Detailed shape inspection
```
