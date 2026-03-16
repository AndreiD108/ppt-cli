# Image Generation — Annotated Prompt Template Library

Prompt templates, traps, and style vocabulary for AI image generation with ppt-cli.
Model: Gemini 3.1 Flash (`gemini-3.1-flash-image-preview`). Requires `GEMINI_API_KEY`, assume exists.

---

## WHAT THIS MODEL CAN DO

Recalibrate your assumptions. This model can:
- **Render text** directly into images (titles, labels, captions). Exception: very small text (<20px) may be unreliable.
- **Complex compositions** with multiple subjects, specific spatial relationships, layered elements.
- **Genre rendering**: manga, comic panels, retro posters, propaganda art, pixel art, editorial photography — not gimmicks, communicative tools.
- **Charts and data visualizations**: bar charts, line graphs, scatter plots with actual numbers and labels.
- **Structured visuals**: diagrams, flowcharts, architectural views, isometric renders.
- **Image editing**: color grading, background replacement, style transfer, inpainting, adding/removing elements.
- **Subject consistency** across multiple images using `--ref` with a reference image.

These capabilities mean you should reach for image generation more often than you expect. A generated chart can be cleaner than shapes; a generated diagram can handle complexity that positioned textboxes cannot.

---

## GLOBAL TRAPS

These anti-patterns apply across many template types. Read before writing any prompt.

```
TRAP  physical-artifact-nouns
      Never use "poster", "label", "book cover", "card", "brochure" as the subject.
      The model renders the artifact AS AN OBJECT inside the image — a picture OF a
      poster, not an image that IS a poster.
      FIX: describe the aesthetic: "vintage propaganda style, flat graphic, limited
      palette, bold silhouettes" — name the visual qualities, not the physical object.

TRAP  "glowing" / "glow" in 2D compositions
      Produces cheap outer-glow Photoshop-style effects on charts, diagrams, icons.
      FIX: "luminous with soft radiance" | "subtle rim light along edges" |
      "2px soft glow at 10% opacity in warm amber" | or just use color contrast
      (warmer hue / higher saturation against muted neighbors).

TRAP  keyword-soup prompts
      "business, professional, modern, clean, corporate" gives the model no
      compositional structure. Produces generic stock output.
      FIX: write narrative sentences covering the five dimensions (see below).

TRAP  vague subjects
      "a nice background", "something professional" — model fills blanks with
      generic defaults.
      FIX: specific subjects, materials, colors, compositions.

TRAP  text-heavy genres insert text unprompted
      Retro posters, propaganda art, magazine covers, comic panels — the model
      will add text whether you want it or not.
      FIX: if you want text, specify it in quotes. If you don't, add
      "no visible text, no lettering" explicitly.

TRAP  defaulting to stock-photo aesthetics
      Wastes the model's creative range; produces forgettable images.
      FIX: consider whether the content benefits from a distinctive visual genre —
      editorial, illustrated, stylized, manga, comic, retro.

TRAP  generic stock photography for concept slides
      "teamwork", "innovation" — if the photo could illustrate any topic, it adds
      nothing to this specific one.
      FIX: use specific visual metaphors tied to the actual content, or use
      illustration/diagram styles.

TRAP  overwriting source files during iteration
      If a later edit is worse, you cannot revert.
      FIX: save each iteration as a separate file. Never overwrite the input.

TRAP  continuing past 5 edit iterations without checking in
      Quality degrades — colors shift, details soften, artifacts accumulate.
      FIX: after 5 iterations, pause and ask the user whether to continue or
      start fresh. Batch 3-5 changes per iteration when possible.
```

---

## FIVE DIMENSIONS

All five for hero/editorial/complex scenes. Subject + style may suffice for icons.

```
Subject:      specific materials, textures, colors, details.
              "weathered oak desk with visible grain" > "desk"
              Specificity is the single highest-leverage improvement.

Action:       what subject does / how arranged. Compositional intent.
              "presenting to a boardroom" > standing alone.

Setting:      where the scene takes place. Implies lighting.
              "glass-walled conference room at golden hour"

Composition:  framing, angle, distance, negative space.
              "subject left third, empty right for text overlay"

Style:        genre + color grading + film/lens. Emotional register.
              "editorial photography, cinematic teal-and-orange grading"
```

Dimensions stack without degradation: rich style + simple subject works well. When the composition is too complex for a single prompt (15-20+ specific positioned items), break into layers and compose on the slide.

Specify hex for colors that tie the image to the deck — backgrounds, accents, color grading targets, lighting hues. Natural language for scene-internal colors that don't need to match across slides.

---

## PROMPT TEMPLATES

### Hero / Full-Bleed Background

```
FLAGS:  --ratio 16:9 --resolution 2k
PLACE:  --x 0in --y 0in --w 13.333in --h 7.5in
ORDER:  add image FIRST, then text shapes on top (layer order = creation order)
        if not just a background, have the text baked in by including in prompt!

TRAP:   ignoring composition when text will overlay — model places subjects wherever
        it wants, text becomes unreadable.
        MUST specify negative space when text will overlay, or specify text in prompt (bake in).

PROMPT SKELETON:
"{subject with specific materials/textures},
{setting with implied lighting},
{composition: wide or medium shot, subject in [left|right|lower] third,
negative space on [opposite side] for text overlay},
{style: genre + color grading + film/lens}"

EXAMPLE:
"A confident engineer presenting an architecture diagram on a large screen,
modern tech office with floor-to-ceiling windows, medium shot from a slight
low angle, shallow depth of field, editorial photography with cinematic
teal-and-orange color grading"
```

### Half-Bleed (Image Occupies Half the Slide)

```
FLAGS:  --ratio 1:1 or 3:4 (left/right split) | --ratio 16:9 (top/bottom strip)
        --resolution 2k
PLACE:  left half: --x 0in --y 0in --w 6.667in --h 7.5in
        right half: --x 6.667in --y 0in --w 6.667in --h 7.5in
        top half: --x 0in --y 0in --w 13.333in --h 3.75in

TRAP:   ratio mismatch with slide dimensions produces awkward cropping.
        Always set --ratio explicitly to match the split geometry.

PROMPT SKELETON:
"{subject with specific detail},
{setting anchoring the scene},
{composition: subject fills frame, no dead space on the text-adjacent edge},
{style matching deck direction}"
```

### Icon / Spot Illustration

```
FLAGS:  --ratio 1:1 --resolution 512
PLACE:  --w 0.4in to 0.6in (sized small alongside text)

TRAP:   model adds gradients, vignettes, glow, and lighting effects to backgrounds.
        Makes the icon impossible to place cleanly on a slide.
        Fight this explicitly with "solid flat {color} background, no gradients
        or effects".

RULE:   generate ALL icons in a set with the SAME style description. The shared
        style string is the coherence mechanism — it creates a visual family.

PROMPT SKELETON:
"flat vector icon of {subject},
single color {#HEX from theme},
solid flat {#BG_HEX} background, no gradients or effects,
clean edges, {rounded|sharp corners}, {Npx line weight}"

NOTE:   if the slide background is a specific color, use its hex as BG_HEX.
        If white, use #FFFFFF.
```

### Concept / Metaphor Illustration

```
FLAGS:  --ratio 16:9 or 1:1 depending on layout --resolution 1k or 2k

TRAP:   abstract nouns produce nothing useful. "An image representing growth" fails.
        MUST describe a concrete visual metaphor.

PROMPT SKELETON:
"{concrete metaphorical subject — e.g., small green seedling sprouting
from cracked dry earth with a single beam of warm sunlight},
{setting that reinforces the metaphor},
{composition appropriate to slide placement},
{style: illustration or photography depending on deck direction}"
```

### Chart / Data Visualization

```
FLAGS:  --ratio 16:9 or 4:3 --resolution 2k (text labels need high resolution)

TRAP:   "glowing" highlight produces cheap effects — see GLOBAL TRAPS.
TRAP:   small dense text in labels. If 20+ items, ensure label text is readable
        at presentation scale. Axis labels and footnotes are where text rendering
        becomes unreliable.

RULE:   include actual data, numbers, and labels in the prompt — the model renders them.
RULE:   chart elements can be thematic objects (bars as buildings, nodes as trees)
        but specify the rendering treatment explicitly — "bars as buildings" alone
        lets the model decide flat vs photorealistic. State the visual style.

PROMPT SKELETON:
"{chart type} showing {data description with actual values and labels},
{background color/style}, {accent color for highlighted element},
clean {font style} labels, minimal grid lines,
{optional: thematic element treatment with explicit rendering style}"

EXAMPLE:
"horizontal bar chart showing five product categories with revenue values,
dark #1A1A2E background, accent #E94560 for the top performer,
clean sans-serif labels in white, minimal grid lines"

THEMATIC EXAMPLE:
"bar chart where bars are flat silhouette buildings with rooftop gardens,
clean geometric outlines, muted earth tones, readable axis labels"
```

### People / Team Photos

```
FLAGS:  --ratio 3:4 or 1:1 (portraits) | --ratio 16:9 (scene) --resolution 2k

TRAP:   generic descriptions produce uncanny results.
        MUST specify camera, lens, depth of field, and lighting.

PROMPT SKELETON:
"{person description with specific action and environment},
{DSLR|mirrorless} photograph, {focal length} lens,
shallow depth of field, {lighting type},
{style: editorial | corporate | photojournalistic}"

EXAMPLE:
"a data scientist explaining a dashboard in a modern open-plan office,
DSLR photograph, 85mm lens, shallow depth of field,
natural window lighting, editorial photography"
```

### Text-in-Image

```
FLAGS:  --reasoning (use for any text-in-image — spatial precision matters)
        --resolution 2k

WHEN TO USE: text is part of the visual composition — title rendered into a dramatic
background, a word used as visual element, labels integrated into a diagram.
WHEN NOT TO USE: text needs to be editable, content might change, or text is
functional (body copy, descriptions). Use text shapes overlaid on the image instead.

RULES:
  1. Enclose text in quotes within the prompt: the word "INNOVATE"
  2. Specify font style: "bold white sans-serif" | "thin minimalist" | "heavy Impact-style"
     Font style includes material treatments when text is THE visual element.
     Clean typography when overlay; material treatments when subject.
  3. Specify placement: "centered at top" | "bottom-left corner" | "filling center"
  4. Keep short: 1-5 words most reliable. Multiple sentences work but error rate increases.

WORKFLOW: text in stylized images
  Sentences and short phrases: prompt directly — reliable for headlines, labels,
  captions, short statements.
  Dense or exact text (code listings, terminal output, data tables): use --ref with
  a screenshot or render of the text, if available. The model reproduces reference
  text faithfully while applying the prompted visual treatment (CRT screen,
  chalkboard, neon sign, printed page, notebook).

TRAP:   over-prompting spatial relationships for text + multiple elements.
        Focus on 3-4 key dimensions; break complex compositions into layers.

PROMPT SKELETON:
"{scene/background description},
the word \"{TEXT}\" in {font style} {color} font,
{placement in frame},
{style}"
```

### Genre Rendering

Each genre communicates differently. Choose based on what the content needs, not novelty.

#### Manga / Anime
```
USE WHEN: urgency, transformation, emotional amplification, conflict, exaggerated
          states. Trip-to-Japan recaps, team retrospectives with dramatic moments,
          product launch with "battle" framing.
TOOLS:    speed lines, impact frames, exaggerated expressions, narrative panels.

PROMPT SKELETON:
"{character description} in {dramatic action with manga conventions —
speed lines, sweat drops, impact marks},
{manga/anime style reference — e.g., shonen action, Studio Ghibli, Makoto Shinkai},
{color treatment}"

TIP:  works particularly well with reference images — e.g., 3 team members' photos
      rendered into a manga scene.
```

#### Comic Book / Graphic Novel
```
USE WHEN: cause-and-effect, before/after, multi-step scenarios, narrative sequences.
          A server crash with "BOOM!" communicates differently than an error log screenshot.
TOOLS:    speech bubbles, action lines, sound effects (visual onomatopoeia), panels.

PROMPT SKELETON:
"{scene with comic conventions — panels, speech bubbles, action lines},
{comic style reference — e.g., Moebius, Mignola, ligne claire},
{color: bold primaries | noir B&W | muted vintage}"
```

#### Retro / Stylized Art
```
USE WHEN: nostalgia, humor, personality. Informal tone, audience appreciates personality.
          GTA-style team poster, pixel-art roadmap, vintage travel poster for offsite.
TOOLS:    the surprise of an unexpected visual frame IS the engagement tool.

TRAP:   text-heavy genres (retro posters, propaganda art) — see GLOBAL TRAPS.

PROMPT SKELETON:
"{subject in retro/stylized treatment},
{specific era/style: 1960s travel poster | 8-bit pixel art | Art Deco |
Soviet propaganda graphic | GTA loading screen},
{palette: limited, period-appropriate},
{optional: 'no visible text' if text not wanted}"
```

#### Editorial / Cinematic
```
USE WHEN: credibility, gravitas, emotional depth. Default for creative decks with
          real subjects — people, places, products.
TOOLS:    shallow depth of field, intentional lighting, color grading matching palette.

PROMPT SKELETON:
"{subject in real-world context},
{setting with specific lighting},
{camera: focal length, angle, depth of field},
editorial photography, {color grading: teal-and-orange | desaturated | warm film}"
```

#### Flat Vector / Diagrammatic
```
USE WHEN: clarity, explainability, structure. Default for educational and technical content.
TOOLS:    clean lines, minimal palettes, labeled components.

PROMPT SKELETON:
"flat vector illustration of {subject with labeled components},
{N}-color palette using {hex values from theme},
clean lines, {white|dark} background, no gradients,
{optional: isometric perspective | exploded view | cutaway}"
```

---

## STYLE VOCABULARY

### Photography Styles
- `editorial photography, cinematic color grading` — magazine-quality, moody
- `corporate photography, clean lighting` — professional, neutral
- `fashion magazine style editorial` — bold, stylized
- `photojournalistic style` — documentary, candid
- `high-end product photography` — studio, controlled

### Illustration Styles
- `flat vector illustration, minimal palette` — clean, diagrammatic
- `isometric 3D render` — spatial, architectural
- `high-fidelity 3D render` — realistic objects, environments
- `watercolor painting style` — soft, artistic
- `pencil sketch on white paper` — conceptual, in-progress feel

### Film and Color
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

### Camera and Lens
- `shallow depth of field (f/1.8)` — blurred background, subject pops
- `wide-angle lens` — vast scale, landscapes, architecture
- `50mm lens` — natural human-eye perspective
- `macro lens` — extreme close-up detail
- `low-angle shot` — subject appears powerful, imposing
- `bird's eye view` — overview, maps, layouts
- `tilt-shift miniature effect` — makes real scenes look like models

These combine freely. `editorial photography, golden hour backlighting, shallow depth of field, Fujifilm color science` is a valid, effective combination.

---

## STYLE ANCHORS

### Brand Aesthetics

Brand names compress entire design systems (proportions, color relationships, abstraction level, whitespace philosophy) into a few words the model already understands.

**Clean tech / SaaS illustration**
- Stripe — polished gradients, geometric precision, premium feel
- Notion — hand-drawn-feeling, minimal, warm, approachable
- Linear — ultra-minimal, monochrome, precise, developer-oriented
- Figma — colorful but structured, playful geometry
- Slack — rounded, friendly, bold colors, approachable characters
- Mailchimp — quirky, hand-drawn, personality-forward
- Spotify — bold duotones, gradient washes, energetic
- Vercel — dark, sleek, subtle gradients, developer-premium
- Shopify — green-tinted, approachable, commerce-oriented

**Data and editorial**
- Bloomberg — dark backgrounds, neon accents, data-dense, financial authority
- The New York Times — conceptual editorial illustration, sophisticated metaphors
- The New Yorker — distinctive illustrated covers, literary tone
- Monocle — clean editorial photography, sophisticated restraint
- The Economist — red/white, sharp, authoritative infographics
- Wired — futuristic, high-contrast, tech-forward editorial

**Premium / minimal**
- Apple — whitespace, product-focused, precision photography
- Muji — no-brand minimalism, natural materials, quietness
- Aesop — botanical, typographic, apothecary warmth
- Dieter Rams / Braun — functional, systematic, grid-based
- Kinfolk — muted earth tones, quiet photography, lots of whitespace
- IKEA — functional, democratic design, bright primary accents on clean backgrounds

**Playful / human**
- Headspace — soft, rounded, calming, warm palettes
- Airbnb — warm lifestyle photography, human connection
- Duolingo — bright, bold, cartoonish, high energy
- Google / Material Design — clean, geometric, bold primary colors, structured motion
- Lego — bright, blocky, constructive, joyful

### Named References

Named artists, studios, directors, and movements compress entire visual systems.

**Anime and Manga**
- Studio Ghibli — soft painterly backgrounds, natural settings, emotional warmth
- Makoto Shinkai — hyperrealistic skies, dramatic light shafts, vivid saturated color
- Shonen (Dragon Ball, Naruto) — high energy, speed lines, impact frames, exaggerated action
- Akira / Katsuhiro Otomo — detailed cyberpunk, mechanical precision, dystopian scale
- Junji Ito — intricate linework, unsettling compositions, horror

**Comics and Graphic Novels**
- Moebius / Jean Giraud — dreamlike, detailed, European sci-fi, vast landscapes
- Mike Mignola (Hellboy) — heavy black shadows, minimal detail, gothic
- Frank Miller (Sin City) — extreme high-contrast black and white, noir
- Hergé (Tintin) — ligne claire, clean outlines, flat colors, precise
- Jack Kirby — cosmic scale, crackling energy, bold geometric compositions

**Photography**
- Annie Leibovitz — dramatic editorial portraits, theatrical staging
- Ansel Adams — monumental black and white landscapes, tonal range
- Steve McCurry — vivid National Geographic, cultural portraiture, intense eyes
- Andreas Gursky — massive scale, architectural repetition, almost abstract
- Peter Lindbergh — raw black and white fashion, emotional, unretouched

**Illustration**
- Charley Harper — geometric, minimal, nature subjects reduced to shapes
- Saul Bass — bold graphic design, movie poster aesthetic, strong silhouettes
- Mary Blair — mid-century Disney, bold flat color, stylized shapes
- Alphonse Mucha — Art Nouveau, decorative, flowing organic lines
- Edward Gorey — pen and ink, gothic Victorian, darkly whimsical

**Film / Cinematic**
- Wes Anderson — symmetrical framing, pastel palettes, dollhouse precision
- Ridley Scott — atmospheric, smoky, industrial, epic scale
- Denis Villeneuve — vast minimalist landscapes, muted desaturated tones, monumental
- Wong Kar-wai — neon-soaked, motion blur, saturated romantic melancholy
- David Lynch — surreal, unsettling, dreamlike, high contrast

**Data Visualization and Infographics**
- Edward Tufte — maximum data-ink ratio, no chartjunk, precise and minimal
- David McCandless (Information is Beautiful) — colorful, modern, accessible, pop
- Isotype / Otto Neurath — pictographic statistics, simplified icons representing quantities

---

## WORKFLOW PATTERNS

### Low-Resolution Drafting
When expecting multiple iterations, draft at `--resolution 512` (less than half the cost, faster). Once composition, colors, mood, and subject placement are confirmed, generate the final version at target resolution. Pass the 512 draft as `--ref` and prompt: `"generate a high-resolution version of this image"` with `--resolution 2k`.

Use this workflow for: complex compositions, text-in-image verification, prompts where the user is likely to request adjustments. Skip for: simple backgrounds, single-subject images, icons.

### Generating Variations
Use `--count N` to generate multiple variations in parallel. Useful when:
- Composition matters — pick the best of 3-4
- Offering the user a choice between interpretations
- Text rendering — verify at least one version is clean

Review all variations before committing. Best of 4 is almost always better than a single generation.

### Prompt Refinement
When a generation is close but not right, refine the specific dimension that is off (lighting, composition, color temperature) rather than rewriting the entire prompt. If three rounds of refinement have not produced the desired result, the prompt structure itself is the issue — step back, reconsider the five dimensions, write a fresh prompt with a different approach.

### Budget Planning
Before generating images, estimate total cost and confirm with the user:
- 512: ~$0.045 per image
- 1k: ~$0.067 per image
- 2k: ~$0.10 per image

Present the estimate as a range. A 20-slide deck with 10 images at 2k: ~$1. With iterations: $3-5.

### Consistent Asset Families
When a deck needs a set of related elements (matching icons, section illustrations, decorative accents), use the same style description string across all prompts. The shared style string IS the brand guide — it creates visual coherence without a pre-made asset library.

### Complexity Ceiling
5-8 specific positioned objects works reliably. 15-20+ with precise spatial relationships becomes unreliable. This limit applies to concrete spatial instructions, NOT to style/mood/lighting/color which stack without degradation. When composition is too complex, break into layers: generate background, foreground elements separately, compose on the slide.

---

## EDITING OPERATIONS

Pass an existing image as `--ref` and describe the modification. Same model, same commands.

### Visual Cohesion (Unifying Disparate Source Images)
- **Duotone / colorization**: `"convert to duotone using deep navy #1A1A2E and coral #E94560"` — strips original colors, re-maps to deck palette
- **Color grading**: `"apply cinematic teal-and-orange color grading to match a moody editorial aesthetic"` — shifts color balance, preserves content
- **Monochrome + accent tint**: `"convert to black and white, then tint with #028090 at 30% intensity"` — unifies disparate sources
- **Style adaptation**: `"render this photograph in the style of a flat vector illustration with a minimal palette"` — transforms genre, preserves subject

Five photographs from five sources, all color-graded to the same palette, look intentionally designed. Without processing, they look like a collage.

### Background and Environment
- **Background replacement**: frame as a "professional reshoot" or "color-graded composite", not just a background "replacement". `"Replace the background with X"` produces a cheap cutout.
- **Background removal**: `"remove the background, leave white"` or `"leave transparent"` — isolate subjects. Works well because isolation on solid is a well-defined operation.
- **Environment change**: `"place this product on a weathered oak desk with soft studio lighting"` — re-contextualize

### Effects and Treatments
- **Blur and depth**: `"add shallow depth of field, blur the background"` — create depth in flat images
- **Texture and distortion**: `"add a subtle paper texture overlay"`, `"add a ripple effect"` — creative treatments
- **Lighting modification**: `"change the lighting to golden hour warmth"` — shift mood without re-generating

### Reference Images
Use `--ref` with both `image-gen` and `add-image --prompt`. Up to 14 images. Reference files can be addressed by filename in the prompt: `"use photo1.png as the character and style_guide.jpg for the color treatment"`.

**Character consistency**: pass a person's photo as reference for each generation to maintain facial structure, proportions, and features across slides. Pattern: `"[reference is the person's face] — show this person presenting in a conference room, medium shot, editorial photography"`.

**Style matching**: pass an existing image to generate new images in the same visual language. Pattern: `"[reference defines visual style] — generate a mountain landscape in the same style and palette as the reference"`.

**Object/product consistency**: pass a product photo to generate it in different contexts while preserving design details, proportions, and branding.

**Multiple references — specify roles**: `"[image 1 is the character, image 2 is the style reference] — render this person in the style of image 2, standing in a cyberpunk cityscape"`. Clear role assignment prevents confusion.

---

## FLAGS QUICK REFERENCE

### `add-image` (into a slide)
```
ppt-cli add-image DECK.pptx SLIDE [image_path | --prompt "..."]
  --prompt TEXT        generate with AI instead of inserting a file
  --resolution 512|1k|2k   pixel resolution (default: 1k). Only with --prompt
  --ratio RATIO        aspect ratio (e.g. 16:9). Auto-guessed from --w/--h. Only with --prompt
  --grounding search|image|full   ground with web/image search. Only with --prompt
  --reasoning          enable model reasoning for better spatial precision. Only with --prompt
  --ref IMAGE [IMAGE...]   reference images for editing/style transfer (max 14). Only with --prompt
  --x, --y             position on slide (default: 1in, 1in)
  --w, --h             shape size on slide
  -o, --output         save to new file instead of overwriting
```

### `image-gen` (standalone, to disk)
```
ppt-cli image-gen "PROMPT"
  --resolution 512|1k|2k   pixel resolution (default: 1k)
  --ratio RATIO        aspect ratio (e.g. 16:9, 1:1)
  --grounding search|image|full   ground with web/image search
  --reasoning          enable model reasoning
  --ref IMAGE [IMAGE...]   reference images (max 14)
  --count N            generate N images in parallel
  -o, --output         output path (default: /tmp/ppt-cli/image-gen/{name}.png)
```

### Supported Ratios
`1:1`, `1:4`, `1:8`, `2:3`, `3:2`, `3:4`, `4:1`, `4:3`, `4:5`, `5:4`, `8:1`, `9:16`, `9:21`, `16:9`, `21:9`

### Aspect Ratio by Layout
| Layout | Ratio | Notes |
|--------|-------|-------|
| Full-bleed background | 16:9 | Fills entire slide |
| Half-bleed (left/right) | 3:4 or 1:1 | Depends on split width |
| Half-bleed (top/bottom) | 16:9 | Wide strip |
| Icon / spot illustration | 1:1 | Square, sized small |
| Stat callout background | 16:9 | Behind a stat |

### Resolution by Use
| Use | Resolution | Cost |
|-----|-----------|------|
| Hero, full-bleed, half-bleed | 2k | ~$0.10 |
| Medium inline, diagrams, half-bleed | 1k | ~$0.067 |
| Icons, thumbnails, drafts | 512 | ~$0.045 |

Use 2k for creative decks (any visible image). 1k acceptable for business/educational inline images. 512 only for icons and draft iterations.

### Text Rendering
Works for headlines, labels, captions, poster typography. Handles font style, size, placement. Exception: very small text (fine print, dense labels on complex charts). Anything readable at presentation viewing distance is fair game.

### The `--reasoning` Flag
Use for: title slides with text in image, complex multi-element scenes, detailed product mockups, anything where spatial precision matters a lot.

### The `--grounding` Flag
Use when the prompt references real places, current events, specific products, or anything where visual accuracy benefits from up-to-date reference data. Values: `search` (web search), `image` (image search), `full` (both).
