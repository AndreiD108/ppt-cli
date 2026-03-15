# Design Universals

Principles and rules that hold across all design directions. Every direction-specific file will assume you have internalized all of this. They are not optional defaults — they are the floor of competence.

---

## Color

### Content-informed palette

The palette should feel like it was chosen *for this specific presentation*. A deck about ocean conservation should not use the same colors as a quarterly sales review. If the colors could be swapped into a completely unrelated deck and still "work," the choice was not specific enough.

This does not mean literal color matching (blue for ocean, green for nature). It means the palette's personality — warm or cool, muted or saturated, dark or bright — should reflect the subject's emotional register. A deck about crisis response needs gravity; a deck about a product launch needs energy. The palette is the first signal the audience reads, before they process a single word.

### Dominance hierarchy

Never give all colors equal visual weight. One color dominates, one supports, one accents.

- **Primary (60-70%)**: Large areas — backgrounds, header bars, full-slide fills. This is the color the audience associates with the deck.
- **Secondary (20-30%)**: Supporting areas — content cards, section backgrounds, shapes that frame content. Provides contrast against the primary without competing with it.
- **Accent (5-10%)**: Sparingly applied to the things the audience must notice — key statistics, callout highlights, active states, important labels. If accent color appears on more than a few elements per slide, it stops being an accent.

This 60/20/10 split is a guideline, not a pixel-counting rule. The point is that one color clearly dominates and the accent is rare enough to draw the eye when it appears.

### Background strategy

Decide early whether the deck uses a uniform background approach (all dark, all light, all a single tone) or a contrast approach (dark for structural slides like title/conclusion/section dividers, light for content slides). Either works. What fails is no strategy — some slides dark, some light, with no pattern the audience can anticipate.

The choice of strategy is directional (a premium deck might go all-dark; a corporate report might use the contrast sandwich), but *having* a strategy is universal.

### Image palette coordination

When the deck uses AI-generated images, every image must coordinate with the deck's color palette. An image with colors that clash with or ignore the palette breaks visual cohesion regardless of how well the rest of the slide is designed.

This does not mean every image must use only palette colors — a photograph or illustration has its own natural color range. It means the dominant tones of the image should not fight the slide's palette. A warm coral-and-navy deck with a cold cyan-and-lime photograph on slide 7 looks like a collage, not a designed presentation.

When generating images, specify palette hex values for any color that must match (backgrounds, accent highlights, dominant tones). When working with user-provided images, consider re-processing them to align with the palette — duotone conversion, color grading, or tint overlays can unify disparate source images into a cohesive visual language. See `2-image-generation.md` for the mechanics.

---

## Typography

### Font pairing

Every deck needs two font choices: a header font and a body font. The header font carries personality — it signals whether the deck is formal, modern, playful, technical. The body font is invisible — it should be clean, readable, and stay out of the way.

Do not use the same font for both unless the design direction specifically calls for it (minimalist directions sometimes do). Do not default to Arial. The header font is one of the cheapest ways to make a deck look intentional rather than generated.

### Size hierarchy

Size contrast is what creates visual hierarchy. If the title is 20pt and the body is 16pt, the audience's eye has no anchor — everything looks equally important. Maintain clear separation between levels:

| Element | Size range | Weight |
|---------|-----------|--------|
| Slide title | 36-44pt | Bold |
| Section header (within a slide) | 20-24pt | Bold |
| Body text | 14-16pt | Regular |
| Captions and footnotes | 10-12pt | Regular, muted color |
| Large stat callouts | 60-72pt | Bold |

These ranges are not arbitrary. 36pt is the threshold where a title visually separates from 14-16pt body copy at projection distance. Below that, the hierarchy flattens. Stat callouts at 60-72pt are large enough to function as visual elements in their own right — they replace images on data-heavy slides.

### Bold everything structural

Bold all of these, always:
- Slide titles
- Section headers within a slide
- Inline labels at the start of a line ("Revenue:", "Status:", "Timeline:")

Never bold body paragraphs or descriptions. The purpose of bold is to create scannable anchors — the audience should be able to glance at a slide and pick out the structure from the detail in under two seconds. If everything is bold, nothing is.

---

## Layout

### Layout vocabulary

These are the named patterns available for composing slides. Think in terms of these patterns rather than placing shapes ad-hoc.

**Two-column.** Text on one side, image or supporting content on the other. The most versatile general-purpose layout. Works for explanations, case studies, feature descriptions.

**Icon + text rows.** A vertical stack of items, each with a small icon (or colored circle) on the left and a bold label + description on the right. Works for feature lists, benefit summaries, process overviews.

**Grid (2x2 or 2x3).** Content blocks arranged in a grid. Each cell has a consistent internal structure (icon, title, short text). Works for comparisons, feature matrices, team introductions.

**Half-bleed image.** An image fills exactly one half of the slide (left or right, top or bottom). Content occupies the other half. Works for case studies, testimonials with photos, visual storytelling.

**Full-bleed background image.** An image fills the entire slide. Text is overlaid, usually with a semi-transparent color bar or positioned in negative space within the image. Works for title slides, section dividers, emotional impact slides.

**Stat callout.** A very large number (60-72pt) with a small label below it. Sometimes two or three stats side by side. Works for metrics, KPIs, before/after comparisons.

**Comparison columns.** Two or three columns, each representing an option, tier, or time period. Consistent internal structure across columns. Works for pricing, pros/cons, before/after, competitive analysis.

**Timeline or process flow.** Numbered or sequential steps arranged horizontally or vertically, with connecting visual elements. Works for roadmaps, implementation plans, historical narratives.

**Quote or callout.** A single statement, large and centered, often in italic or a distinctive font. Optional attribution below. Works for testimonials, key takeaways, provocative questions.

**Section divider.** A slide that introduces a new section of the deck. Usually minimal — a title, maybe a subtitle or section number, often with a distinctive background treatment. Works for any deck longer than 6-7 slides to give the audience structural cues.

### Content-type to layout mapping

When deciding which layout to use, start from the content, not from variety for its own sake.

- Key points or benefits → icon + text rows, or bullet layout
- Team or people → grid with images, or multi-column
- Testimonials or quotes → quote slide
- Metrics or KPIs → stat callout, or comparison columns
- Processes or timelines → timeline or numbered steps
- Case studies → two-column (image + text) or half-bleed
- Detailed data → table (but consider if stat callouts or comparison columns would communicate better)

### Layout variation

Never repeat the same layout pattern on consecutive slides. Two stat callout slides in a row, or three two-column slides in a row, creates visual monotony even if the content is different. Actively rotate through patterns.

This does not mean every slide should look wildly different — the deck still needs to feel cohesive. It means the structural skeleton of each slide should vary enough that the audience perceives progression, not repetition.

### Visual motif

A motif is not a single element you stamp onto every slide. It is a visual principle — a consistent design language that manifests differently depending on what each slide contains. The principle is singular; the elements it produces vary by context.

For example, if the principle is "soft edges," it shows up as rounded image frames on slides with images, rounded containers around text blocks on content slides, rounded accent shapes on data slides. No single element needs to appear on every slide, but the principle does — and the audience perceives cohesion because every decorative choice shares the same visual DNA.

Examples of visual principles and how they manifest:

- **Soft and rounded.** Rounded image frames, rounded background boxes behind titles, rounded containers for bullet groups, pill-shaped accent elements.
- **Sharp and geometric.** Angular accent bars, square image crops, rectangular content cards with hard corners, diagonal stripe elements.
- **Minimal line work.** Thin border outlines instead of filled shapes, hairline dividers, icons in a line-art style rather than solid fills.
- **Bold blocks of color.** Large filled rectangles as section backgrounds, solid color cards, thick accent bars, images inside colored frames.

The elements that express a motif vary in how much of the deck they naturally cover. Some are **high-coverage** — they appear on nearly every slide regardless of content: a small logo in a consistent corner, a colored sidebar, a subtle background texture, a decorative element near titles. Others are **content-dependent** — they only appear when their content type is present: rounded image frames show up on slides with images, icon circles show up on list slides, styled table containers show up on data slides.

A deck built only on content-dependent elements will have gaps — slides where nothing expresses the motif because the right content type isn't there. The strongest approach is to anchor the motif with at least one high-coverage element that appears everywhere, then let content-dependent elements reinforce the same visual principle when their content type is present.

When the deck uses AI-generated images, they are content-dependent motif elements — they appear only on slides that call for imagery, but they must express the same visual principle as the rest of the motif. If the motif is "soft and rounded," images should use rounded crops or frames, soft lighting, and organic compositions. If the motif is "sharp and geometric," images should use square crops, hard lighting, and angular compositions.

The coherence mechanism is the shared style description. When generating a set of images for a deck, establish a style fragment — palette, rendering style, lighting, compositional approach — and include it in every image prompt. The images will feel like they belong to the same family because they share visual DNA, just as shapes across slides feel cohesive because they share the same motif principle. See `2-image-generation.md` for prompt structure and consistency techniques.

A deck with varied layouts but no visual motif feels like a collection of unrelated slides. A deck with a consistent visual language feels designed, even if the audience couldn't articulate why. The motif is what makes "varied" feel "cohesive" rather than "random."

---

## Spacing

### Margins

Maintain at least 0.5 inches of clear space between content and all four slide edges. Content that touches or approaches the edge looks cramped, and on some displays or projectors the edges may be clipped.

On a standard 10" x 7.5" slide, this means the usable content area is 9" wide (0.5" to 9.5") and 6.5" tall (0.5" to 7.0"). Plan layouts within this box.

### Inter-element gaps

Choose a consistent gap size — 0.3" or 0.5" — and use it between all content blocks throughout the entire deck. Mixing gap sizes (0.2" here, 0.6" there) makes the layout look unintentional.

The gap size itself matters less than its consistency. Smaller gaps (0.3") feel tighter and more information-dense. Larger gaps (0.5") feel more spacious and premium. Match the gap to the deck's density and tone.

### Whitespace

Empty space on a slide is not wasted space. It is what makes the content that *is* there readable. A slide with every inch filled communicates "I couldn't decide what to cut." A slide with breathing room communicates "this is what matters."

When a slide feels cramped, the fix is almost never to make elements smaller. The fix is to move content to a second slide or cut content that doesn't earn its place.

---

## Content structure

### Every slide needs a visual element

A slide with only text — no image, no shape, no table, no colored element — is forgettable. The audience's eye needs something to anchor to beyond words.

This does not mean every slide needs a photograph or a generated image. A colored accent bar, a filled rectangle behind a stat, an icon, a simple shape that echoes the visual motif — any of these qualify. The bar is low. The failure mode is not meeting it at all.

When AI image generation is available for the deck, images become one more option in this toolkit — not a replacement for simpler visual elements. A stat callout slide is better served by a bold number and an accent shape than by a generated background image. A section divider might benefit from a striking generated visual, or it might be stronger as a single bold word on a colored field. The availability of image generation does not change the principle: choose the visual element that serves the content, not the most elaborate one available.

### Text alignment

Left-align body text, lists, and descriptions. Always.

Center-align only: slide titles, short callout text (one line), stat numbers, and quote text. Never center a paragraph, a multi-line description, or a bulleted list. Centered body text is harder to read because the eye has to find a new starting position on every line.

### Separate items into distinct shapes

When a slide has multiple items — steps in a process, features in a list, team members, metrics — each item should be its own text shape (or group of shapes). Never concatenate them into a single text block with newlines between them.

Separate shapes give you independent positioning, sizing, and styling control. A single block with embedded newlines is fragile — changing one item can reflow everything below it, and you cannot style or position individual items differently.

This is one of the most important ppt-cli-specific patterns. The tool creates shapes cheaply. Use that.

### Tables as a last resort

Before creating a table, ask whether the data would communicate better as:
- Stat callouts (for a few key numbers)
- Comparison columns (for side-by-side options)
- Icon + text rows (for qualitative comparisons)
- A generated chart image (for complex data visualizations where building from shapes would be brittle — bar charts, trend lines, pie charts rendered as a polished visual artifact; requires AI image generation)

Tables are appropriate when the data is genuinely tabular — multiple rows and columns where the reader needs to cross-reference. For 2-4 data points, a visual layout almost always communicates faster than a grid of cells.

---

## Visual accents

### No accent lines under titles

A thin colored line directly beneath a slide title is the single most common hallmark of generic, template-driven slides. It adds no information, wastes vertical space, and signals "no design thought went into this." Use whitespace or background color contrast to separate the title from the content below it.

### Icon contrast

When using small icons or visual markers, ensure they have sufficient contrast against their background. If an icon is similar in value (lightness) to the background, it disappears. Two fixes: place icons inside filled circles of a contrasting color, or choose icon colors with strong value contrast against the slide background.

### Emphasis through contrast, not effects

When one element in a composition needs to stand out — a key bar in a chart, a highlighted step in a process, a featured item in a grid — reach for contrast before reaching for effects. A shape in the accent color surrounded by shapes in muted tones draws the eye without any glow, shadow, or filter applied. Higher saturation against desaturated neighbors, a warmer hue against cool ones, or a bolder weight against lighter ones — these are reliable, clean emphasis techniques.

Avoid glow effects. A generic outer glow on a shape or element looks like an amateur filter, not an intentional design choice. If a subtle luminous quality is genuinely what the design calls for, be specific — a thin rim highlight, a faint warm tint, a slight increase in brightness — rather than applying a blunt glow. The same principle applies to generated images: when prompting for emphasis on an element within an image, specify the visual treatment precisely rather than asking for generic "glowing."

---

## Common design mistakes

These are the failure modes that recur most often. They are listed here as a checklist to run against finished slides.

| Mistake | What to do instead |
|---------|-------------------|
| Same layout repeated on consecutive slides | Rotate through layout patterns; consecutive slides should have visibly different structures |
| Body text centered | Left-align all body text, lists, and descriptions |
| Text-only slides with no visual element | Add at least one non-text element — image, shape, accent bar, icon |
| One slide styled, the rest left plain | Commit to the design system across every slide, no exceptions |
| Content touching or within 0.5" of slide edges | Reposition within the safe content area |
| Inconsistent gaps between content blocks | Pick 0.3" or 0.5" and apply uniformly |
| Title not visually distinct from body text | Title must be 36pt+ and bold; body is 14-16pt regular |
| All colors given equal visual weight | One color dominates (60-70%), accent is rare (5-10%) |
| Multiple items concatenated in one text block | Split into separate shapes, one per item |
| Accent line directly under a title | Remove it; use whitespace or background contrast instead |
| Low-contrast icons blending into background | Place on contrasting circles or use high-contrast colors |
| Generic color palette unrelated to topic | Choose colors that reflect the subject's emotional register |
| Inconsistent image styles across slides | When using generated images, establish a shared style description and apply it to every image prompt |
