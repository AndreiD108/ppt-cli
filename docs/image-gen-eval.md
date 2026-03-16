# Image Generation Eval Framework

Comparative test framework for evaluating the effect of the image generation skill file on prompt quality. Guided agents read `ppt_cli/skill/image-gen.md` (core methodology: prompt templates, style vocabulary, traps, workflow patterns, editing operations). Each run produces side-by-side comparisons: guided vs unguided agents.

## Run structure

```
image-gen-tests/
  {run-number}/          # 001, 002, ...
    metadata.json        # skill file hash, timestamp, run config
    prompts.json         # prompts from agents, keyed by image type, guided + unguided
    guided/              # images from agents that read the skill file
      {NN}-{type}_1.png
      {NN}-{type}_2.png
      {NN}-{type}_3.png
    unguided/            # images from agents that did NOT read the skill file
      {NN}-{type}_1.png
      {NN}-{type}_2.png
      {NN}-{type}_3.png
    results.html         # Vue-based comparison page (also embeds prompts)
```

Each image type produces 3 images per side. Each image has its own unique prompt — the agent writes 3 different prompts for the same brief and runs the commands in parallel. This tests prompt diversity and creativity, not just single-prompt quality.

## Test units

Ten agent pairs, each producing guided + unguided output:

| Unit | Types | Images per side | Rationale |
|------|-------|-----------------|-----------|
| 1 | Full-bleed background | 3 | Core slide background use case |
| 2 | Half-bleed image | 3 | Split-layout imagery |
| 3 | Concept + Icon + Chart + Text-in-image | 12 (4 types × 3) | Functional image types grouped |
| 4 | Genre: manga, comic, retro, editorial, flat vector | 15 (5 types × 3) | Creative genre rendering grouped |
| 5 | People/teams photography | 3 | Portrait/team imagery |
| 6 | Consistent asset family (4 icons) | 12 (4 icons × 3) | Visual coherence across a set |
| 7 | Visual cohesion: duotone, color grading, style adaptation | 9 (3 types × 3) | Palette unification of mismatched source photos |
| 8 | Background editing: replacement + removal | 6 (2 types × 3) | Subject isolation and re-contextualization |
| 9 | Character consistency | 3 | Same person across different scenes via reference |
| 10 | Style matching + multi-reference | 6 (2 types × 3) | Reference-driven generation and role specification |

Units 1–6 are generation-only. Units 7–10 use reference images from `image-gen-tests/stock/` (see Stock images below).

Total images per side: 72. Total images per run: 144.

## Stock images

Units 7–10 require source images to use as `--ref` input. These are pre-generated once and stored in `image-gen-tests/stock/`. They are reused across runs — do not regenerate them unless they are missing or you intentionally want to change them.

The images are designed to be useful across different presentation scenarios: a portrait with a busy background (tests background editing and character consistency), a product on a cluttered surface (tests background removal), three photos with clashing color profiles (tests visual cohesion processing), and a strongly styled illustration (tests style matching).

| File | What | Ratio | Used by |
|------|------|-------|---------|
| `portrait.png` | Professional headshot with a busy, cluttered office background. Clear face, upper body framing. | 3:4 | Units 8 (bg replace), 9 (character), 10 (multi-ref) |
| `product.png` | A tech device on a messy desk — cables, coffee mug, sticky notes. The clutter makes removal meaningful. | 1:1 | Unit 8 (bg remove) |
| `photo-event.png` | Conference keynote hall, warm amber stage lighting, slightly oversaturated. Distinct warm color profile. | 16:9 | Unit 7 (duotone) |
| `photo-office.png` | Empty meeting room, cool fluorescent lighting, blue-grey tones. Distinct cool color profile. | 16:9 | Unit 7 (color grading) |
| `photo-street.png` | Busy urban street at midday, harsh shadows, colorful signage. Mixed natural light. | 16:9 | Unit 7 (style adaptation) |
| `style-ref.png` | Isometric 3D illustration — floating island with a miniature office building, trees, a park. Stripe-style premium tech aesthetic. | 16:9 | Unit 10 (style match, multi-ref) |

### Generation commands

```bash
cd image-gen-tests/stock

ppt-cli image-gen "A professional woman in her early 30s standing in a busy open-plan office, colleagues and desks visible behind her, natural overhead lighting mixed with window light, DSLR photograph, 85mm lens, upper body framing, slight confident smile, wearing a dark blazer over a light top" \
  --resolution 1k --ratio 3:4 -o portrait.png

ppt-cli image-gen "A matte black wireless Bluetooth speaker sitting on a cluttered home desk surrounded by tangled cables, a half-empty coffee mug, scattered sticky notes, and a small potted succulent, overhead LED panel lighting, realistic product photography, slightly messy lived-in environment" \
  --resolution 1k --ratio 1:1 -o product.png

ppt-cli image-gen "A tech conference keynote hall seen from mid-audience, rows of seated attendees from behind, a large stage with a presenter and a giant screen showing colorful abstract data graphics, warm amber and orange stage lighting, slightly oversaturated, casual phone camera quality" \
  --resolution 1k --ratio 16:9 -o photo-event.png

ppt-cli image-gen "An empty modern office meeting room with floor-to-ceiling glass walls, a long white table with grey chairs, a whiteboard covered in diagrams and sticky notes, cool fluorescent overhead lighting casting blue-grey tones, no people, smartphone photo quality, flat lighting" \
  --resolution 1k --ratio 16:9 -o photo-office.png

ppt-cli image-gen "A busy urban street scene at midday with pedestrians crossing, colorful shop fronts with neon signs, food stalls with red and yellow awnings, harsh direct sunlight creating strong shadows on the pavement, documentary street photography" \
  --resolution 1k --ratio 16:9 -o photo-street.png

ppt-cli image-gen "An isometric 3D illustration of a small floating island with a miniature modern glass office building, two small trees, a tiny park bench, and a winding path, clean gradients, soft ambient shadows, polished premium tech illustration aesthetic, light grey background" \
  --resolution 1k --ratio 16:9 -o style-ref.png
```

If stock images already exist, skip this step. To verify: `ls image-gen-tests/stock/*.png | wc -l` should return 6.

## Agent configuration

Both agents in each pair receive identical context:

- **Presentation scenario:** a specific fictional presentation with defined subject, audience, and aesthetic direction
- **Image type:** what kind of image, roughly what it depicts, why it fits in the presentation
- **Technical requirements:** resolution (1k for evals), ratio, output paths
- **Command example:** `ppt-cli image-gen "prompt" --resolution 1k --ratio 16:9 -o /path/to/file.png`

Each agent writes 3 different prompts per image type and runs them in parallel. The prompts should vary in approach, composition, or creative interpretation — not just be minor rewrites of the same idea.

The **guided** agent reads one file before crafting prompts:
- `ppt_cli/skill/image-gen.md` — core methodology (prompt templates, style vocabulary, traps, workflow patterns, editing operations)

The **unguided** agent is explicitly told NOT to read any files.

Neither agent receives:
- Specific prompt wording or style vocabulary
- Composition or framing instructions
- Prompt structure formulas

## Execution

- Agents run as `general-purpose` subagents via the Task tool
- Maximum 4 agents in parallel per wave
- No backgrounding — wait for completion before next wave
- Waves are organized so each pair's guided + unguided agents run in the same wave when possible
- **Critical:** Instruct agents to run their ppt-cli commands in parallel using multiple foreground Bash tool calls in a single message. Explicitly tell them "Do NOT background commands with `&` or `run_in_background`." Without this, agents will background the commands, fail to poll results, and retry — wasting tool calls and API budget

## Metadata

`metadata.json` records:

```json
{
  "run": "002",
  "timestamp": "2026-03-14T...",
  "skill_file": "ppt_cli/skill/image-gen.md",
  "skill_file_hash": "sha256:...",
  "stock_images_hash": "sha256:...",
  "resolution": "1k",
  "images_per_type": 3,
  "prompt_mode": "unique_per_image",
  "presentation_scenario": "...",
  "units": [
    {"unit": 1, "types": ["fullbleed"], "ratio": "16:9"},
    ...
    {"unit": 7, "types": ["duotone", "colorgrade", "styleadapt"], "ratio": "16:9", "ref": true},
    ...
  ]
}
```

`stock_images_hash` is a SHA-256 hash of all stock image files concatenated (sorted by filename). This tracks whether the reference inputs changed between runs.

## Prompt capture

Every agent must report the exact prompt it used for each image generation command. Prompts are stored in `prompts.json` and embedded in `results.html`. Since each image has its own unique prompt, prompts are stored as arrays:

```json
{
  "01-fullbleed": {
    "guided": ["prompt for _1", "prompt for _2", "prompt for _3"],
    "unguided": ["prompt for _1", "prompt for _2", "prompt for _3"]
  }
}
```

Agents are instructed to "Report all prompts you used and whether each command succeeded" in their task description. The orchestrator collects these from agent outputs and writes them into the results page data and `prompts.json`.

For grouped agents (e.g. concept+icon+chart+text in one agent), all prompts from that agent must be captured individually.

## Results page

`results.html` is a self-contained Vue app (CDN) that:

- Shows all image pairs side by side in a scrollable grid (guided left, unguided right)
- Groups by unit/type with headers
- Clicking an image opens a carousel lightbox showing the image large with its prompt displayed underneath
- The carousel is navigable with left/right arrow buttons and keyboard arrow keys, cycling through all images in the same row (guided or unguided for that type)
- Scrollable single page, optimized for 2k widescreen
- HTML title includes the run number
- For reference-image types (units 7–10), shows the source/stock image as a thumbnail alongside the guided and unguided outputs so the viewer can judge how well the reference was used

## Running an eval

1. Ensure `GEMINI_API_KEY` is set
2. Verify stock images exist in `image-gen-tests/stock/` — if missing, generate them (see Stock images)
3. Run `image-gen-tests/init-run.sh` — creates the next run directory, writes skeleton `metadata.json`, copies `results.html` from template, seeds empty `prompts.json`
4. Edit `metadata.json` — fill in `presentation_scenario`
5. Edit `results.html` — update scenario name in subtitle, fill in all `EDIT:` section descriptions, update icon group labels and prefixes (13–16)
6. Run agent pairs in waves of 4
7. Collect prompts from agent outputs, write `prompts.json`
8. Serve via HTTP and open in browser (fetch won't work on file:// URLs). Serve from `image-gen-tests/` (not the run directory) so that `../stock/` reference image paths resolve correctly:
   ```
   cd image-gen-tests
   python3 -m http.server 8765 &
   google-chrome http://localhost:8765/{run-number}/results.html
   ```

## Reference files

- **`image-gen-tests/init-run.sh`** — run to create a new eval run directory. Handles numbering, directory structure, hashing, metadata skeleton, and HTML template copy. Prints the new run path.
- **`image-gen-tests/results-template.html`** — the reusable Vue app template. Contains all 24 image types (01–16 generation, 17–24 reference), carousel lightbox, reference image column support, and `EDIT:` markers for scenario-specific content. Placeholders `{{RUN}}` and `{{DATE}}` are substituted by `init-run.sh`.
- **`image-gen-tests/stock/`** — pre-generated reference images for units 7–10 (see Stock images).
- **`image-gen-tests/prompts-reference.json`** — reference for the expected JSON structure (keyed by prefix like `01-fullbleed`, arrays of 3 prompts per side).
- **`ppt_cli/skill/image-gen.md`** — core image generation skill file. Hash before each run.

## Agent prompt templates

**Guided agent (single-type, e.g. fullbleed):**
> You are generating 3 images using ppt-cli for an eval test. Each image must use a DIFFERENT prompt — 3 unique creative interpretations of the same brief.
>
> **FIRST:** Read this file and use what you learn to craft prompts:
> - `/path/to/skill/image-gen.md` — image generation methodology
>
> **Presentation context:** [scenario]
>
> **What to generate:** [image type description]
>
> **Technical:** Resolution 1k, ratio [X:Y]. Save to: [3 paths]
>
> **Command:** `ppt-cli image-gen "prompt" --resolution 1k --ratio X:Y -o /path/to/file.png`
>
> **IMPORTANT: Run all 3 commands in parallel using multiple Bash tool calls in a single message. Do NOT background them with & or run_in_background.**
>
> Report EACH prompt (labeled 1, 2, 3) and whether each succeeded.

**Unguided agent:** Same as above but replace the FIRST instruction with:
> **IMPORTANT: Do NOT read any files. No skill files, docs, or guides. Just use your own knowledge.**

**Grouped agent (e.g. concept+icon+chart+text):** Same pattern but list all types with their ratios and save paths. Instruct to run all commands in parallel.

**Reference-image agent (guided, e.g. duotone, character consistency):**
> You are generating 3 images using ppt-cli for an eval test. Each image must use a DIFFERENT prompt — 3 unique creative interpretations of the same brief.
>
> **FIRST:** Read this file and use what you learn to craft prompts:
> - `/path/to/skill/image-gen.md` — especially the sections on image editing and reference images
>
> **Presentation context:** [scenario]
>
> **Reference image(s):** [paths and what each image contains — e.g. "portrait.png is a professional headshot with a busy office background"]
>
> **What to generate:** [image type description — what to do with the reference]
>
> **Technical:** Resolution 1k, ratio [X:Y]. Save to: [3 paths]
>
> **Command:** `ppt-cli image-gen "prompt" --resolution 1k --ratio X:Y --ref /path/to/stock/image.png -o /path/to/file.png`
>
> **IMPORTANT: Run all 3 commands in parallel using multiple Bash tool calls in a single message. Do NOT background them with & or run_in_background.**
>
> Report EACH prompt (labeled 1, 2, 3) and whether each succeeded.

**Reference-image agent (unguided):** Same as above but replace the FIRST instruction with:
> **IMPORTANT: Do NOT read any files. No skill files, docs, or guides. Just use your own knowledge to write editing/processing prompts.**

## Image type briefs

These are the briefs given to agents. The presentation scenario is constant across all types; only the image-specific description varies.

| # | Prefix | Type | Ratio | Brief (what to tell the agent) |
|---|--------|------|-------|-------------------------------|
| 01 | `01-fullbleed` | Full-bleed background | 16:9 | Opening title slide background. Sets visual tone for deck. Subject evokes the presentation topic. Title text will be overlaid. |
| 02 | `02-halfbleed` | Half-bleed | 3:4 | Fills left half of slide. Right half has text. Close-up showing the product/technology. |
| 03 | `03-concept` | Concept/metaphor | 16:9 | Visual metaphor for a "growth/potential" slide. Concrete scene, not abstract. Organic and aspirational. |
| 04 | `04-icon` | Icon | 1:1 | Small icon for an infographic bullet point. Clean, simple, matches deck palette. |
| 05 | `05-chart` | Chart | 16:9 | Bar chart with specific data (provide values). Dark background, polished, not generic. |
| 06 | `06-text-in-image` | Text-in-image | 16:9 | Section divider with a word rendered into a dramatic background. Text is the visual element. |
| 07 | `07-manga` | Genre: manga | 16:9 | Same core subject rendered as manga. Exaggerated energy, speed lines, motion. |
| 08 | `08-comic` | Genre: comic | 16:9 | Same subject as Western comic. Bold lines, dramatic angles, heroic framing. |
| 09 | `09-retro` | Genre: retro | 16:9 | Same subject as vintage propaganda/travel poster. Bold, graphic, nostalgic. |
| 10 | `10-editorial` | Genre: editorial | 16:9 | Same subject as editorial photography. Magazine-quality, cinematic lighting, shallow DOF. |
| 11 | `11-flatvector` | Genre: flat vector | 16:9 | Same subject as flat vector illustration. Minimal palette, clean lines, simplified. |
| 12 | `12-people` | People/teams | 3:4 | Team portrait in their environment. Confident, approachable. Fills left side of slide. |
| 13-16 | `13-icon-fresh` etc. | Asset family | 1:1 | Set of 4 matching icons (one per benefit). Must look like same visual family. |
| 17 | `17-duotone` | Cohesion: duotone | 16:9 | Process `photo-event.png` into a two-color duotone using the deck's palette. Strip original colors, remap to two theme colors. Result should work as a slide background. **Ref:** `stock/photo-event.png` |
| 18 | `18-colorgrade` | Cohesion: color grading | 16:9 | Apply cinematic color grading to `photo-office.png` to match the deck's mood. Shift color balance to fit the presentation palette without destroying content. **Ref:** `stock/photo-office.png` |
| 19 | `19-styleadapt` | Cohesion: style adaptation | 16:9 | Transform `photo-street.png` into a different visual genre matching the deck aesthetic (e.g. flat vector, watercolor, illustration). Preserve core subject matter. **Ref:** `stock/photo-street.png` |
| 20 | `20-bgreplace` | Background replacement | 3:4 | Replace the busy office background in the portrait with a clean backdrop matching the deck palette — gradient, solid, or themed environment. **Ref:** `stock/portrait.png` |
| 21 | `21-bgremove` | Background removal | 1:1 | Remove the cluttered desk background from the product photo. Isolate on solid white or a deck-colored surface. Clean edges. **Ref:** `stock/product.png` |
| 22 | `22-character` | Character consistency | 16:9 | Place the person from the portrait in 3 different presentation-relevant scenes. Must be recognizably the same individual — face, build, hair. Different context each time. **Ref:** `stock/portrait.png` |
| 23 | `23-stylematch` | Style matching | 16:9 | Generate new subjects in the visual language of the style reference. Match its palette, rendering style, level of detail, and compositional approach. New subject, same aesthetic. **Ref:** `stock/style-ref.png` |
| 24 | `24-multiref` | Multi-reference | 16:9 | Combine two references: portrait is the character, style-ref is the aesthetic. Generate this person rendered in the reference illustration style, placed in a presentation-relevant scene. **Ref:** `stock/portrait.png` + `stock/style-ref.png` |

## Interpreting results

Compare side-by-side for:

- **Compositional intent** — does the image have deliberate framing, negative space, subject placement?
- **Specificity** — are subjects detailed and concrete, or generic?
- **Style coherence** — does the image have a consistent visual register?
- **Presentation fitness** — would this actually work on a slide?
- **Genre accuracy** — for genre tests, does the image convincingly render the requested genre?
- **Set coherence** — for asset families, do the icons look like they belong together?
- **Prompt diversity** — do the 3 prompts per type show meaningfully different approaches, or are they minor variations?

For reference-image types (units 7–10), additionally compare:

- **Source fidelity** — does the output preserve what matters from the reference (face in character tests, product shape in bg removal, subject content in cohesion)?
- **Edit quality** — are edits clean? No artifacts, halos, blurred edges, or color bleed from the original?
- **Role clarity** — in multi-reference tests, did the agent correctly assign roles (face from one, style from another) vs. muddling inputs?
- **Processing intent** — for cohesion types, does the output genuinely match the deck palette, or is it just a vague filter?
