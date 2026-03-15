# Writing 3rd-Level Design Direction Files

Guidelines for creating design direction files — the leaf nodes in a skill tree that give an AI agent the aesthetic judgment to build presentations in a specific style. This document captures the philosophy, structural decisions, and reasoning behind the format, so that new directions can be created (or existing ones extended) without losing coherence.

## What a direction file is

A direction file is one of several named design approaches that an agent chooses between (with user input) before building a presentation. It sits at the third level of a skill tree:

```
SKILL.md                    → orientation, pointers
  design-guidelines.md      → universal rules + direction selection (branching node)
    design-business.md      → leaf: full guidance for one direction
    design-technical.md     → leaf: full guidance for one direction
    ...
```

The agent reads the universal rules first (always), then reads one or two direction files based on the user's context. The direction file is where abstract principles become concrete aesthetic choices.

## Relationship to the parent and sibling files

**design-universal.md** contains the principles that hold across every direction: color dominance hierarchy, typography size ladder, layout vocabulary, spacing rules, content structure rules, visual motif theory. Every direction file assumes the agent has already internalized these. Direction files do not repeat universal rules — they build on them.

**design-guidelines.md** (the 2nd-level branching node) contains a short description of each direction — enough for the agent to recommend one to the user without reading all the children first. Each description has two jobs: communicate the concept (audience, purpose, tone, ideal reaction) and give concrete recognizable examples of what a deck in this direction looks like. The description is a paragraph or two, not a section. It does not have its own header for "when to use" — that information is woven into the description naturally.

Direction files are siblings. They should not reference each other, and their content should not assume the agent has read any other direction. Each is self-contained given the universal foundation.

## The nine sections

Every direction file follows the same structural framework. The consistency matters — the agent learns to expect the same sections in the same order, which makes it faster to absorb a new direction.

### 1. Personality statement

A short opening (one to two paragraphs) that captures the vibe of this direction. Not instructions — a description of what a deck in this direction feels like to the audience. This is the aesthetic north star. When the agent faces a judgment call that no specific rule covers, it refers back to this.

Write it as if describing the experience of sitting through a well-executed presentation in this style. What does the audience notice? What do they not notice? What feeling do they leave with?

A common trap: multiple directions can converge on the same high-level claim if you're not careful. "The design should be invisible" could describe business (invisible because trust comes from precision) and technical (invisible because comprehension matters more than aesthetics) — but if both personality statements say "invisible," the agent can't tell them apart. Find the *specific reason* each direction values what it values, and lead with that reason, not the shared surface trait.

### 2. Palette character

Not specific hex codes as mandates, but the *character* of palettes that fit this direction. Open with a concrete grounding metaphor — a real-world reference the agent can picture immediately. "The aesthetic of a premium financial dashboard" or "a well-designed terminal theme" anchors the palette character more effectively than abstract descriptors like "muted and authoritative." Then describe the tendencies: warm vs. cool, muted vs. saturated, dark-leaning vs. light-leaning, monochromatic vs. contrasting. Then provide 2-4 example palettes that illustrate the range within the direction.

The examples are framed as "palettes like these" — they show the kind of thinking, not the answer. Each example should include a brief note on what context it fits (e.g., "works for financial reporting where trust matters more than energy"). The agent should feel equipped to construct a new palette that fits the direction, not just pick from the list.

Include the hex codes in the examples — they are concrete and useful — but make clear they are illustrations.

Each palette example should be a table listing every color role used in practice. The specific roles depend on the direction's background strategy — a direction that uses a dark/light sandwich needs roles for both slide types (dark slide background, dark slide headings, dark slide body, dark slide muted, light slide background, light slide headings, light slide body, light slide muted, accent), while a direction that commits to one background approach needs fewer roles (primary background, secondary/cards, headings, body, muted/captions, accent). Match the role structure to the direction; don't force a universal template. Every palette in a given direction file should use the same role structure for consistency.

Palettes benefit from visual iteration. The set can be previewed by implementing them in a Vue-based HTML preview file (see `ppt_cli/skill/design-palettes-demo/palette-preview-technical.html` for the reference implementation). Open the preview in Chrome, review the colors in context across multiple slide types, and iterate with the user until the palette feels right. This workflow catches contrast and readability issues that are invisible when looking at hex codes in a table.

### 3. Typography

Which font pairings fit this direction's personality. Offer 3-4 options with notes on what each communicates and when to reach for it within the direction. The universal file establishes the size hierarchy (36-44pt titles, 14-16pt body, etc.); the direction file can tighten those ranges if the direction has a preference (e.g., educational might favor the lower end of title sizes because slides carry more text).

Include any direction-specific typography habits. Technical might use monospace in headers. Creative might push title sizes higher than the universal range. Business might always pair a serif header with a sans body. These are the choices that make a direction feel distinct.

### 4. Background strategy

The universal file says "have a background strategy." The direction file says which strategy fits here and why. Options include: all-dark (premium, dramatic), all-light (clean, approachable), contrast sandwich (dark structural slides, light content), warm-tinted (off-white rather than pure white), or committed contrast (alternating dark and light for rhythm).

State the natural fit for this direction, note acceptable alternatives, and flag what doesn't work. A single paragraph is usually enough.

### 5. Layout preferences

The universal file defines the layout vocabulary (two-column, icon+text rows, grid, half-bleed, full-bleed, stat callout, comparison columns, timeline, quote, section divider). The direction file weights them — which patterns this direction reaches for most, which it rarely uses, and how it uses them differently.

This is not about inventing new patterns. It is about saying "in this direction, the signature layouts are X and Y, Z is used sparingly, and W is avoided because it conflicts with the direction's personality." The agent needs to know what to default to and what to save for special occasions.

If a direction has a distinctive way of using a universal pattern (e.g., technical decks might build diagrams from grids of textboxes with connecting accent bars), describe that here.

### 6. Visual motif suggestions

The universal file explains what a motif is (a visual principle, not a single element), the distinction between high-coverage and content-dependent elements, and why a motif matters for cohesion. The direction file gives concrete examples of motifs that match this aesthetic.

Name 2-3 motif principles that fit the direction (e.g., "sharp and geometric" for business, "bold blocks of color" for creative) and describe how each would manifest across different slide types. Include at least one high-coverage element suggestion (something that appears on nearly every slide regardless of content).

### 7. Content density

How much text per slide, how many slides a topic warrants, how to balance text vs. visuals. This varies significantly by direction and is one of the most important practical differences between them.

Educational tolerates more text if well-structured. Creative wants minimal text — spread across more slides rather than cramming. Business is moderate but favors numbers over words. Technical is the densest but demands rigid structural organization to stay readable.

Also address: when to split content across multiple slides vs. keeping it together, how to use speaker notes (some directions lean on them more than others), and what "too much" looks like in this direction.

### 8. Image style

What kind of imagery fits this direction. Photography vs. illustration, realistic vs. abstract, atmospheric vs. functional. When to use AI-generated images vs. shapes and accents. What image style modifiers (from the image-generation doc) align with this direction's aesthetic.

Include guidance on resolution and aspect ratio choices that are typical for this direction's common layouts. Note what to avoid — image styles that would feel out of place in this direction.

### 9. Direction-specific anti-patterns

Things that would be fine in another direction but wrong in this one. Present as a table: the choice, why it fails here, and what to do instead. These are the guardrails that prevent the agent from drifting into a different direction or producing a generic blend.

This section is important for blending. When the agent is combining two directions, the anti-patterns tell it which elements of each direction are load-bearing (must keep) vs. flexible (can swap out). If something is an anti-pattern in direction A but a signature move in direction B, the agent knows that element comes from B, not A.

### Command annex (at the end)

A short section with its own header, introduced by a sentence or two framing it as useful commands that may not be immediately obvious from reading `--help`. Lists only non-obvious workflow patterns — how to achieve specific visual effects that require multi-step command sequences or non-intuitive flag combinations.

Keep it minimal. The agent should discover most commands through `--help`; this annex exists for the handful of patterns where that discovery would be unreliable. Typically 3-5 entries.

## Writing principles

### Specifics as examples, not imperatives

Every concrete choice in a direction file — a palette, a font pairing, a motif — is an example of the kind of decision the agent should make, not the decision itself. If the agent follows a direction file and produces identical output every time regardless of the user's topic, the file is too prescriptive.

Frame specifics with language like "palettes in this range," "pairings like these," "motifs that share this principle." Provide enough examples that the agent understands the boundaries of the direction, but leave room for it to adapt to the specific presentation's subject matter.

### Every "avoid" needs a "because"

When a direction file says to avoid something — a font, a layout pattern, a color choice, an image style — it must explain *why* it fails in this direction. A bare "avoid X" teaches the agent to pattern-match against a list. "Avoid X because it signals Y, which conflicts with this direction's goal of Z" teaches the agent to reason about fonts, layouts, and choices it hasn't seen before. The reasoning is what generalizes; the specific example is just an illustration of it.

### Teach judgment, not syntax

The direction file is about design judgment. It answers "what should this look like and why" — not "which commands to run." Command syntax belongs in `--help`. The command annex at the end is the only exception, and it covers workflow patterns (multi-step sequences), not individual command usage.

### The personality statement anchors everything

When writing a direction file, write the personality statement first. Every subsequent section should feel like a natural consequence of that personality. If the palette section feels disconnected from the personality statement, one of them is wrong.

### Anti-patterns do real work

The anti-pattern section is not a formality. It is what distinguishes this direction from its neighbors. Without it, a business file and an educational file might both produce "clean, professional" output that looks the same. The anti-patterns encode the boundaries — what business does that educational doesn't, and vice versa.

When writing anti-patterns, think about what an agent would do if it confused this direction with another. Those confused choices are the anti-patterns.

### Each direction should feel unmistakably different

If you read the personality statements of all directions back to back, they should sound like different people talking about different goals. If two directions feel similar, either they should be merged or their differentiating characteristics haven't been articulated sharply enough.

The test: could someone read just the personality statement and correctly guess which direction it belongs to? If not, it needs more edge.

## When to create a new direction

Add a new direction when an existing one would require the agent to fight against its own guidance to serve a user's needs. If a user asks for something and the closest direction feels like a poor fit that would need heavy overriding, that gap is a candidate for a new direction.

Do not create directions preemptively for completeness. Each direction is a maintenance commitment — it needs to stay consistent with the universal rules and with the parent file's description. Four well-maintained directions are better than eight with uneven quality.

When adding a new direction:

1. Write the personality statement first and test it against existing directions for distinctiveness.
2. Write a description for the parent file (design-guidelines.md) following the same pattern: concept/context first, then concrete recognizable examples.
3. Build out the nine sections, using existing direction files as structural reference but not copying their content.
4. Review the anti-patterns of existing directions — the new direction might need to appear in their anti-pattern tables, and they might need to appear in the new direction's.
