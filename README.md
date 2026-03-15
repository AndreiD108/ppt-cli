# ppt-cli

A command-line tool for creating, inspecting, and editing PowerPoint (.pptx) presentations. Built for AI agents — every command produces structured JSON, commands compose naturally into multi-step workflows, and a bundled agent skill provides design guidelines, image generation guidance, and workflow examples that help agents produce professional results.

## Install

```
pipx install ppt-cli
```

## What it can do

**Create decks from scratch or from templates.** Start with a blank deck or use a saved template that carries your corporate theme, masters, and layouts. Add slides by choosing from the available layouts, reorder them, duplicate them, or remove them. Set a default template so new decks pick up your branding automatically.

**Inspect any existing deck.** Get a structured view of what's inside a .pptx: slide count, dimensions, available layouts, shape positions, text content, and styles — all as JSON. The `peek` command gives a compact overview with shape IDs and text previews; `dump` gives the full detail. You can also render any slide to a PNG screenshot for visual review.

**Edit text and content.** Set text on any shape by ID, set slide titles, write speaker notes. Find-and-replace across every slide in the deck — useful for rebranding or fixing repeated typos. Insert images from local files or generate them on the fly with AI. Add textboxes with font styling, or add tables directly from CSV data.

**Generate images with AI.** Create images from text descriptions using Google Gemini, with control over resolution (up to 2K), aspect ratio, and grounding (web search, image search, or both for more accurate results). Generate multiple variations in parallel to pick the best one, or generate and insert directly into a slide in a single command. Pass reference images with `--ref` for style matching, character consistency, background editing, or compositing — up to 14 images per generation.

**Fine-tune styling and layout.** Set font properties — bold, italic, size, color, font family — on any shape. Set fill colors. Move and resize shapes with precise positioning using inches, centimeters, points, or pixels. Every styling command addresses shapes by their stable ID, so you can make targeted adjustments without affecting the rest of the slide.

**Work at the OOXML level when you need full control.** The `internals` commands go beyond what the high-level API covers. `analyze` gives you a structured inventory of every master, layout, and media file in the deck, including which layouts are actually used by slides and which are dead weight. `fingerprint` detects structural patterns across slides — for instance, finding that slides 5, 11, and 23 all share the same freehand card layout that nobody turned into a proper template. You can then stage the deck (extract it for editing), add, delete, or duplicate layouts and masters with full cross-reference syncing (relationships, content types, and XML references are all updated automatically), and rebuild into a valid .pptx. This is how you create and evolve templates — not by hand-editing ZIP files, but with commands that guarantee structural integrity.

**Agent skill with design and workflow guidance.** A bundled skill ships with the package — a hierarchical set of files that AI agents read progressively as they work. It covers four design directions (business, technical, creative, educational) with complete palettes, typography pairings, and layout preferences for each. It includes an image generation guide with prompt structure, style vocabulary, and practical patterns. It provides QA procedures, a user interaction flow, and ten end-to-end workflow examples. Agents load only what they need for the current task rather than ingesting everything upfront.

## Example workflows

### Turn an existing deck into a reusable template

Someone sends you a polished quarterly report. You want to strip the content but keep the theme, layouts, and branding for future use:

```
ppt-cli internals analyze quarterly-report.pptx    # see what's inside: layouts, masters, media
ppt-cli internals stage quarterly-report.pptx       # extract for editing
ppt-cli internals delete slide <dir> --slide 4      # remove content slides
ppt-cli internals delete layout <dir> --layout "unused-thing"  # clean up dead layouts
ppt-cli internals build-template <dir> --name=quarterly --description="Q report template"
```

Now `ppt-cli create new-report.pptx --template quarterly` starts from that clean foundation.

### Build a branded presentation from scratch

```
ppt-cli create q1-report.pptx --template quarterly
ppt-cli add-slide q1-report.pptx --layout "Title Slide"
ppt-cli set-title q1-report.pptx 1 "Q1 2026 Results"
ppt-cli add-slide q1-report.pptx --layout "bg_white"
ppt-cli add-image q1-report.pptx 2 --prompt "clean bar chart showing 15% YoY revenue growth, corporate blue palette" --w 8in --h 4.5in
ppt-cli add-table q1-report.pptx 3 financials.csv --x 1in --y 1.5in
ppt-cli set-notes q1-report.pptx 1 "Open with the new product line announcement"
```

Slide by slide: pick a layout, fill placeholders, drop in images and tables, add speaker notes. The agent can inspect results at any point with `peek` or `screenshot` and adjust.

### Bulk edit an existing deck

Rebranding, or a company name changed across 30 slides:

```
ppt-cli replace-text deck.pptx "Acme Corp" "NewCo Inc."
ppt-cli replace-text deck.pptx "FY2025" "FY2026"
ppt-cli peek deck.pptx --all    # verify the changes look right
```

## Commands

| | |
|---|---|
| `create` | Create a new .pptx (blank, widescreen, or from template) |
| `info` | Deck metadata — slide count, dimensions, available layouts |
| `list` | List slides with titles and shape counts |
| `dump` | Full JSON dump of slide shapes, positions, text, styles |
| `peek` | Compact shape summary — IDs, types, text preview |
| `screenshot` | Render slides as PNG images |
| `set-text` | Set text on a shape |
| `set-title` | Set slide title |
| `set-notes` | Set speaker notes |
| `replace-text` | Find and replace text across all slides |
| `add-slide` | Add a slide (with layout selection) |
| `delete-slide` | Delete a slide |
| `reorder` | Move a slide to a new position |
| `duplicate-slide` | Duplicate a slide |
| `add-image` | Add image from file or generate with AI |
| `image-gen` | Generate images from text (standalone, no deck needed) |
| `add-textbox` | Add a textbox with optional styling |
| `add-table` | Add a table from CSV |
| `delete-shape` | Delete a shape |
| `set-font` | Set font properties (bold, italic, size, color, family) |
| `set-fill` | Set shape fill color |
| `set-position` | Move or resize a shape |
| `internals` | Low-level OOXML: stage, analyze, fingerprint, build, mutate |
| `template` | Save, list, show, delete, rename, set default |

All commands produce JSON output. Slides are 1-based. Shapes are addressed by `--shape-id`. Lengths accept units: `1in`, `2.5cm`, `72pt`, `100px`, `914400emu` (default: inches). Colors are `#RRGGBB`.

Run `ppt-cli <command> --help` for full usage of any command.

## Requirements

- **Python 3.10+**
- **GEMINI_API_KEY** environment variable — required only for AI image generation (`add-image --prompt` and `image-gen`). Get one at [Google AI Studio](https://aistudio.google.com/api-keys) or [Google Cloud Console](https://console.cloud.google.com/apis/credentials).
- **LibreOffice** and **poppler-utils** (`pdftoppm`) — required only for the `screenshot` command.

## Disclaimer

ppt-cli is not affiliated with or endorsed by Microsoft. PowerPoint is a trademark of Microsoft Corporation.
