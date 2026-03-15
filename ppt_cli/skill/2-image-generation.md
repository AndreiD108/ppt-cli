# Image Generation

How to generate, edit, and process images for presentations using ppt-cli's AI image generation. Read this file when you identify a need to generate or manipulate images as part of a presentation — before writing any image generation prompts.

The design direction files (business, technical, creative, educational) each have an "Image style" section that describes what kind of imagery fits that direction's aesthetic. This file does not repeat that guidance. It covers the mechanics of image generation, the full range of what the model can do, and the practical workflow for producing high-quality results.

---

## What this model can do

The image generation model (Gemini 3.1 Flash) is far more capable than you might expect. Recalibrate your assumptions:

**Text rendering works.** The model produces legible, correctly spelled text in images — headlines, labels, captions, poster typography. It handles font style, size, and placement instructions. The exception is very small text (fine print, dense labels on complex charts) where error rates rise enough to not be worth attempting. Anything readable at presentation viewing distance is fair game.

**Complex compositions work.** The model follows multi-dimensional prompts accurately — subject, lighting, camera angle, composition, mood, spatial relationships, all specified together. It understands visual hierarchy, foreground/background separation, negative space, and depth of field.

**Genre rendering works.** Any established visual genre — editorial photography, manga, comic book, watercolor, oil painting, isometric 3D, flat vector, retro game art, cinematic film still, fashion editorial — the model can produce it convincingly. These are not novelty tricks; they are tools for communicating different things.

**Charts and data visualizations work.** The model produces clean, well-designed graphs, bar charts, pie charts, timelines, process diagrams, and infographics directly as images. At 2k resolution with reasonably sized text, the results are production-quality. This is a strong option for complex visualizations where building charts from shapes would be brittle or ugly.

**Structured visuals work.** Diagrams, flowcharts, process illustrations, comparison layouts, infographic-style compositions — the model handles spatial organization and visual hierarchy natively. It understands how to lay out information visually.

**Image editing works.** The model can take an existing image as input and modify it: change lighting, replace backgrounds, remove objects, apply color grading, add effects, transfer styles. This is not a separate tool — it is the same generation model with an input image.

**Subject consistency works.** When using reference images, the model maintains character resemblance (facial structure, clothing, proportions) and object fidelity across multiple generations. This means you can produce a set of images for a deck where the same person, product, or environment appears consistently across slides.

### The complexity ceiling

There is a practical limit to how many concrete, positional instructions the model can follow in a single prompt. Specifying the exact placement, size, and relationship of 5-8 specific objects works reliably. Pushing to 15-20+ specific items with precise spatial relationships ("the red circle is 3px left of the label, the arrow points from box A to box B, the title sits directly under the logo") will start producing unreliable results.

This ceiling applies to concrete spatial instructions — specific objects with specific positions. It does not apply to style, mood, lighting, color grading, and compositional direction, which stack without degradation. You can write a richly detailed style description with a simpler subject specification and get excellent results.

When the composition is too complex for a single prompt, break it into layers: generate a background, generate foreground elements separately, and compose them in the slide using positioning.

---

## Prompt structure

A prompt built from isolated keywords produces generic, unfocused results. Structure your prompts as narrative sentences covering five dimensions:

**Subject** — what is in the image. Be specific about materials, textures, colors, and details. "A weathered oak desk with visible wood grain" produces a better result than "a desk." Specificity is the single highest-leverage improvement you can make.

**Action or state** — what the subject is doing or how it is arranged. "A woman presenting to a boardroom" vs. "a woman" gives the model compositional intent.

**Setting** — where the scene takes place. "A modern glass-walled conference room at golden hour" anchors the image in a real environment with implied lighting.

**Composition** — how the shot is framed. Camera angle, distance, framing, and where the subject sits in the frame. This is where you control negative space for text overlay: "wide shot, subject positioned in the left third, negative space on the right for text."

**Style** — the visual look and feel. Photography genre, illustration style, color grading, film stock. This is the emotional register of the image.

Not every prompt needs all five — an icon prompt might only need subject and style. But when generating hero visuals, editorial images, or complex scenes, covering all five produces dramatically better results than leaving dimensions unspecified.

When a color in the image must exactly match the presentation's theme — backgrounds that need to blend with the slide, accent colors that must be consistent across assets — specify hex values from the theme: `"deep navy #1A1A2E background"`, `"accent highlights in #E94560"`. For colors that don't need to match precisely, natural language (`"warm coral"`, `"muted teal"`) is fine and gives the model more creative latitude.

### Example

```
A confident engineer presenting an architecture diagram on a large screen,
modern tech office with floor-to-ceiling windows, medium shot from a slight
low angle, shallow depth of field, editorial photography with cinematic
teal-and-orange color grading
```

Each dimension is doing work: the subject is specific (engineer, not "person"), the action provides compositional structure, the setting implies lighting and mood, the composition controls framing and perspective, and the style sets the visual register.

---

## Style vocabulary

Style modifiers go at the end of the prompt and shape the visual output. The categories below are a starting point — the model understands FAR more than what is listed here. You should "invent" modifiers that match the presentation's mood and direction.

### Photography

- `editorial photography, cinematic color grading` — magazine-quality, moody
- `corporate photography, clean lighting` — professional, neutral
- `fashion magazine style editorial` — bold, stylized
- `photojournalistic style` — documentary, candid
- `high-end product photography` — studio, controlled

### Illustration

- `flat vector illustration, minimal palette` — clean, diagrammatic
- `isometric 3D render` — spatial, architectural
- `high-fidelity 3D render` — realistic objects, environments
- `watercolor painting style` — soft, artistic
- `pencil sketch on white paper` — conceptual, in-progress feel

### Film and color

- `cinematic color grading with muted teal tones` — modern, moody
- `shot on medium-format analog film, pronounced grain` — editorial texture
- `Fujifilm color science` — natural, slightly warm
- `desaturated, high contrast black and white` — dramatic emphasis
- `as if shot on 1980s color film, slightly grainy` — nostalgic warmth

### Lighting

- `three-point softbox studio lighting` — even, professional
- `golden hour backlighting creating long shadows` — warm, cinematic
- `Chiaroscuro lighting with harsh, high contrast` — dramatic
- `overcast diffused daylight` — neutral, documentary
- `neon-lit lighting in pink and blue` — futuristic, tech

### Camera and lens

- `shallow depth of field (f/1.8)` — blurred background, subject pops
- `wide-angle lens` — vast scale, landscapes, architecture
- `50mm lens` — natural human-eye perspective
- `macro lens` — extreme close-up detail
- `low-angle shot` — subject appears powerful, imposing
- `bird's eye view` — overview, maps, layouts
- `tilt-shift miniature effect` — makes real scenes look like models

These modifiers combine freely. `editorial photography, golden hour backlighting, shallow depth of field, Fujifilm color science` is a valid, effective combination. The model resolves the combined intent into a coherent image.

### Brand aesthetics as style anchors

You may also use recognizable brand aesthetics as style anchors. Referencing a known brand's visual identity ("Notion or Stripe illustration aesthetic") compresses an entire design system (proportions, color relationships, level of abstraction, whitespace philosophy) into a few words the model already understands.

  Clean tech/SaaS illustration
  - Stripe — polished gradients, geometric precision, premium feel
  - Notion — hand-drawn-feeling, minimal, warm, approachable
  - Linear — ultra-minimal, monochrome, precise, developer-oriented
  - Figma — colorful but structured, playful geometry
  - Slack — rounded, friendly, bold colors, approachable characters
  - Mailchimp — quirky, hand-drawn, personality-forward
  - Spotify — bold duotones, gradient washes, energetic
  - Vercel — dark, sleek, subtle gradients, developer-premium
  - Shopify — green-tinted, approachable, commerce-oriented

  Data and editorial
  - Bloomberg — dark backgrounds, neon accents, data-dense, financial authority
  - The New York Times — conceptual editorial illustration, sophisticated metaphors
  - The New Yorker — distinctive illustrated covers, literary tone
  - Monocle — clean editorial photography, sophisticated restraint
  - The Economist — red/white, sharp, authoritative infographics
  - Wired — futuristic, high-contrast, tech-forward editorial

  Premium/minimal
  - Apple — whitespace, product-focused, precision photography
  - Muji — no-brand minimalism, natural materials, quietness
  - Aesop — botanical, typographic, apothecary warmth
  - Dieter Rams / Braun — functional, systematic, grid-based
  - Kinfolk — muted earth tones, quiet photography, lots of whitespace
  - IKEA — functional, democratic design, bright primary accents on clean backgrounds

  Playful/human
  - Headspace — soft, rounded, calming, warm palettes
  - Airbnb — warm lifestyle photography, human connection
  - Duolingo — bright, bold, cartoonish, high energy
  - Google / Material Design — clean, geometric, bold primary colors, structured motion
  - Lego — bright, blocky, constructive, joyful

The most useful ones for presentations are probably the first group — they're the visual language people already associate with "well-designed deck." But the others are powerful precisely because they're unexpected in a slide context. A Bloomberg-style data visualization or a New Yorker-style conceptual illustration on a slide would be distinctive.

### Named references as style anchors

The same principle applies beyond brands. Named artists, studios, directors, and movements compress entire visual systems into a few words.

  Anime & Manga
  - Studio Ghibli — soft painterly backgrounds, natural settings, emotional warmth
  - Makoto Shinkai — hyperrealistic skies, dramatic light shafts, vivid saturated color
  - Shonen (Dragon Ball, Naruto) — high energy, speed lines, impact frames, exaggerated action
  - Akira / Katsuhiro Otomo — detailed cyberpunk, mechanical precision, dystopian scale
  - Junji Ito — intricate linework, unsettling compositions, horror

  Comics & Graphic Novels
  - Moebius / Jean Giraud — dreamlike, detailed, European sci-fi, vast landscapes
  - Mike Mignola (Hellboy) — heavy black shadows, minimal detail, gothic
  - Frank Miller (Sin City) — extreme high-contrast black and white, noir
  - Hergé (Tintin) — ligne claire, clean outlines, flat colors, precise
  - Jack Kirby — cosmic scale, crackling energy, bold geometric compositions

  Photography
  - Annie Leibovitz — dramatic editorial portraits, theatrical staging
  - Ansel Adams — monumental black and white landscapes, tonal range
  - Steve McCurry — vivid National Geographic, cultural portraiture, intense eyes
  - Andreas Gursky — massive scale, architectural repetition, almost abstract
  - Peter Lindbergh — raw black and white fashion, emotional, unretouched

  Illustration
  - Charley Harper — geometric, minimal, nature subjects reduced to shapes
  - Saul Bass — bold graphic design, movie poster aesthetic, strong silhouettes
  - Mary Blair — mid-century Disney, bold flat color, stylized shapes
  - Alphonse Mucha — Art Nouveau, decorative, flowing organic lines
  - Edward Gorey — pen and ink, gothic Victorian, darkly whimsical

  Film / Cinematic
  - Wes Anderson — symmetrical framing, pastel palettes, dollhouse precision
  - Ridley Scott — atmospheric, smoky, industrial, epic scale
  - Denis Villeneuve — vast minimalist landscapes, muted desaturated tones, monumental
  - Wong Kar-wai — neon-soaked, motion blur, saturated romantic melancholy
  - David Lynch — surreal, unsettling, dreamlike, high contrast

  Data Visualization & Infographics
  - Edward Tufte — maximum data-ink ratio, no chartjunk, precise and minimal
  - David McCandless (Information is Beautiful) — colorful, modern, accessible, pop
  - Isotype / Otto Neurath — pictographic statistics, simplified icons representing quantities

---

## Resolution, ratio, and budget

### Aspect ratio by layout

Match the aspect ratio to the slide layout the image will occupy:

| Layout | Ratio | Notes |
|--------|-------|-------|
| Full-bleed background | 16:9 | Fills the entire slide |
| Half-bleed (left/right) | 3:4 or 1:1 | Depends on how much of the slide the image fills |
| Half-bleed (top/bottom) | 16:9 | Wide strip |
| Icon or spot illustration | 1:1 | Square, sized small |
| Stat callout background | 16:9 | If used behind a stat |

Always set `--ratio` explicitly. The default may not match your slide dimensions, and the mismatch produces awkward cropping or stretching.

Supported ratios: `1:1`, `3:2`, `2:3`, `3:4`, `4:3`, `4:5`, `5:4`, `9:16`, `16:9`, `9:21`, `21:9`, `1:4`, `4:1`, `1:8`, `8:1`.

### Resolution by use

| Use | Resolution | Cost (approx.) |
|-----|-----------|------|
| Hero images, full-bleed, half-bleed | 2k | $0.10 |
| Medium inline images, diagrams | 1k | $0.067 |
| Icons, thumbnails, drafts | 512 | $0.045 |

For creative decks, use 2k for any visible image — pixel density matters at that visual fidelity level. For business and educational decks, 1k is acceptable for most inline images. Use 512 for icons and for draft iterations during the editing workflow.

### Budget planning

Before generating images, estimate the total cost and confirm with the user. A 20-slide deck with 10 images at 2k resolution costs roughly $1. A deck with 20 images including multiple iterations and variations could reach $3-5. These are modest amounts, but the user should know the expected spend before you begin.

Count: how many slides need images, at what resolution, and how many iterations you expect. Present the estimate as a range.

---

## Text rendering in images

The model renders text directly into images — useful for title slides with embedded typography, poster-style section dividers, stat callouts where the number is part of the visual composition, and mockup graphics.

### How to prompt for text

1. **Enclose the text in quotes** within the prompt: `the word "INNOVATE"`
2. **Specify the font style**: `bold white sans-serif font`, `thin minimalist font`, `heavy blocky Impact-style font`, `flowing elegant script`
3. **Specify placement**: `centered at the top`, `bottom-left corner`, `filling the center of the frame`
4. **Keep it short**: one to three words render most reliably. Full sentences work but error rates increase with length.
5. **Adapt, be creative**: the specific examples above are just that, examples, you should use whatever specifics are fitting for your presentation.

### When to use text-in-image vs. text shapes

**Text-in-image** when: the text is part of the visual composition — a title rendered into a dramatic background image, a word used as a visual element, a label integrated into a diagram or chart. The text and the image are one artistic unit.

**Text shapes overlaid on the image** when: the text needs to be editable, the content might change, or the text is functional (body copy, descriptions, speaker notes references). Overlaid text shapes also give you precise font control and guaranteed readability.

The creative direction often benefits from text-in-image for title slides and section dividers. Business and educational decks almost always use text shapes.

---

## Creative applications

The design direction files describe what kind of imagery fits each aesthetic. This section covers capabilities that go beyond conventional "stock photo" usage — the things that can turn a good presentation into an unforgettable one when deployed in the right context.

### Genre rendering

Every visual genre the model can produce is a tool for communication. The question is not "can I use manga in a presentation" but "what does manga communicate that photography cannot?"

**Manga and anime** — exaggeration of motion, emotion, and physical states. A manga-style illustration of someone frantically typing at a laptop, sweat drops flying, glasses askew, communicates urgency more viscerally than any photograph. Manga gives you speed lines, impact frames, exaggerated expressions, and narrative panels. Use it when the content involves conflict, urgency, transformation, or any scenario where emotional amplification serves the story. A trip-to-Japan recap, a team retrospective with dramatic moments, a product launch with a "battle" framing.

**Comic book and graphic novel** — narrative sequence, sound, impact, texture. Comics excel at depicting cause and effect, before/after states, and multi-step scenarios in a single image. Speech bubbles, action lines, sound effects (visual onomatopoeia) — these are communicative tools that have no equivalent in photography. A comic panel showing a server crashing with "BOOM!" communicates differently than a screenshot of an error log.

**Retro and stylized art** — nostalgia, humor, personality. A GTA-style poster of the team, a pixel-art representation of the product roadmap, a vintage travel-poster design for a team offsite invitation. These work because they are unexpected in a presentation context — the surprise itself is the engagement tool. Use them when the tone is informal, the audience will appreciate personality, and the content benefits from a distinctive visual frame.

**Editorial and cinematic** — credibility, gravitas, emotional depth. The visual language of magazines and film. This is the default for creative decks dealing with real subjects — people, places, products. Shallow depth of field, intentional lighting, color grading that matches the palette.

**Flat vector and diagrammatic** — clarity, explainability, structure. The default for educational content and technical diagrams. Clean lines, minimal palettes, labeled components. When the goal is understanding, not impression.

The point is not to use every genre in every deck. It is to know they exist, understand what each communicates, and reach for the right one when the context calls for it. A quarterly earnings report does not need manga. An engineering team's incident retrospective might.

Some genres are so heavily associated with text that the model will insert it unprompted — retro posters, propaganda art, magazine covers, comic panels. When working with these genres, handle text deliberately:
- Specify the exact text in quotes if you want text in the image
- Accept that text will appear and ensure enough context in the prompt for the model to generate something sensible, without specifying it directly
- Explicitly state `"no visible text"` or `"no text, no lettering"` if you want the style without any typography

Quick note here: the first 4 types go particularly well with reference images, if you have such. For example you could have 3 team members that you want to put in a manga scene, attach their individual pictures and prompt accordingly.

### Charts and data visualizations

The model produces clean, well-designed charts directly as images: bar charts, line graphs, pie charts, scatter plots, comparison tables, trend visualizations. At 2k resolution with reasonably sized labels, the results are production-quality and aesthetically polished.

This is a strong option when:
- The chart is complex enough that building it from ppt-cli shapes would be brittle or ugly
- The visualization needs to look polished and the model's design sense will produce a better result than manual construction
- The data is the visual centerpiece and the chart needs to feel like a designed artifact, not a generic Excel export

When prompting for charts, specify the data, the chart type, the style, and the palette: `"a horizontal bar chart showing five product categories with revenue values, dark background, accent color for the highest-performing bar, clean sans-serif labels, minimal grid lines."` Include the actual numbers and labels in the prompt — the model will render them.

Avoid small, dense text in chart labels. If the chart has 20+ items, use 2k resolution and keep label text at a size that would be readable in a presentation. Axis labels and fine-print footnotes are where text rendering becomes unreliable.

Chart elements don't have to be abstract rectangles. You can render bars, slices, or nodes as **thematic objects** that reinforce the subject matter — the chart remains readable as data, but the visual metaphor makes it memorable. For a farming deck, bars become buildings with rooftop gardens. For a logistics deck, bars become shipping containers. For a climate deck, a timeline's nodes become trees at different growth stages.

Control the intensity through the rendering style: for example `"flat silhouettes"` or `"clean geometric outlines"` keeps it restrained and immediately readable, while `"isometric 3D rendering with surface detail and lighting"` produces a striking creative visualization. Both are valid — match the tone to the deck. Specify the rendering treatment explicitly — `"bars as buildings"` alone lets the model decide whether that means flat icons or photorealistic 3D. State the visual style you want, not just the metaphor.

When highlighting an element in a 2D composition (chart, visualization, diagram, infographic), avoid generic `"glowing"` — it produces cheap-looking Photoshop-style outer glow effects. Instead, use vocabulary that produces natural-looking emphasis:
- `"luminous with soft radiance"` — the element appears to emit warm light naturally
- `"subtle rim light along its edges"` — a thin highlight outline that reads as intentional design, not a filter

Both produce noticeably more polished results than just specifying a non-descript `"warm glow"`. Being technically specific also works — for example `"2px soft glow at 10% opacity in warm amber"` — giving the model concrete parameters rather than a vague effect. Color contrast alone (a warmer hue or higher saturation against muted neighbors) is often a safer option.

### Consistent asset families

When a deck needs a set of related visual elements — matching icons, section header illustrations, decorative accents — generate them individually with a shared style description.

The style description is the coherence mechanism. If every icon prompt includes `"flat vector icon, single color #028090, white background, clean edges, rounded corners, 2px line weight"`, the resulting icons will feel like they belong to the same family. If every section illustration includes `"isometric 3D render, muted teal and coral palette, soft shadows, white background"`, the illustrations will feel cohesive.

This is how you create a visual identity for a deck without needing a pre-made asset library. The shared style prompt is the brand guide.

---

## Image processing and editing

The model edits existing images as well as generating new ones. Pass an existing image as `--ref` and describe the modification you want. This opens up workflows that would normally require graphic design software.

### Visual cohesion across user-provided images

When the user provides images that were not generated for this deck — photographs, screenshots, downloaded graphics — they will not match the deck's palette or mood. You can re-process them through image generation to create visual cohesion.

Pass the original image as a reference and prompt with the target treatment:

- **Duotone / colorization**: `"convert to duotone using deep navy #1A1A2E and coral #E94560"` — strips the original colors and re-maps to the deck's palette. Any image processed this way will feel like it belongs.
- **Color grading**: `"apply cinematic teal-and-orange color grading to match a moody editorial aesthetic"` — shifts the color balance without destroying the image content.
- **Monochrome + accent tint**: `"convert to black and white, then tint with #028090 at 30% intensity"` — creates a unified visual language across disparate source images.
- **Style adaptation**: `"render this photograph in the style of a flat vector illustration with a minimal palette"` — transforms the visual genre while preserving the subject.

This is one of the most powerful techniques for presentation visual cohesion. A deck that uses five photographs from five different sources, all color-graded to the same palette, looks intentionally designed. Without processing, it looks like a collage.

### Background and environment editing

- **Background replacement**: `"replace the background with a clean dark navy gradient"` — useful for team headshots, product images, or any subject that needs a consistent backdrop.
- **Background removal**: `"remove the background, leave white"` or `"remove the background, leave transparent"` — isolates the subject for placement over slide backgrounds or other elements.
- **Environment change**: `"place this product on a weathered oak desk with soft studio lighting"` — re-contextualizes an object.

### Effects and treatments

- **Blur and depth**: `"add shallow depth of field, blur the background"` — creates visual depth in flat images.
- **Texture and distortion**: `"add a subtle paper texture overlay"`, `"add a ripple effect"` — creative treatments for section dividers or atmospheric backgrounds.
- **Lighting modification**: `"change the lighting to golden hour warmth"` — shifts the mood without re-generating.

### Practical limits

Image editing degrades with repeated iterations. After 4-5 rounds of edits on the same image, quality starts to drop — colors shift, details soften, artifacts accumulate. If you need more than 5 edits:

- Batch 3-5 changes per iteration when possible (describe all modifications in one prompt).
- After 5 iterations, stop and ask the user whether to continue with the current result or start fresh.
- Never overwrite the source file when iterating. Save each iteration as a separate file so the user (or you) can revert to any previous state if a later edit produces a worse result.

---

## Workflow and iteration

### Low-resolution drafting

When the final image needs to be 2k but you expect multiple iterations (composition adjustments, prompt refinement, editing), work at 512 resolution first. The cost is less than half, and the generation is faster.

Once the 512 draft looks right — composition, colors, mood, subject placement all confirmed — generate the final version at the target resolution. Pass the 512 image as a reference and prompt: `"generate a high-resolution version of this image"` with `--resolution 2k`. The model will reproduce the composition at full quality.

This workflow is not necessary for every image. Use it when you expect to iterate — complex compositions, text-in-image where you want to verify rendering, or when the user is likely to request adjustments.

### Generating variations

Use `--count N` to generate multiple variations from the same prompt in parallel. This is useful when:
- The prompt is good but the specific composition matters (pick the best of 3-4)
- You want to offer the user a choice between interpretations
- The image involves text rendering and you want to verify at least one version is clean

Review all variations before committing. The best image from a batch of 4 is almost always better than a single generation.

### The --reasoning flag

Add `--reasoning` to generation commands when the image requires planning: complex multi-element compositions, embedded text, specific spatial relationships, detailed scene setups. The model takes longer but produces more accurate results.

Use `--reasoning` for:
- Title slides with text rendered into the image
- Complex scenes with multiple subjects interacting
- Detailed product mockups
- Any prompt where spatial precision matters

Skip it for: simple backgrounds, gradients, abstract textures, single-subject portraits, icons. These do not benefit from the extra planning time.

### Prompt refinement

When a generated image is close but not right, refine the prompt rather than rewriting it. Identify the specific dimension that is off (lighting too harsh? composition too centered? wrong color temperature?) and adjust that dimension. Adding `"warmer lighting"` or `"shift the subject to the left third"` to an otherwise working prompt is more effective than starting over.

If three rounds of refinement have not produced the desired result, the prompt structure itself may be the issue. Step back, reconsider the five dimensions, and write a fresh prompt with a different approach.

---

## Reference images

Reference images provide the model with visual anchors — a face to maintain, a style to match, an environment to place subjects in, an object to preserve. Can also be used for image editing — pass the image as `--ref` and prompt with the desired changes. Works with both `image-gen` and `add-image --prompt`, just `--ref photo1.png style_guide.jpg product.png` (up to 14 images). Reference files can be addressed by their filename in the prompt text — e.g. `"use photo1.png as the character and style_guide.jpg for the color treatment"`, if the specificity is needed.

### Character consistency

When a presentation features the same person across multiple slides (a case study subject, a mascot, a team member in different scenarios), pass their photo as a reference for each generation. The model will maintain facial structure, proportions, and identifying features while placing the person in new contexts.

Prompt pattern: `"[reference image is the person's face] — show this person presenting confidently in a modern conference room, medium shot, editorial photography"`.

### Style matching

Pass an existing image as a style reference to generate new images in the same visual language. This is useful when the deck has one strong image and you need more that feel like they belong to the same set.

Prompt pattern: `"[reference image defines the visual style] — generate a new image of a mountain landscape in the same style, color palette, and artistic treatment as the reference"`.

### Object and product consistency

For product presentations, pass a product photo as a reference to generate the same product in different contexts, angles, or environments. The model preserves design details, proportions, and branding elements.

### Role specification

When using multiple reference images, specify the role of each in the prompt: `"[image 1 is the character's face, image 2 is the style reference] — render this person in the artistic style of image 2, standing in a cyberpunk cityscape"`. Clear role assignment prevents the model from confusing which reference to use for what.

---

## Common presentation image patterns

Quick reference for recurring image needs. These are starting points — adjust the prompt dimensions to match the specific deck's direction and palette.

### Full-bleed slide backgrounds

Size to fill the slide. Specify negative space for text. Use `--ratio 16:9`, `--resolution 2k`, and position at `--x 0in --y 0in --w 13.333in --h 7.5in`.

Keep subjects off-center or specify atmospheric/abstract compositions that naturally accommodate overlaid text. Include `"negative space on the left for text overlay"` or `"subject positioned in the lower third"` in the prompt when text will be placed on the image.

### Half-bleed images

Fill one half of the slide. Match the aspect ratio to the split — a left-half image on a widescreen slide is roughly square or slightly tall. Specify `--ratio 1:1` or `--ratio 3:4` depending on the layout, and size to half the slide width.

### Concept and metaphor illustrations

For abstract ideas (growth, transformation, disruption, connection), describe a concrete visual metaphor rather than the abstract concept. `"A small green seedling sprouting from cracked dry earth with a single beam of warm sunlight"` works. `"An image representing growth"` does not.

### Icons and spot illustrations

Small images placed alongside text. Use `--ratio 1:1`, `--resolution 512`, and size at 0.4-0.6" in the slide. Prompt for clean, simple visuals: `"flat vector icon of a shield with a checkmark, single color, white background, clean edges"`. Generate all icons in a set with the same style description for visual consistency.

When generating elements that are not meant to fill their entire frame — icons, logos, spot illustrations, diagrams on a colored field — the model tends to "polish" the background with gradients, vignettes, glow, and/or lighting effects. This makes the image harder to place on a slide because the baked-in background won't match the slide surface. Fight this explicitly: `"solid flat #FFFFFF background, no gradients or effects"`. If the slide background is a specific color, use its hex value: `"solid flat #1A1A2E background, no gradients or effects"`.

### People and teams

Specify camera type and natural context to avoid uncanny results. Include lens, depth of field, and lighting: `"DSLR photograph, 85mm lens, shallow depth of field, natural window lighting"`. Avoid generic descriptions — specify the action, the environment, and the mood.

### Charts and graphs

Specify the data, chart type, and visual style: `"horizontal bar chart showing five categories with their revenue values, dark background, clean sans-serif labels, accent color highlighting the top performer"`. Include actual values in the prompt. Use 2k resolution for any chart with text labels.

---

## Anti-patterns

| Pattern | Why it fails | What to do instead |
|---------|-------------|-------------------|
| Keyword soup (`"business, professional, modern, clean, corporate"`) | Gives the model no compositional structure; produces generic output | Write a narrative sentence covering the five prompt dimensions |
| Vague subjects (`"a nice background"`, `"something professional"`) | The model fills in blanks with generic defaults | Describe specific subjects, materials, colors, and compositions |
| Ignoring composition when text will overlay | The model places subjects wherever it wants; text becomes unreadable | Specify negative space: `"subject in the right third, empty dark area on the left for text"` |
| Over-prompting with conflicting instructions | Stacking too many specific spatial requirements causes the model to satisfy some and ignore others | Focus each prompt on 3-4 key dimensions; break complex compositions into layers |
| Overwriting source files during iteration | If a later edit is worse, you cannot revert | Save each iteration separately; never overwrite the input file |
| Continuing past 5 edit iterations without checking in | Quality degrades and cost accumulates without clear improvement | After 5 iterations, pause and ask the user whether to continue or start fresh |
| Defaulting to conservative stock-photo aesthetics | Wastes the model's creative range; produces forgettable images | Consider whether the content would benefit from a distinctive visual genre — editorial, illustrated, stylized |
| Using 512 resolution for visible images (except icons) | Pixel density matters at presentation scale; low-res images look amateur | Use 1k minimum for inline images, 2k for hero and bleed images; reserve 512 for drafts and icons |
| Generic stock photography for concept slides (`"teamwork"`, `"innovation"`) | If the photo could illustrate any topic, it adds nothing to this specific one | Use specific visual metaphors tied to the actual content, or use illustration/diagram styles |
| Generic `"glowing"` or `"glow"` in 2D compositions | Produces cheap outer-glow layer effects | Use `"luminous with soft radiance"`, `"subtle rim light"`, or specify parameters (`"2px glow at 10% opacity"`) |
| Using physical artifact nouns (`"poster"`, `"label"`, `"book cover"`) | The model renders the artifact as an object inside the image — a picture *of* a poster, not an image that *is* a poster | Describe the aesthetic: `"vintage propaganda style, flat graphic, limited palette, bold silhouettes"` — name the visual qualities, not the physical object |

---

## Non-obvious command patterns

A few ppt-cli workflows for image generation that are not immediately apparent from `--help`.

**Full-slide background from a generated image.** Generate the image sized to fill the slide (`--w 13.333in --h 7.5in --x 0in --y 0in`), add it to the slide first, then add text shapes on top. Layer order is creation order — the image must be added before the text shapes so it sits behind them.

**Upscaling from a low-res draft.** Generate at `--resolution 512` for iteration, then pass the final draft as `--ref` with `--resolution 2k` and the prompt `"generate a high-resolution version of this image"`. The model reproduces the composition at full quality.

**Generating a consistent icon set.** Use `--ratio 1:1 --resolution 512` for all icons. Include the same style description in every prompt (`"flat vector icon, single color #HEXCODE, white background, clean edges"`), changing only the subject. Generate all icons in a batch for visual comparison, then insert them at consistent sizes and positions across slides.

**Processing a user-provided photo to match the deck palette.** Pass the photo as `--ref` and prompt with the target treatment: `"convert to duotone using #1A1A2E and #E94560"` or `"apply black and white, then colorize with #028090"`. The processed image will match the deck's visual language.

**Google search grounding.** Use `--grounded` to have the generation informed by current Google search results. Useful when the prompt references real places, current events, specific products, or anything where visual accuracy benefits from up-to-date reference data.
