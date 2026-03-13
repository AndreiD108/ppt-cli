# Image Prompting Tips for ppt-cli

Practical prompt engineering guidance for `ppt-cli image-gen` and
`ppt-cli add-image --prompt`. These tips are adapted from the Nano Banana
prompting frameworks and tailored for generating presentation-quality visuals.

---

## Quick Reference: The Two Commands

```bash
# Standalone generation (saves to disk)
ppt-cli image-gen "your prompt here" --ratio 16:9 --resolution 2k -o slide-bg.png

# Generate and insert into a slide in one step
ppt-cli add-image deck.pptx 3 --prompt "your prompt here" --ratio 16:9 --w 10in --h 5.625in
```

Both commands accept `--resolution` (512, 1k, 2k), `--ratio` (e.g., 16:9,
1:1), and `--reasoning` (slower but better results). Use `--count N` with
`image-gen` to generate multiple variations in parallel and pick the best one.

---

## 1. Prompt Structure

A prompt made of isolated keywords produces generic, unfocused results.
Instead, construct your prompt as a narrative sentence that covers five
dimensions in order:

**Formula:** `[Subject] + [Action/State] + [Setting] + [Composition] + [Style]`

Each dimension answers one question:

| Dimension | Question it answers | Presentation example |
|---|---|---|
| Subject | What is in the image? | A confident woman in business attire |
| Action/State | What is it doing? | Presenting to a boardroom |
| Setting | Where is this happening? | A modern glass-walled conference room |
| Composition | How is the shot framed? | Wide shot, rule of thirds |
| Style | What does it look and feel like? | Corporate photography, clean lighting |

### Example: Full-Stack Prompt for a Title Slide Background

```bash
ppt-cli add-image deck.pptx 1 \
  --prompt "An aerial view of a sprawling modern cityscape at golden hour, \
warm sunlight reflecting off glass towers, wide-angle lens, cinematic \
color grading with warm amber tones, editorial photography style" \
  --ratio 16:9 --resolution 2k --w 13.333in --h 7.5in
```

### Example: Product Slide Hero Image

```bash
ppt-cli image-gen \
  "A sleek wireless earbud resting on a dark marble surface, three-point \
softbox studio lighting, shallow depth of field (f/1.8), center-framed, \
high-end product photography on a medium-format digital camera" \
  --ratio 16:9 --resolution 2k
```

---

## 2. Style Modifiers

Style modifiers go at the end of your prompt and dramatically shift the visual
output. Mix and match from these categories.

### Photography Styles

Use these when you want realistic, photographic images:

- `editorial photography` -- clean, magazine-quality
- `photojournalistic style` -- documentary, candid feel
- `corporate photography, clean lighting` -- safe for business decks
- `high-end product photography` -- for product showcases
- `fashion magazine style editorial` -- bold and stylized

### Art and Illustration Styles

Use these for conceptual slides, section dividers, or creative decks:

- `flat vector illustration, minimal palette` -- clean diagrams
- `watercolor painting style` -- soft, artistic feel
- `isometric 3D render` -- good for tech/architecture concepts
- `high-fidelity 3D render` -- realistic objects/environments
- `pencil sketch on white paper` -- brainstorming/ideation slides

### Film Stock and Color Grading

These modifiers control the emotional tone through color and texture:

- `cinematic color grading with muted teal tones` -- modern, moody
- `as if shot on 1980s color film, slightly grainy` -- nostalgic, warm
- `shot on medium-format analog film, pronounced grain, high saturation` -- editorial punch
- `shot on a cheap disposable camera, raw flash aesthetic` -- raw authenticity
- `Fujifilm color science` -- natural, slightly warm tones
- `desaturated, high contrast black and white` -- dramatic emphasis

### Example: Section Divider with Artistic Style

```bash
ppt-cli add-image deck.pptx 5 \
  --prompt "Abstract geometric shapes representing data connections and \
neural networks, dark navy background with glowing cyan and magenta \
accents, flat vector illustration, minimal palette" \
  --ratio 16:9 --w 13.333in --h 7.5in
```

---

## 3. Lighting Direction

Lighting is the single most impactful creative control. Be explicit about how
the scene is illuminated rather than leaving it to chance.

### Studio Lighting (for products, portraits, professional shots)

- `three-point softbox setup` -- even, professional, no harsh shadows
- `single key light from the left with a white fill card` -- subtle dimension
- `soft and radiant studio lighting` -- beauty/product shots
- `ring light, even front illumination` -- flat, modern look

### Dramatic and Environmental Lighting

- `golden hour backlighting creating long shadows` -- warm, inspiring
- `Chiaroscuro lighting with harsh, high contrast` -- dramatic emphasis
- `neon-lit, cyberpunk lighting in pink and blue` -- tech/futuristic
- `overcast diffused daylight` -- neutral, documentary
- `dappled sunlight through trees` -- natural, organic

### Example: Dramatic Keynote Visual

```bash
ppt-cli image-gen \
  "A lone figure standing at the edge of a cliff overlooking a vast \
valley, golden hour backlighting creating long shadows, wide-angle \
lens, cinematic color grading with warm amber tones" \
  --ratio 16:9 --resolution 2k
```

---

## 4. Camera, Lens, and Composition

Using specific photographic terminology gives you precise control over
framing, depth, and perspective.

### Camera/Hardware Cues

Different camera references produce different visual DNA:

- `shot on a medium-format digital camera` -- high detail, shallow DOF
- `shot on a GoPro` -- immersive, wide, distorted action feel
- `shot on a Fujifilm camera` -- warm, natural color science
- `shot on a cheap disposable camera` -- raw, nostalgic, flash-heavy
- `DSLR photograph` -- general high-quality photography baseline

### Lens and Depth of Field

- `shallow depth of field (f/1.8)` -- blurred background, subject pops
- `wide-angle lens` -- shows vast scale, good for landscapes and architecture
- `macro lens` -- extreme close-up detail
- `50mm lens` -- natural human-eye perspective
- `telephoto lens, compressed perspective` -- flattened layers, dense feel
- `low-angle shot` -- subject looks powerful, imposing
- `bird's eye view` -- maps, layouts, overview perspectives
- `tilt-shift miniature effect` -- makes real scenes look like models

### Framing and Composition

- `center-framed` -- subject dominates, symmetric
- `rule of thirds` -- balanced, natural
- `medium-full shot` -- shows subject with context
- `wide shot` -- environment emphasis
- `extreme close-up` -- texture and detail
- `negative space on the right for text overlay` -- leave room for slide text

### Example: Team Photo Replacement

```bash
ppt-cli add-image deck.pptx 7 \
  --prompt "A diverse team of four professionals collaborating around a \
whiteboard in a bright modern office, DSLR photograph, 50mm lens, \
shallow depth of field, corporate photography, clean natural lighting, \
negative space on the left for text overlay" \
  --ratio 16:9 --w 8in --h 4.5in --x 4.5in --y 1.5in
```

---

## 5. Materiality and Texture

When generating objects, products, or characters, specify their physical
materials. Generic terms produce generic results.

### Instead of This, Say This

| Generic | Specific |
|---|---|
| a suit jacket | a navy blue tweed suit jacket |
| armor | ornate elven plate armor, etched with silver leaf patterns |
| a coffee mug | a minimalist matte ceramic coffee mug |
| a desk | a weathered oak desk with visible wood grain |
| a phone | a glossy black smartphone with chamfered aluminum edges |

### Example: Product Mockup

```bash
ppt-cli image-gen \
  "A minimalist matte ceramic coffee mug with a subtle embossed logo, \
resting on a weathered oak desk with visible wood grain, three-point \
softbox studio lighting, shallow depth of field, high-end product \
photography" \
  --ratio 1:1 --resolution 2k
```

---

## 6. Text in Images

The AI model can render legible text directly into images -- useful for
mockup slides, poster concepts, or hero banners.

### Rules for Sharp Typography

1. **Enclose text in quotes** within the prompt: `the word "INNOVATE"`
2. **Describe the font style explicitly**: `bold white sans-serif font`,
   `thin minimalist Century Gothic font`, `heavy blocky Impact font`,
   `flowing elegant script font`
3. **Specify text placement**: `centered at the top`, `bottom-left corner`
4. **Keep it short**: One to three words render most reliably

### Example: Conference Title Slide

```bash
ppt-cli add-image deck.pptx 1 \
  --prompt "A dramatic dark gradient background transitioning from deep \
navy to black, with the word \"SUMMIT\" in large bold white sans-serif \
font centered in the frame, and \"2026\" in a thin minimalist font \
directly below it, clean typographic poster design" \
  --ratio 16:9 --resolution 2k --w 13.333in --h 7.5in
```

### Example: Motivational Section Break

```bash
ppt-cli image-gen \
  "A typographic poster with a solid black background, bold white letters \
spell \"Think Different\", filling the center of the frame, clean \
minimalist design, high contrast" \
  --ratio 16:9 --resolution 2k
```

---

## 7. Common Presentation Image Patterns

Recurring image needs mapped to prompt strategies.

### Full-Bleed Slide Backgrounds

Use `--ratio 16:9` and size to fill the slide (`--w 13.333in --h 7.5in`
for widescreen). Keep subjects off-center to leave text space:

```bash
ppt-cli add-image deck.pptx 2 \
  --prompt "Soft abstract gradient of deep blue to teal, subtle bokeh \
light particles floating, minimal and elegant, out of focus" \
  --ratio 16:9 --resolution 2k --w 13.333in --h 7.5in --x 0in --y 0in
```

### Concept/Metaphor Illustrations

For abstract business concepts (growth, transformation, disruption):

```bash
ppt-cli image-gen \
  "A small green seedling sprouting from cracked dry earth with a single \
beam of warm sunlight illuminating it, shallow depth of field, \
cinematic color grading, metaphor for growth and resilience" \
  --ratio 16:9 --resolution 2k
```

### Icon-Style Spot Illustrations

Small images placed alongside text. Use `1:1` ratio and smaller dimensions:

```bash
ppt-cli add-image deck.pptx 4 \
  --prompt "A minimal flat vector icon of a shield with a checkmark, \
dark blue on white background, clean edges, corporate icon style" \
  --ratio 1:1 --resolution 512 --w 1.5in --h 1.5in --x 1in --y 2in
```

### Before/After or Comparison Images

Generate multiple variants with `--count`:

```bash
ppt-cli image-gen \
  "A modern office workspace, clean and organized, bright natural \
lighting, corporate photography" \
  --ratio 16:9 --resolution 1k --count 3
```

### People and Teams

Avoid uncanny results by specifying camera type and natural context:

```bash
ppt-cli add-image deck.pptx 6 \
  --prompt "A confident business professional giving a presentation to \
a small engaged audience, modern conference room with glass walls, \
DSLR photograph, 85mm lens, shallow depth of field, natural window \
lighting, corporate editorial style" \
  --ratio 16:9 --w 6in --h 3.375in --x 6.5in --y 2in
```

---

## 8. The --reasoning Flag

Add `--reasoning` to any generation command when you need higher quality
results at the cost of speed. This enables the model to plan the image
more carefully before generating. Recommended for:

- Hero images on title slides
- Complex scenes with multiple subjects
- Images with embedded text
- Detailed product mockups

```bash
ppt-cli image-gen \
  "A futuristic smart city at dusk, autonomous vehicles on clean streets, \
glass towers with vertical gardens, warm sunset sky with purple and \
orange tones, wide-angle aerial photograph, cinematic" \
  --ratio 16:9 --resolution 2k --reasoning
```

---

## 9. Prompt Refinement Checklist

Before submitting a prompt, verify you have addressed as many of these as
relevant:

- [ ] **Subject** -- What is the main focus? Be specific about materials,
      colors, and details.
- [ ] **Action/State** -- Is the subject doing something or in a specific
      posture/arrangement?
- [ ] **Setting** -- Where does this take place? Studio, office, outdoors?
- [ ] **Composition** -- How is the shot framed? What angle? Where does the
      subject sit in the frame?
- [ ] **Style** -- Photography or illustration? What genre?
- [ ] **Lighting** -- How is the scene lit? Natural, studio, dramatic?
- [ ] **Camera/Lens** -- What perspective and depth of field?
- [ ] **Color/Mood** -- What color grading or film stock?
- [ ] **Text space** -- Does the slide need room for a title or body text?
      If so, specify negative space.
- [ ] **Aspect ratio** -- Does it match your slide layout? Use `--ratio 16:9`
      for full-bleed backgrounds, `1:1` for spot images.
- [ ] **Resolution** -- Use `2k` for full-slide images, `1k` for medium,
      `512` for thumbnails/icons.

---

## 10. Anti-Patterns to Avoid

- **Keyword soup**: `"business, professional, modern, clean, corporate"` --
  gives the model no structure. Use a full sentence instead.
- **Vague subjects**: `"a nice background"` -- describe what makes it nice
  (gradient direction, color palette, texture).
- **Ignoring composition**: Not specifying framing means the model picks
  arbitrarily. If you need text space on the slide, say so in the prompt.
- **Forgetting aspect ratio**: The default may not match your slide
  dimensions. Always set `--ratio` explicitly for presentation images.
- **Over-prompting**: Cramming every modifier into one prompt creates
  conflicting instructions. Focus on the 3-4 most important dimensions for
  each image.
