# Skill File System Guide

How the skill files in `ppt_cli/skill/` are structured, why they work the way they do, and how to expand them without breaking the patterns.

## Format choices

**YAML for structured design data.** Palettes, typography specs, layout preferences, anti-pattern lists — anything an agent looks up by key during execution. The design system hub and all direction files use YAML.

**Markdown for procedural knowledge.** Protocols, workflows, prompt patterns, speaker note rules — anything that must be read sequentially to absorb judgment or follow a procedure. The entry point, protocol, image generation guide, and speaker notes file use Markdown.

The split is functional. YAML suits key-value lookup ("what is the accent color?"). Markdown suits sequential reasoning ("how do I structure a QA loop?"). If new content is primarily lookup data, use YAML. If it teaches a process or exercises judgment, use Markdown.

## Progressive disclosure

The system is designed so an agent never reads all files. The loading tree:

1. `SKILL.md` — always loaded first (the installed skill entry point)
2. `protocol.md` — always loaded next ("read before starting any task")
3. `design-system.yaml` — universal section loaded during direction selection
4. One `3-design-{direction}.yaml` — loaded after the user picks a direction
5. `image-gen.md` — loaded only if the task involves images
6. `speaker-notes.md` and `build-template.sh` — loaded at build time

A business presentation without images loads: SKILL.md, protocol.md, design-system.yaml (universal), 3-design-business.yaml, speaker-notes.md, build-template.sh. It never touches image-gen.md or any other direction file. This is critical for context window management — the total system is large, but any single task loads only its relevant subset.

Every new file must fit into this tree with a clear "when to load" trigger. No file should be required reading for all tasks unless it is SKILL.md or protocol.md.

## File naming

Files use numeric prefixes to encode their depth in the loading tree:

- No prefix: entry point (`SKILL.md`), shared infrastructure (`design-system.yaml`, `build-template.sh`), and general reference (`protocol.md`, `image-gen.md`, `speaker-notes.md`)
- Prefix `3-`: third-level leaf nodes loaded conditionally (`3-design-business.yaml`, `3-design-template.yaml`)

The scheme accommodates future levels. A `4-` prefix could represent sub-directions or specialized extensions without restructuring existing files.

## Cross-referencing

Files reference each other exclusively by filename, never by path. `SKILL.md` says "Read protocol.md", not "./protocol.md" or an absolute path. This works because all skill files live in one flat directory. No subdirectories except `design-palettes-demo/` (which holds user-facing HTML previews, not agent-readable skill content).

The `design-system.yaml` hub uses a `file:` key to point to direction-specific files and a `palette_preview:` key for the HTML demos.

## YAML conventions

### Key naming and structure

Keys use `snake_case`. Single-word keys where possible. Nesting is shallow — typically 2-3 levels deep. Deep nesting taxes an LLM's ability to track context.

Flow-style YAML for compact color maps: `{ bg: "#282828", cards: "#3C3836", head: "#EBDBB2" }`. One line carries all color roles for a variant.

### Comments carry behavioral nuance

The design system file explicitly states: "Comments carry behavioral nuance and are as important as the keyed values." The YAML is read by an LLM, not parsed by a YAML engine, so comments serve as inline reasoning. Annotation patterns:

- `# OVERRIDE:` — replaces a universal value
- `# ADD:` — appends to a universal list
- `# INHERIT` — section header reminder that universals apply unchanged

### Inheritance model

`design-system.yaml` establishes universal rules. Each direction YAML states only overrides and additions. Direction files never repeat universal rules — they build on them. Anti-patterns in direction files add to (never remove from) the universal list.

### Palette role structure

Color roles within palette examples vary by direction because different directions have different structural needs:

- Directions using a dark/light contrast sandwich need roles for both slide types (bg, head, body, muted in both dark and light variants)
- Directions with a uniform background approach need fewer roles (bg, secondary/cards, head, body, muted)

Match the role structure to the direction's background strategy. Every palette within a given direction file uses the same role structure for consistency.

### Direction file sections

Every direction YAML follows a consistent section framework. The consistency matters — the agent learns to expect the same sections in the same order. The standard sections:

1. **Character** — the aesthetic personality (a description, not instructions)
2. **Palette** — palette character plus named examples with hex codes
3. **Typography** — font pairing overrides, size overrides
4. **Background** — background strategy override
5. **Layout** — primary/sparingly/avoid layout preferences
6. **Motif** — direction-specific motif principles
7. **Density** — content density overrides
8. **Image style** — imagery guidance, style modifiers, avoids
9. **Anti-patterns** — direction-specific additions to the universal list

Not all sections override universals. Some may be absent when universals apply unchanged, signaled by an `# INHERIT` comment in context.

### Template analysis (3-design-template.yaml)

This file is structurally different from direction files. It defines a procedure for deriving a design system from an existing deck, not a design specification. It contains `method:` and `output:` blocks for each extraction step. It is loaded when a user provides an existing template instead of choosing a direction.

## Markdown conventions

### Protocol (protocol.md)

Uses a state machine encoding: states named `Sn:` with annotations (`!STOP`, `!READ(file)`, `!ASK(q)`), conditional branches (`?condition:`), involvement branches (`A: ... | K: ... | F: ...`), and transitions (`>>Sn`). A legend at the top defines the pseudo-code notation. The pattern repeats identically for every state.

Heading hierarchy: `##` for major sections, `###` for individual states.

### Reference files (image-gen.md, speaker-notes.md)

More prose-heavy because they teach judgment, not procedure. Key patterns:

- Code blocks for structured definitions (prompt skeletons, timing tables, cue notation)
- `TRAP:` / `FIX:` pairs for anti-patterns
- Concrete examples positioned immediately after the skeleton they illustrate
- Lookup tables for vocabulary and style anchors

### build-template.sh

Dual role: a pattern library (comment blocks with `@pattern name (direction-affinity)` tags) and a runnable build script template. The pattern names become vocabulary used in the protocol's slide planning table. The executable portion provides a `slide_N()` function structure with idempotent rebuilds.

## Data density guidelines

Density varies by file role:

- **YAML design files** (~90% structure / 10% prose in comments): extremely dense. Terse labels, flow-style maps, abbreviations in comments. A single direction file under 200 lines covers palette, typography, background, layout, motif, density, image style, and anti-patterns.
- **Protocol markdown** (~70% structure / 30% prose): state machine encoding with domain-specific shorthand compresses behavioral branches into single lines.
- **Reference markdown** (~40% structure / 60% prose): more verbose because judgment content requires absorption, not lookup.

New files should match the density of whichever category they belong to. YAML additions should aim for the same information-per-line ratio as existing direction files. New markdown procedures should use the protocol's notation system. New reference material can be more verbose.

## Expanding the system

### Adding a new design direction

1. Create `3-design-{name}.yaml` following the standard section framework
2. Use the same YAML conventions: flow-style color maps, `# OVERRIDE:` / `# ADD:` / `# INHERIT` annotations, terse comments
3. Add an entry in `design-system.yaml` under `directions:` with prose description, `file:` pointer, and `palette_preview:` pointer
4. Create a matching `design-palettes-demo/palette-preview-{name}.html`
5. Update `protocol.md` S2 to include the new direction's summary

### Adding a new protocol state or procedure

1. Add states following the existing notation (state name, annotations, directives, A/K/F branches, transitions)
2. Wire the new states into the existing state graph with `>>` transitions
3. If the procedure needs a new file, add a `!READ(filename)` directive at the appropriate state

### Adding new build patterns to build-template.sh

1. Add the pattern as a comment block in the pattern library section
2. Use the `@pattern name (direction-affinity)` naming convention
3. Include exact ppt-cli commands with placeholder variables
4. Note direction affinity parenthetically but don't restrict usage

### Adding a new standalone reference file

1. Name it descriptively without numeric prefix (it goes in the flat skill directory)
2. Add `!READ(filename)` directives in `protocol.md` at the appropriate state
3. Follow the code-block-for-structure, prose-for-judgment pattern
4. Reference it from SKILL.md's "When a task comes in" section if it represents a top-level capability

### General rules

- Files in the skill directory are flat — no subdirectories except `design-palettes-demo/`
- Cross-references by filename only, never by path
- The progressive loading tree must be maintained — every file has a "when to load" trigger
- Comments in YAML carry equal weight to keyed values
- Direction files state only what they change from universal
- If SKILL.md content changes, bump `__version__` in `__init__.py` to trigger redistribution

## design-palettes-demo/

Contains one HTML file per design direction — self-contained Vue 3 apps that render interactive palette previews. Each file defines mock slide renderings using direction-specific slide types (business shows metrics/comparison, technical shows architecture/code, etc.). These are user-facing visualization tools surfaced during design direction discussion, not read by agents at build time.

When adding a new direction, create a matching preview HTML following the existing files as structural reference.
