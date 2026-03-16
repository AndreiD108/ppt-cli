# Protocol

## Legend

```
!STOP       = sole action this turn; wait for user response
!READ(file) = read file silently before proceeding
!ASK(q)     = ask user (use harness question tool when available); must be last in turn
?cond       = do this only if condition is true
A/K/F       = autopilot / key_decisions / full_control behavior
>>state     = transition to this state next
~infer      = infer from context; don't ask if answer is implied
!TASK(parallel) = launch Task tool sub-agents in parallel
```

## General rules (apply at every state)

```
BUNDLE:   when multiple independent questions arise in the same state,
          bundle into one turn/tool call. Do not split across turns.

INTERACT: describe FEEL not specs. Plain language, no design jargon in
          user-facing messages. Internal vocabulary (motif, half-bleed,
          stat callout) goes in the plan, not in conversation.

OPTIONS:  describe what each option PRODUCES, not what it IS. If the user
          can't tell the difference in the output, don't surface the choice.
          Show > describe — ASCII sketches, hex+name pairs.

INFER:    every question has a cost. If the answer is implied by context,
          state the assumption and move on. The user will correct if wrong.
```

## INTERACTION_STYLE

```
anticipate:       sequence decisions so the user's next concern is addressed
                  before they articulate it. Don't dump info preemptively —
                  order the conversation so each answer flows from the last.
plain_language:   "big numbers front and center" not "stat callout at 60pt".
                  Describe look and feel, not typeface names or hex codes.
infer_not_ask:    "so this is for investors, fairly formal, data-forward" is
                  good. "Who is the audience?" when they already said it is bad.
concrete_options: when presenting choices, describe outcomes. A 3-line ASCII
                  sketch beats a paragraph. Hex+name pairs bridge precise/accessible.
```

---

## ROUTE: task classification

Classify the user's request before entering any state machine:

```
NEW_PRESENTATION  -> >>S0
DECK_ANALYSIS     -> >>A0
DECK_MODIFICATION -> >>M0
TEMPLATE_CREATION -> >>T0
DECK_CONVERSION   -> >>S0 with source_deck set (run A0-A3 first for content)
TEMPLATE_MGMT     -> run commands directly; no protocol needed (see --help)
UNCLEAR           -> ask the user to clarify scope
```

If the request combines types ("analyze then rebuild"), classify as dominant type
(DECK_CONVERSION). Sub-flows compose.

---

## New-Presentation State Machine

### S0: involvement  !STOP

!ASK(involvement: Autopilot / Key Decisions [recommended] / Full Control)

This is a HARD stop. Even if the user's first message makes the level obvious,
ask explicitly. Do not infer involvement level — ~infer does not apply here.
The !STOP annotation overrides all other rules including INFER.

Persists for session. If user's behavior contradicts stated level, adjust silently.

A end-to-end: user sees only slide list approval + image budget confirmation.

>>S1

### S1: understand the ask

Extract (~infer): purpose_audience | source_material (!READ if provided) | constraints
Run `ppt-cli template list` silently; hold results for S2.
?source_deck: source_material = A0-A3 output; !READ analysis results before proceeding.

A: confirm understanding, move on | K: confirm; ?unclear ask | F: follow-up questions

>>S2

### S2: design direction

!READ(design-system.yaml) -- universal section

?template_provided: >>S2t

Propose direction (describe FEEL not specs). Use summaries below to choose and to
give the user accessible vocabulary:

**Business** — Conservative, credible, data-forward. For board decks, investor
updates, internal reports. The audience should leave knowing the numbers and the
narrative without once thinking about the slides. Dark title/conclusion slides
sandwiching light content, muted charts with a single accent highlight, big
numbers with short labels. The design is invisible.

**Technical** — Structured, dense, functional. For architecture reviews, engineering
talks, system documentation. The audience should understand the system and retain the
structure. Dark backgrounds throughout, monospace in the mix, code containers,
numbered step breakdowns, before/after comparisons. Decoration is minimal — structure
does the work.

**Creative** — Expressive, bold, visually assertive. For design showcases, brand
launches, event decks. The audience should remember the feeling before the information.
Full-bleed imagery, asymmetric layouts, confident color, large typography, genre
rendering (editorial, manga, retro poster). The design makes a statement.

**Educational** — Clear, progressive, approachable. For workshops, tutorials, onboarding.
The audience should feel they followed each step and can apply what they learned. Progress
indicators, icon-text rows, callout boxes, numbered steps. Repetitive layout patterns
are fine — consistency aids learning. Higher text density acceptable with clear hierarchy.

A: state choice, no question | K: 2-3 options, 1 recommended | F: present, user decides

?templates_match: surface matching template — "You have a template called `X` — use it
as the base, or start from blank?"

After direction chosen: !READ(design-system.yaml) -- direction-specific section

>>S3

### S2t: template analysis

?template_has_design_system:
  Read `design-system.yaml` from the template directory (`template show <name>` → `design_system_path`).
  Also read layout screenshots from `screenshots/` dir.
  The design system is pre-derived — use it directly. Skip analysis commands.
  >>S3

?template_without_design_system (branded deck or file path):
  Analyze: `internals analyze` | `internals fingerprint` | `peek --all` | `screenshot --all`

  Derive design system (same schema as direction-based):
    palette (roles + hex) | fonts (heading + body) | motif (principle + manifestations) |
    layout_patterns | spacing | bg_strategy

  Record derived system in plan file. Template is the authority — when it consistently
  diverges from universals (e.g., centered body text), follow the template.

  ?incomplete: extend conservatively. Prefer plain-but-consistent over polished-but-foreign.
  ?ambiguous (internal inconsistency): pick dominant pattern (most frequent). Flag at K/F.

>>S3

### S3: image decision

?user_stated_preference: respect it.
?no_preference:
  A: decide based on presentation nature (most decks benefit; data-only reports may not)
  K/F: !ASK(images: yes/no)
?yes: !READ(image-gen.md) silently
?no: skip; do not read image-gen.md

>>S4

### S4: content plan

Determine slide-by-slide content, narrative arc, image placement if images approved.
A: decide silently | K: propose structure, confirm | F: walk through topic by topic

?research_would_help:
  Offer: "I can research [topics] in background — you'll see permission prompts."
  !ASK(research: yes/no)  -- bundle with image_budget if both pending
  ?accepted:
    !TASK(parallel): one sub-agent per topic, background execution.
    Instruct each sub-agent: "This research is for a presentation. Provide a narrative
    overview of [topic] plus the 5-10 highest-signal details that would make strong slides
    — key moments, standout data points, memorable specifics. For each, note any associated
    imagery or visual that would reinforce it. Target ~500 words. Do not write exhaustively;
    write for someone building 5-8 slides, not a report."
    Continue conversation — do not wait.
    When results arrive:
      A: integrate silently, note what changed | K: propose changes | F: present findings
  ?declined: proceed with available material

?images_approved:
  Estimate count + cost from content plan.
  A: state estimate, confirm | K/F: !ASK(image_budget: ~$X for ~N images)

>>S5

### S5a: slide list  !STOP

Present slide list as table:

```
| # | Layout       | Content                                               |
|---|--------------|-------------------------------------------------------|
| 1 | Full-bleed   | "Q1 2026 Results" — dark bg, company logo             |
| 2 | Stat callouts| Three key metrics: revenue, growth, retention         |
| 3 | Two-column   | Product highlights — text left, generated image right |
```

Keep descriptions short, scannable in 15 seconds.

!ASK("Does this look right? If so, I'll go ahead and build it.")

Do NOT enter plan mode or call any tools this turn. Table + question only.

?F or user_requests_walkthrough:
  Walk through slides 1-by-1. For each:

    Render ASCII mockup with actual content (not placeholder labels):
    ```
    ┌─────────────────────────────────────────────┐
    │                                             │
    │   Q1 2026 Results             [logo]        │
    │                                             │
    │   Subtitle text here                        │
    │                                             │
    └─────────────────────────────────────────────┘
    ```

    1-2 sentence description of finished slide.
    "Say next to move on." (conversational, NOT !ASK — keep it flowing)

    ?change_cascades: "This would also affect slides 4, 7, 9 — [how].
      Want me to update those too?" Confirm before registering.

  After all reviewed: >>S6

>>S6

### S6: build and verify

!READ(build-template.sh)

```
ASSERT  build_method = SCRIPT  [scope: NEW_PRESENTATION, DECK_CONVERSION]
        # every ppt-cli command goes through the build script
        # exception: `internals stage` for things scripts can't express
ASSERT  each slide_N() is idempotent
ASSERT  fix_method = edit_script + rerun  [scope: NEW_PRESENTATION, DECK_CONVERSION]
        # NEVER hand-edit XML for scriptable issues
```

**Build:**
  Copy build-template.sh to `/tmp/ppt-cli-build-<deck-name>.sh`.
  Write one `slide_N` function per slide. Build back-to-front: bg -> panels -> text/images.
  Use `shape_id` helper. Use design system from plan for all colors/fonts/positions.
  Write all functions in one pass.
  Execute: `bash /tmp/ppt-cli-build-<deck-name>.sh all`

**QA:**

QA_APPROACH:
  A: auto-verify, full loop, no questions
  K: !ASK — self-verify or user reviews?
  F: !ASK — offer per-slide screenshot walkthrough

QA_CHECKLIST:
```
overlap:     text/text, text/shape, stacked!=side-by-side, image/text
spacing:     edge<0.5in, gap<0.3in, uneven_gaps, near_touch
text:        cutoff, excess_wrap, placeholder_remnants, overflow
alignment:   column_misalign, title_y_varies, content_area_shifts
contrast:    light/light, dark/dark, small_low_contrast, icon_blend
consistency: font_change, palette_violation, partial_styling, monotony
template:    ?template_based: palette_match, font_match, spacing_match, motif_match
```

QA_SCREENSHOTS:
  Prefer !TASK(parallel) sub-agents for image reading — one per image.
  Each sub-agent receives: image path + "Describe what you see in detail —
  layout, text, positioning, spacing, colors, fonts, images, artifacts."
  Do NOT tell sub-agent what the image should contain.
  Compare descriptions against intent. Read image yourself only to confirm discrepancies.

QA_LOOP:
  1. Screenshot all slides.
  2. Catalogue every issue. Do NOT fix as you go.
  3. Fix all issues (edit script functions, re-run affected slides).
  4. Re-screenshot changed slides.
  5. Inspect again — fixes can introduce new problems.
  6. Repeat until a full pass reveals nothing.

QA_MINDSET: your first output is almost never correct. Hunt for bugs, don't seek confirmation.

COMMON_FIXES:
```
overlapping_elements -> recalculate positions; bounding boxes need >= 0.3in clearance
text_overflow        -> reduce text, increase shape height, or split across shapes
inconsistent_margins -> snap to 0.5in boundary; same x/y across slides
placeholder_remnants -> peek all, search for default strings
single_slide_styling -> after establishing style, apply to every slide systematically
edge_touching        -> minimum 0.5in from all edges
large_text_wrapping  -> make text box 15-20% wider; verify with screenshot
```

---

## Deck Analysis (A0-A3)

### A0: structural analysis
`ppt-cli internals analyze <deck>` — layouts used, dead weight, real layouts vs. freehand.
>>A1

### A1: shape-level fingerprinting
`ppt-cli internals fingerprint <deck>` ?specific_slides: `--slide N`
Spots patterns: "slides 5, 11, 23 share same 3-card layout but no real layout exists."
>>A2

### A2: content overview
`ppt-cli peek <deck> --all` ?detail_needed: `ppt-cli dump <deck> <slide_number>`
>>A3

### A3: visual overview
`ppt-cli screenshot <deck> --all`
Sequence matters: structure -> fingerprint -> content -> visual. Do NOT skip ahead.
After A3: answer the user's question using collected data.

---

## Deck Modification (M0-M3)

### M0: understand the change
Extract: which slides, what changes, scope (surgical vs. restyle).
?scope=restyle (>3-4 slides AND design decisions, not just content swaps): >>S1
  (enter new-presentation flow; source_deck = existing deck).
?scope=surgical: >>M1

### M1: inspect affected slides
`ppt-cli dump <deck> <slide_numbers>` + `ppt-cli screenshot <deck> <slide_numbers>`
Understand current state before changing anything.
>>M2

### M2: execute changes
Use ppt-cli commands directly — no build script needed for surgical edits.
?complex_changes (multi-slide): write a small script; use build-template.sh pattern.

Common operations:
  `replace-text deck.pptx "Old" "New"` — bulk find-and-replace across all slides
  `list` / `duplicate-slide` / `reorder --to N` / `delete-slide` — restructure
  `set-font --shape-id N --bold --size 28` / `set-fill` / `set-position` — styling
>>M3

### M3: verify
`ppt-cli screenshot <deck> <changed_slides>`
Compare against intent. Fix if needed.

---

## Template Creation (T0-T2)

### T0: analyze source deck
>>A0 (run the full analysis flow on the source deck)
>>T1

### T1: strip content, keep structure
`ppt-cli internals stage <deck>`
Remove content slides, unused layouts, embedded media.
Keep: masters, layouts, theme, branded elements.
`ppt-cli internals build-template <staged-dir> --name=<name>`
This creates `<name>/template.pptx` + `<name>/screenshots/` in the template dir but does NOT register.
>>T2

### T2: write design system and register

Write `design-system.yaml` in the template directory. Use the template_analysis procedure
from `3-design-template.yaml` to derive palette, typography, motif, layout patterns,
spacing, and background strategy from the source deck analysis (A0-A3 output).

The yaml MUST have:
  - `description:` field (required for validation)
  - References to every PNG in `screenshots/` (filename must appear in yaml text)
  - Derived design system fields: palette, typography, motif, layout_patterns, spacing, bg_strategy

Then: `ppt-cli template save <name>` to validate and register.
>>T3

### T3: verify template
`ppt-cli create /tmp/test-deck.pptx --template <name>`
`ppt-cli template show <name>`
Confirm layouts, masters, and theme survived.

Recipes:
  **Evolve template** — `template show <name>` for path, `internals stage` it,
    edit theme/layout XML, `internals duplicate layout` for variants,
    `internals build-template --name=<name>`, write updated design-system.yaml,
    `template save <name>`.
  **Promote freehand to layout** — fingerprint reveals shared structure,
    `internals add layout <staged-dir> --name "X" --master 1`, edit layout XML
    to add placeholder shapes matching fingerprint.
  **Audit layout fidelity** — `internals analyze` + `internals stage`, read slide
    XMLs alongside layout XMLs. `<p:ph>` = placeholder; no `<p:ph>` = freehand.

---

## Template Management

No protocol needed. Direct commands:
```
ppt-cli template prepare <name> <file>   # create dir, copy pptx, generate screenshots
ppt-cli template save <name>             # validate design-system.yaml + register
ppt-cli template list                    # all templates (shows design-system.yaml path)
ppt-cli template show <name>             # path, description, layouts, design_system_path
ppt-cli template rename <old> <new>      # renames directory
ppt-cli template delete <name>           # remove directory and registry entry
ppt-cli template default                 # print current default
ppt-cli template default <name>          # set default
ppt-cli template default --unset         # clear default
ppt-cli template update-design-system <name> <yaml>  # replace design-system.yaml
```

---

## Glossary (cold-path reference)

Rules where terse encoding above may lose behavioral nuance. Re-read only for
ambiguity resolution, not on every task.

**Turn-boundary rule.** Any question to the user — tagged `!ASK` or not — must be
the last action in the turn. Never bundle a question with tool calls that continue
the workflow. If you ask and simultaneously proceed, the user's answer arrives too
late. Use the harness question tool (`AskUserQuestion` in Claude Code, or equivalent)
when available. If none exists, ask in plain text and end your turn.

**Research mechanics.** Scope is broad — not just factual content. Audience background,
recent news, industry benchmarks, best practices for the presentation type. Offer when
any of these would make the deck more credible or specific. Parallel Task tool calls,
one topic per sub-agent. Each sub-agent should be told the research is for a presentation
and to target ~500 words: narrative overview + 5-10 high-signal details with associated
imagery ideas. Do NOT wait — continue the conversation. Results feed back into the
content plan, not into the build. Integration follows A/K/F. Turn economy: research
offer and image budget are independent; bundle into one question turn when both pending.

**Involvement level contract.** The level set in S0 is a contract. A chose Autopilot:
do not surface "just one more question." F chose Full Control: do not skip decisions
you think are obvious. If the user's behavior contradicts their stated level (Autopilot
user keeps asking to see options), adjust silently to match behavior, not declaration.

**Template authority.** When design system is derived from a template (S2t), the template
is the authority. Universal rules apply only where the template is silent. If the
template consistently centers body text, follow the template — the consistency is
intentional branding, not an error. "Ambiguous" means internal inconsistency within
the template (e.g., two font families for the same role), not divergence from universals.
When extending a template for slide types it lacks, the closest existing layout is a
better starting point than Blank — duplicate and modify.

**QA sub-agents.** Requires harness support for spawning sub-agents (e.g., Claude Code
Task tool). If unavailable, read images directly. QA sub-agents (S6) wait for results;
research sub-agents (S4) do not. The distinction is inline at point of use.

**Build script rationale.** With a script, fixing a slide = edit function + re-run.
Re-running also picks up ppt-cli bug fixes automatically. `internals stage` is for
surgical touch-ups scripts genuinely cannot express (layout XML, theme colors, master
properties). If you are staging XML to fix text alignment or font styling, use the
build script instead.
