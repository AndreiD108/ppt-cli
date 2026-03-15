# QA and Deck Analysis

How to verify your own output and analyze existing presentations. These are workflow procedures, not design rules — they apply regardless of design direction.

---

## Quality assurance

### Mindset

Your first output is almost never correct. Approach QA as a bug hunt, not a confirmation step. The question is not "does this look okay?" — it is "what did I get wrong?" If you inspect your output expecting to find problems, you will find them. If you inspect expecting approval, you will miss them.

### When to run QA

Whether and how to run the verification loop depends on the user's involvement level (set during planning — see `2-user-experience.md` Step 0). The plan file's session context block records this decision:

- **Autopilot:** Run the full verification loop automatically after building. Do not ask — the user already delegated all decisions to you.
- **Key Decisions:** Ask the user before starting QA whether they want you to self-verify and iterate, or prefer to review the output themselves.
- **Full Control:** Ask, and offer to walk through each slide's screenshot together.

The verification loop can take a while, and some users prefer to drive it themselves visually — that is why Key Decisions and Full Control users are asked. But Autopilot users have explicitly opted out of being asked, so just do it.

This restriction does not apply to working with images and other intermediary build steps — check your work there as often as needed regardless of involvement level.

### The verification loop

After building slides, run this loop:

1. **Screenshot all slides.** Render every slide as a PNG and visually inspect each one.
2. **List every issue.** Write down every problem you find — overlapping elements, text overflow, spacing inconsistencies, contrast failures, alignment errors. Do not fix as you go. Catalogue first.
3. **Fix all issues.** Address each problem from the list. Use `set-position` for spacing, `set-font` for sizing and color, `set-text` for content, `delete-shape` to remove elements that don't work.
4. **Re-screenshot affected slides.** Only the ones you changed.
5. **Inspect again.** Fixes can introduce new problems (repositioning one element may crowd another). If you find new issues, return to step 2.
6. **Repeat until a full pass reveals nothing.** A clean pass means every slide was inspected and no issues were found. One pass is not enough if the first pass found problems — the fixes themselves need verification.

This loop is not optional. Skipping it produces output that looks plausible at a glance but falls apart under inspection — overlapping text, orphaned shapes, inconsistent margins. The user sees these immediately. You must catch them first.

### Reading screenshots

When verifying slides via screenshots, prefer delegating image reading to lightweight sub-agents — one per image, run in parallel (not backgrounded). Each sub-agent receives only two things: the image path to read, and a description prompt. It must not read any other files or take any other actions.

Prompt each sub-agent with: "Read the image at [path] and describe what you see in detail — layout, text content, element positioning, spacing, colors, fonts, images, and any visual artifacts or oddities." Nothing more. Do not tell it what the image is supposed to contain or omit.

Compare the returned descriptions against your intent. Only read an image yourself if a description reveals a discrepancy and you need to confirm before deciding on a fix.

This requires a harness that supports spawning sub-agents (e.g., Claude Code's Task tool with a lightweight model like Haiku). If your harness does not support this, read images directly but be aware of the context cost — batch verification of large image sets may not be practical.

### What to look for

Run this checklist against every slide during visual inspection:

**Overlap and collision**
- Text overlapping other text
- Text running through or behind shapes
- Stacked elements that should be side by side
- Images covering text or vice versa

**Spacing and margins**
- Any element within 0.5" of a slide edge
- Gaps between elements smaller than 0.3"
- Uneven spacing — large gap in one area, cramped in another
- Elements nearly touching (< 0.3" apart)

**Text problems**
- Text cut off at the edge of its bounding box
- Excessive line wrapping from a text box that is too narrow
- Leftover placeholder text from templates ("Click to add title")
- Text overflow — content that doesn't fit in the allocated space

**Alignment**
- Columns or rows of similar elements not aligned consistently
- Titles at different vertical positions across slides
- Content areas that shift position from slide to slide without reason

**Contrast and readability**
- Light text on a light background (or dark on dark)
- Small text (< 12pt) in a color that doesn't stand out
- Low-contrast icons blending into their background

**Design consistency**
- Font size or family changing between slides without reason
- Color usage inconsistent with the established palette
- One slide styled, adjacent slides left plain
- Layout pattern repeated on consecutive slides (monotony)

### Common mistakes

These are the most common defects encountered. Check for them explicitly.

| Mistake | What went wrong | Fix |
|---------|----------------|-----|
| Overlapping elements | Positioned shapes without accounting for their combined footprint | Recalculate positions; ensure bounding boxes don't intersect with < 0.3" clearance |
| Text overflow | Too much text in a shape, or shape too small | Reduce text, increase shape height, or split across shapes |
| Inconsistent margins | Positioned elements by eyeballing rather than using the grid | Snap to the 0.5" margin boundary; use consistent x/y coordinates across slides |
| Missed placeholder text | Content added but not all template placeholders replaced | Peek all slides and search for default placeholder strings |
| Styling applied to one slide only | Style applied to the current slide but not propagated | After establishing a style, apply it to every slide systematically |
| Elements touching slide edges | Positioned at x=0 or y=0 without accounting for margins | Minimum 0.5" from all edges |
| Large text wrapping | Text box slightly too narrow for oversized text (title slides, section dividers, stat callouts) — one word wraps to a second line | For text intended to be on a single line, make the text box 15-20% wider than the text needs; verify with a screenshot, since large font sizes are unforgiving of small shortfalls |

---

## Analyzing existing presentations

When given an existing deck to understand, replicate, or modify, follow this sequence before making any changes.

### Structural analysis

Start with the deck's internal structure — how many slides, what layouts and masters exist, what media is embedded.

Use `internals analyze` for this. It produces a full inventory: slide count, layout names mapped to their masters, embedded media files, and relationships between components. This tells you what the deck is built from.

### Shape-level fingerprinting

Next, understand the spatial layout of each slide — what shapes exist, where they are, how large they are, what colors they use.

Use `internals fingerprint` for this. It reports each shape's position (x, y), size (w, h), type, and fill color. This is how you reverse-engineer a layout pattern: not by guessing from a screenshot, but by reading the exact coordinates.

For a single slide: `internals fingerprint deck.pptx --slide 3`

### Content overview

Read the actual text content with `peek --all`. This gives a compact summary of every slide's text shapes — titles, body text, labels. Combined with the fingerprint, you can map content to positions.

For detailed shape-level data including IDs: `dump deck.pptx <slide_number>`

### Visual overview

Screenshot all slides for a visual reference. This is what the human sees, and it catches things the structural data doesn't — how fonts actually render, whether images look right, the overall visual impression.

### Sequence matters

Run these in order: structure first (understand what the deck is built from), then fingerprint (understand the spatial layout), then content (understand what it says), then screenshots (understand what it looks like). Each layer adds context that helps interpret the next.

Do not jump straight to screenshots. A screenshot tells you what a slide looks like but not how it is constructed. If you need to replicate or modify the deck, you need the construction details — shape IDs, exact positions, layout assignments — not just the visual result.
