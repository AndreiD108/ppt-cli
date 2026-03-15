# Technical Direction

Structured, dense, and functional. A technical presentation succeeds when the audience leaves understanding a system, a process, or an architecture they didn't understand before. The design serves comprehension — every choice should make complex information easier to parse, not prettier to look at. If the audience notices the design, something went wrong. If the audience follows the logic effortlessly, everything went right.

This direction suits architecture reviews, engineering presentations, developer talks, system documentation, RFC walkthroughs, technical postmortems, and infrastructure overviews. The audience is typically technical — they expect density, tolerate complexity, and respect precision. They will notice structural clarity and be annoyed by decoration that doesn't carry information.

---

## Palette character

Technical palettes are cool, muted, and high-contrast where it counts. The dominant tone is dark or neutral — charcoal, slate, deep navy, dark gray. The supporting tone is a desaturated complement — cool gray, muted blue-gray, off-white. The accent is sharp and singular — a bright teal, electric blue, amber, or green that appears only on the elements the audience must notice (key labels, highlighted components, active states in diagrams).

Avoid pastels. Avoid multiple accent colors — one is enough, and adding a second dilutes the signal. The palette should feel like a well-designed terminal theme or IDE color scheme: restrained background, clear foreground, one color that means "pay attention here." Cool tones are the most common choice, but warm palettes also work when they are muted and dark-leaning — think Gruvbox or warm Solarized, not coral and sunshine. The requirement is high contrast and control, not a specific temperature.

Example palettes that illustrate the range. Each includes the full set of colors needed to build slides — background, card/container fill, heading text, body text, muted captions, and accent. Any of these can be used as-is if the user agrees with the direction, or adapted as a starting point.

**Gruvbox** — Warm, developer-native, cozy. Proves that technical doesn't have to mean cold.

| Role | Color | Hex |
|------|-------|-----|
| Primary (background) | dark brown | `#282828` |
| Secondary (cards) | warm gray | `#3C3836` |
| Text (headings, values) | cream | `#EBDBB2` |
| Body | muted tan | `#A89984` |
| Muted (captions, comments) | gray-brown | `#928374` |
| Accent | burnt orange | `#D65D0E` |

**Darcula** — The JetBrains dark theme. Familiar to any Java/Kotlin/Python developer. Warm amber accent.

| Role | Color | Hex |
|------|-------|-----|
| Primary (background) | charcoal | `#2B2B2B` |
| Secondary (cards) | dark gray | `#3C3F41` |
| Text (headings, values) | cool blue-gray | `#A9B7C6` |
| Body | light gray | `#9A9A9A` |
| Muted (captions) | dim gray | `#6A737D` |
| Accent | amber | `#CC7832` |

**GitHub Dark** — The GitHub code view. Clean, modern, universally recognizable in developer contexts.

| Role | Color | Hex |
|------|-------|-----|
| Primary (background) | near-black | `#0D1117` |
| Secondary (cards) | dark gray | `#161B22` |
| Text (headings, values) | light gray | `#C9D1D9` |
| Body (descriptions) | medium gray | `#8B949E` |
| Muted (captions) | dim gray | `#6D7681` |
| Accent | sky blue | `#58A6FF` |

**Solarized Dark** — Ethan Schoonover's classic. Muted, high-contrast, distinctive teal-cyan base.

| Role | Color | Hex |
|------|-------|-----|
| Primary (background) | dark teal | `#002B36` |
| Secondary (cards) | deep teal | `#073642` |
| Text (headings, values) | pale gray | `#93A1A1` |
| Body | blue-gray | `#7E919A` |
| Muted (captions) | dim teal | `#586E75` |
| Accent | gold | `#B58900` |

**Solarized Light** — The warm variant. Cream backgrounds, same accent family. Good for decks that will be printed or projected in bright rooms.

| Role | Color | Hex |
|------|-------|-----|
| Primary (background) | cream | `#FDF6E3` |
| Secondary (cards) | warm off-white | `#EEE8D5` |
| Text (headings, values) | dark teal | `#073642` |
| Body | slate | `#586E75` |
| Muted (captions) | gray-teal | `#6B7B80` |
| Accent | warm amber | `#B8863A` |

**JetBrains Light** — Clean, bright, professional. A light theme that still reads as technical because of the blue accent and crisp contrast.

| Role | Color | Hex |
|------|-------|-----|
| Primary (background) | white | `#FFFFFF` |
| Secondary (cards) | cool off-white | `#F7F8FA` |
| Text (headings, values) | near-black | `#2B2B2B` |
| Body | dark gray | `#555555` |
| Muted (captions) | medium gray | `#656565` |
| Accent | blue | `#3574F0` |

These are examples of the kind of palette to build, not a fixed menu. Match the palette to the specific subject — a security review might lean toward Solarized Dark or GitHub Dark; a developer onboarding deck might use JetBrains Light or Solarized Light; an infrastructure deep-dive might use Gruvbox or Darcula for the warm, focused feel.

---

## Typography

The header font should signal "technical" without being gimmicky. Monospace fonts work well for headers — they immediately set the tone and feel natural to a technical audience. For body text, use a clean sans-serif that reads well at 14-16pt.

Font pairings that fit this direction:

| Header | Body | Character |
|--------|------|-----------|
| Consolas | Calibri | Developer-native, clean |
| Calibri | Calibri Light | Modern technical, understated |
| Arial Black | Calibri | Structural, bold headers |

Monospace for headers is the signature typographic move of this direction. Default to it. When the subject is technical but the audience includes non-engineers (a CTO presenting to the board about infrastructure), fall back to a strong sans-serif header with monospace reserved for inline code references.

### Size adjustments

Technical slides tend to carry more information per slide than other directions. This is acceptable — the audience expects density. But density without hierarchy is chaos. Maintain the universal size hierarchy strictly. If anything, increase the contrast: push titles to 40-44pt to create a stronger anchor against the denser body content. This is higher than the business direction's 36-40pt range — the extra size is needed here because the body content is denser, and the title needs to compete harder for the eye.

Stat callouts in this direction tend to be smaller than in business decks — 48-60pt rather than the universal 60-72pt range. This is the one direction where going below the universal floor is appropriate, because technical stats almost always carry qualifiers: a latency number alongside a system name, a percentage alongside a time range, an error rate alongside a measurement window. Size them to dominate the slide visually while still leaving room for the qualifying information that makes the number meaningful.

---

## Background strategy

Dark backgrounds work throughout a technical deck. This is the one direction where committing to dark on every slide — not just title and conclusion — feels natural rather than heavy. A dark primary with light text mimics the terminal and IDE environments the audience lives in. It also makes accent-colored elements (highlighted diagram nodes, key labels) pop more sharply.

If the audience includes non-technical stakeholders, or if the deck will be printed, use the sandwich approach instead: dark title, conclusion, and section dividers, with light content slides. This is more conventional but still reads as technical when the typography and palette are right.

Either way, be consistent. Do not mix dark and light content slides without a structural reason.

---

## Layout preferences

Technical presentations lean heavily on a subset of the universal layout vocabulary:

**Numbered step sequences.** The dominant layout for technical content. Each step is a distinct visual block — a number, a bold label, and a short explanation. The audience sees the sequence and understands the flow. Use this for deployment processes, migration plans, incident response procedures, build pipelines — anything with a defined order.

**Comparison columns.** Before/after states, option A vs. option B, current vs. proposed architecture. Two or three columns with consistent internal structure. Essential for RFCs and design proposals where the audience needs to weigh alternatives.

**Two-column (text + diagram).** The workhorse layout. Explanatory text on one side, a diagram, screenshot, or code snippet on the other. The text provides narrative; the visual provides structure. Use this more than any other layout.

**Grid (2x2).** Good for component overviews — four services, four system properties, four deployment stages. Each cell has a label and a short description. Keep the grid small (2x2 or 2x3); larger grids become tables and should be treated as such.

**Stat callout.** Useful for performance metrics, SLA numbers, cost comparisons. In a technical deck, stat callouts often carry units and qualifiers ("99.97% uptime, trailing 90 days") that business decks omit. Leave room for these.

**Layouts to use sparingly or avoid:**

- Full-bleed background images — rarely appropriate; technical content needs the full slide for information, not atmosphere
- Quote slides — occasional use for a key design principle or constraint, but this is not a direction where quotes drive the narrative
- Icon + text rows — can work for feature/capability overviews, but technical audiences often prefer a more structured grid or comparison layout to icon rows

### Diagrams and flow visualizations

Technical decks depend on diagrams more than any other direction. ppt-cli does not have a native diagramming tool, but you can build simple diagrams from positioned shapes:

- Use textboxes as labeled nodes (component names, service names)
- Use filled rectangles as containers (grouping related components)
- Use accent-colored fills to highlight the component under discussion
- Lay out flows left-to-right or top-to-bottom; avoid diagonal arrangements

The decision to build from shapes or generate as an image depends on more than node count. Simple flows (3-6 nodes) with labeled boxes and straight connections are worth building from shapes for editability. But even a 4-node diagram is better generated when it needs visual polish that flat rectangles cannot deliver — data flow direction indicators, component hierarchy with nesting, a highlighted active path through the system, or an isometric perspective. Anything beyond 6 nodes should almost always be a generated image. When generating, carry the direction's sharp-geometric motif into the prompt: hard-cornered boxes, straight connecting lines, no rounded or organic elements.

---

## Motif suggestions

Technical decks suit motifs rooted in structure and precision rather than decoration:

- **Sharp and geometric.** Hard-cornered containers, square image crops, rectangular accent bars. Nothing rounded — the visual language says "precise" and "engineered."
- **Minimal line work.** Thin borders on containers instead of fills, hairline dividers between sections, monospace labels. The design feels like a wireframe or blueprint.
- **Consistent container styling.** Every code block, every diagram node, every data container uses the same fill color, border treatment, and internal padding. The container itself becomes the motif.

For high-coverage anchoring, a thin accent-colored bar along the top or bottom edge of every slide works well. It's visually minimal (appropriate for the direction), appears on every slide regardless of content, and ties the deck together without consuming layout space.

---

## Content density

This direction tolerates more content per slide than any other. A technical audience expects density and will be frustrated if simple ideas are spread across multiple slides — it breaks the logical flow and forces them to hold context across page turns.

Guidelines for calibrating density:

- A concept that requires context to make sense should stay on one slide. If the explanation requires the diagram to be visible while reading the text, they must be on the same slide.
- When a slide feels too dense, split by *logical unit*, not by slide area. Two related concepts each get their own slide. One concept with supporting detail stays together.
- Body text can run to 6-8 lines per block in this direction (compared to 3-4 in creative or business). But each block should cover one point. Multiple points still get separate shapes.
- Use more slides for a long sequence (one step per slide for a 10-step process) but fewer slides for a single complex system (keep the architecture on one slide, even if it's dense).

---

## Image style

Technical decks use images functionally, not atmospherically. The main image types:

**Diagrams and architecture visuals.** Generated or hand-built. When using AI generation, prompt for clarity over beauty — and wire the deck's palette directly into the prompt rather than using generic color descriptors. If the deck uses GitHub Dark, prompt with its hex values: `"a system architecture diagram showing three microservices connected to a message queue and a database, flat vector, #0D1117 background, #161B22 container fills, #C9D1D9 label text, #58A6FF for the highlighted service, hard-cornered rectangular boxes, clean sans-serif labels"`. The palette tables earlier in this file give you the exact hex values to use. Isometric 3D renders also work well for infrastructure and architecture concepts. Use `--resolution 2k` for any diagram with text labels — technical diagrams are label-heavy and legibility degrades at lower resolutions. Use `--reasoning` when the diagram has many components or specific spatial relationships that the model needs to plan.

**Screenshots and UI mockups.** Real screenshots of systems, dashboards, or code. Place them in styled containers (a filled rectangle slightly larger than the image) to integrate them with the slide design. When a deck includes screenshots from multiple tools (Grafana, AWS Console, a terminal, an internal dashboard), they will have wildly different visual treatments — color-grade them to the deck's palette using image processing (pass as `--ref` and prompt with a tint or duotone conversion) for stronger cohesion than styled containers alone can provide.

**Charts and data visualizations.** Performance benchmarks, latency distributions, throughput comparisons, error rate trends, capacity projections — technical decks are data-heavy, and AI-generated chart images are often a better option than building charts from shapes or inserting generic Excel exports. Prompt with the data, chart type, palette hex values, and style: `"horizontal bar chart comparing p50, p95, and p99 latency across five services, #0D1117 background, #58A6FF bars with the highest-latency service in #D29922, #C9D1D9 labels, clean sans-serif font, minimal grid lines, Edward Tufte style — maximum data-ink ratio, no chartjunk"`. Include actual numbers and labels in the prompt. Use `--resolution 2k` for any chart with text.

**Abstract technical backgrounds.** For title and section divider slides only. Geometric patterns, network visualizations, circuit-board textures. Keep them low-contrast so they don't compete with overlaid text. Prompt style: `"abstract geometric network of connected nodes, dark navy background with faint luminous cyan lines, minimal, out of focus"`. For title and section divider slides, short text (1-3 words) can be rendered directly into the generated background image in a monospace or technical typeface rather than overlaid as a separate shape — the text becomes part of the visual composition. This works when the title is brief and final; for longer or editable text, overlay shapes remain the better choice.

Avoid: stock photography of people, lifestyle imagery, metaphor illustrations (seedlings, handshakes, lightbulbs). These read as filler in a technical context. If a slide needs a visual element and the content is abstract, use a geometric shape or accent fill rather than a decorative image.

---

## Direction-specific anti-patterns

| Anti-pattern | Why it fails here | What to do instead |
|---|---|---|
| Full-bleed lifestyle photography | Technical audiences read it as padding; it displaces space needed for content | Use diagrams, screenshots, or abstract geometric backgrounds for visual interest |
| Rounded, soft visual motifs | Conflicts with the precision and structure this audience expects | Use sharp corners, straight lines, rectangular containers |
| Low information density (one idea per slide) | Breaks logical flow; forces the audience to hold context across slides | Keep related concepts together; split by logical unit, not by slide area |
| Multiple accent colors | Dilutes the signal; in diagrams and highlighted elements, one accent color means one thing | Commit to one accent; use value (lightness) variations of the primary for secondary distinctions |
| Decorative icons without information value | Technical audiences parse icons as meaningful symbols; purely decorative ones create confusion | Use shapes and accent fills for visual interest; reserve icons for when they carry meaning |
| Large empty areas on content slides | Reads as "nothing to say" rather than "breathing room" in a density-tolerant context | Fill the space with supporting context, or reduce the slide dimensions to match the content |
| Bright, saturated warm accents | Coral, hot pink, sunny yellow as primaries feel energetic and informal, not precise | Warm palettes work if muted and dark-leaning (Gruvbox-style); the key is desaturation and contrast, not temperature |

---

## Non-obvious command patterns

A few ppt-cli workflows that are particularly relevant to this direction and may not be immediately apparent from `--help`.

**Building a styled code/content container.** There is no native "code block" shape. Build one by creating an empty textbox sized as the container, filling it with a dark color, then placing the actual content textbox on top with a monospace font and light text color. The container shape should be slightly larger than the content shape on all sides to create padding.

**Diagram nodes from textboxes.** Create each node as a textbox with a short label, then use `set-fill` to give it a background color and `set-position` to place it precisely. Use empty textboxes (thin and wide, or thin and tall) as connecting lines between nodes — fill them with the accent color. This is more manual than a diagramming tool, but produces editable, styled nodes that match the deck's design system.

**Dark slide backgrounds.** ppt-cli does not have a "set slide background" command. Create a full-slide textbox (`--x 0in --y 0in --w <slide_width> --h <slide_height>`) with empty text, then fill it with the primary dark color. All subsequent shapes on that slide will layer on top of it. Add this background shape first, before any content shapes, so it sits behind everything.
