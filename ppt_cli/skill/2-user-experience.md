# User Experience

## Scope

The step-by-step flow in this file applies to **creating a new presentation** — the most common and most complex interaction pattern. It does not apply to every task a user might ask for with ppt-cli.

Other common tasks include: creating a template from an existing deck, analyzing or answering questions about a deck, modifying specific slides in an existing presentation, converting one deck into another, and template management. Some of these have workflows hinted at in CLI help pages; others you will have to shape on the spot based on the user's goal. When the user's goal is not "build me a new presentation," do not follow the steps below — but draw on the general principles at the end of this file, which apply regardless of task.

---

## Goal

The goal is an experience where the user feels like they're working with a skilled collaborator who has already thought three steps ahead. Every question should feel like it arrives at exactly the right moment — not too early (overwhelming), not too late (requiring rework). The user's next concern should be addressed before they articulate it. When there is an obvious single path forward, take it and move on. When there is a genuine choice, present 2-3 options with one clearly marked as recommended, described in plain language — no design jargon the user would need a dropdown menu to decode.

This file defines the interaction flow, not the design rules or the build mechanics — those live in `2-design-guidelines.md` and `2-behavior.md` respectively.

---

## Step 0: Involvement level

Before anything else, ask the user how involved they want to be in the planning process. This is the single most important question because it determines the density of every subsequent interaction.

Three levels:

1. **Autopilot** — "I'm leaving all decisions to you." The agent makes every design, content, and layout choice. The user sees only the final slide list for approval before building.
2. **Key decisions** — "I'll weigh in on the important stuff." The agent makes routine choices silently and surfaces only decisions where the outcome meaningfully changes — design direction, content scope, image strategy, slide structure. This is the recommended default.
3. **Full control** — "I want to decide everything." The agent presents options at every decision point. Nothing is decided without explicit user approval.

Present these three levels using your harness's question tool (AskUserQuestion in Claude Code, or equivalent — if no structured question tool is available, ask in plain text and end your turn). Mark "Key decisions" as recommended. The user's choice persists for the entire session. If the user's behavior during the conversation contradicts their stated level (e.g., they picked Autopilot but keep asking to see options), adjust silently — match what they are doing, not what they said.

**This must be the only action in this turn.** Do not ask about content, start reading files, or call any other tools alongside the involvement question. Wait for the user's response before proceeding to Step 1.

**What Autopilot looks like end-to-end:** The user states what they want. The agent confirms its understanding, chooses a direction, plans the content, and presents a slide list table. The only questions the user sees are: involvement level (this step), image budget confirmation (if applicable), and the slide list approval. Everything else is decided silently.

---

## Step 1: Understand the ask

Before proposing anything, understand what the user needs. Most users arrive with a goal and some material but haven't thought through the specifics. Your job is to extract what they have and fill in what they haven't considered.

What to establish:

- **Purpose and audience.** What is the presentation for? Who will see it? A quarterly report for the board, a pitch deck for investors, a workshop for new hires — the answer narrows design direction, content density, and tone in one stroke. Often the user's first sentence tells you this. If it does, confirm the inference rather than asking again.
- **Source material.** Does the user have content — documents, data, bullet points, an outline, an existing deck? If so, read it before continuing. The material shapes everything downstream.
- **Constraints.** Slide count limits, branding requirements, time limits for the talk, mandatory content. Surface these early because they bound every subsequent decision.
- **Existing templates.** Run `ppt-cli template list` silently. If templates exist that match the likely direction, hold this information for Step 2 where it becomes a concrete option.

For Autopilot users, this step is a single exchange: the user states what they want, you confirm your understanding and move on. For Full Control users, you may ask follow-up questions to clarify ambiguities. For Key Decisions users, confirm your read of the situation and ask only if something is genuinely unclear.

---

## Step 2: Design direction

Read `2-design-guidelines.md` and `3-design-universal.md` before this step. You need to have internalized the available directions and the universal design rules before proposing anything to the user.

Based on what you learned in Step 1, recommend a design direction. Present it in plain, accessible language — describe what the deck will *feel like*, not what typeface it uses. "Clean, structured, data-focused — dark title slides, light content slides, big numbers for key metrics" is accessible. "Georgia headers with a navy/teal palette at 60/20/10 dominance" is not.

Always present 2-3 options with one recommended, unless the context so obviously points to a single direction that offering alternatives would feel patronizing (e.g., a board-level quarterly report is Business, full stop — just confirm it).

If `ppt-cli template list` returned templates that match the recommended direction, surface them here: "You have a template called `quarterly` that fits this direction — want to use it as the base, or start from a blank deck?" This is a natural decision point and avoids the user discovering the template later and wondering why it wasn't offered.

For Autopilot users, state the direction you've chosen and why, briefly. No question. Move on.

After the direction is established, read the corresponding `3-design-*.md` file for that direction. Do this silently — the user does not need to know about the internal file structure.

---

## Step 3: Image decision

Before planning content, establish whether the deck will use AI-generated images. This comes first because it affects slide layouts, content density, and what kinds of slides are available — a deck with images and a deck without images are planned differently.

If the user has not expressed a preference, ask whether they want AI-generated images in the deck. If they are categorically against it, note the decision and do not read `2-image-generation.md`. If they agree, read `2-image-generation.md` silently for the mechanics and prompt patterns.

For Autopilot users, decide based on the presentation's nature — most decks benefit from images, so default to yes unless the context suggests otherwise (e.g., a purely data-driven internal report). Do not ask. The budget confirmation comes later, in Step 4, once the content plan makes the cost concrete.

---

## Step 4: Content plan

Determine what goes on which slides, in what order. This is where the presentation takes shape as a narrative — not just a collection of topics, but a sequence with a beginning, middle, and end.

Work from the user's source material if they provided any. If they didn't, propose a content structure based on the purpose and audience. The output of this step is a mental model of what each slide covers and roughly how — not exact text, but the role each slide plays. If images were accepted in Step 3, the content plan should include where images appear and what they depict.

Decisions in this step follow the involvement level:

- **Autopilot:** You decide the content structure. No questions.
- **Key Decisions:** Propose the structure and ask for confirmation. Surface choices only where the content could reasonably go multiple ways — e.g., "Should the competitive analysis come before or after the product demo section?"
- **Full Control:** Walk through the structure topic by topic, offering options for ordering, grouping, and emphasis.

If images are part of the plan, estimate the count and cost now that the content makes it concrete. Surface this to the user: "This plan uses about 6-8 generated images — roughly $0.50-0.70 total. Good to go?" For Autopilot users, state the estimated image cost and confirm — this is the one image-related question they see.

**Turn economy:** This step may involve multiple questions (content structure, image budget, research offer). If your harness supports multi-question tool calls (e.g., AskUserQuestion with multiple questions in Claude Code), bundle independent questions into one call rather than splitting them across turns. The image budget depends on the content plan, so it cannot be asked in the same turn as the content structure — but the research offer and the image budget can be bundled once the content is confirmed.

### Research

Once the content scope is known, assess whether brief online research would improve the result. This applies broadly — not just to factual content, but to anything where current, specific, or domain-expert information would make the deck more credible or compelling. Examples:

- Latest data or statistics on the presentation's subject
- Background on the audience or organization
- Recent news relevant to the topic
- Industry benchmarks or competitive landscape
- Best practices for the specific type of presentation

If you identify topics where research would help, offer it to the user: "I can do some quick research on [topics] to make the content more specific and current. This will launch a few background searches — you'll see some permission prompts come through. Want me to go ahead?"

If the user agrees, launch research agents in parallel using the Task tool. Instruct each agent to produce a brief summary (a few paragraphs, not an essay). Do not wait for results — continue the conversation. When results arrive, assess whether they suggest changes to the content plan. If so, propose the changes to the user according to their involvement level — Autopilot users get a brief note of what changed and why, Key Decisions users get a choice, Full Control users see the findings and decide. If the user declines research, proceed with what you have.

---

## Step 5: Slide list approval

This is the last checkpoint before building. It happens in two phases with a hard turn boundary between them.

### Step 5a: Present the slide list

Output a concise slide summary as a message. Use a table format:

```
| # | Layout | Content |
|---|--------|---------|
| 1 | Full-bleed title | "Q1 2026 Results" — dark background, company logo |
| 2 | Stat callouts | Three key metrics: revenue, growth, retention |
| 3 | Two-column | Product highlights — text left, generated image right |
| ...| ... | ... |
```

Keep descriptions short and in plain language. The user should be able to scan this in 15 seconds and know whether the deck is on track.

Then ask: "Does this look right? If so, I'll go ahead and build it."

**Stop here. Do not enter plan mode, do not call any tools in this turn.** Output the table, ask the question, and wait for the user's response. The slide list is the user's last chance to reshape the presentation before the full build plan is written — do not skip it.

### Step 5b: Write the build plan

After the user approves (and after incorporating any requested changes), enter plan mode. Plan mode will present instructions oriented toward code implementation (explore agents, plan agents, phased workflows) — disregard all of that and write the presentation build plan directly to the plan file.

The plan is a design document, not a build script. It describes **what** each slide looks like and **why**, not the ppt-cli commands to build it. Do not include shell commands, command syntax, shape IDs, or implementation details — those belong in the build script, which is generated later during execution (Step 6).

#### Plan file structure

The plan must contain these sections in order:

**1. Design system.** The palette (role → hex → usage), fonts (heading, body), margins, gaps, visual motif (recurring design elements like accent bars or content panels), and the shared image style fragment if images are used. This section is the source of truth for every visual decision — the build script will reference it.

**2. Deck file.** The absolute path to the output `.pptx` file.

**3. Slides.** One subsection per slide. Each slide description includes:
- Slide number and title (e.g., "Slide 3: Class Identity")
- Layout type in plain language (e.g., "image fills left half, content panel on right"). If the slide uses a pre-made layout from the deck's template (rather than a custom layout built from shapes on a Blank slide), name the layout explicitly — e.g., "uses layout: Title Slide" — so the build script knows to use that layout's placeholders instead of adding shapes from scratch.
- Content: what text appears, what it says, how it's styled relative to the design system (e.g., "title in heading font, accent color" — not "Impact 36pt #D4A843")
- Image description: if the slide has a generated image, describe what it depicts and its placement. Include the full image prompt — these are creative decisions, not implementation details.
- Speaker notes content, if any.

Keep slide descriptions focused on creative intent. Positions, sizes, and exact font sizes are derived from the design system and layout type during execution — they do not need to be specified per-shape in the plan unless a slide deliberately deviates from the standard layout.

**4. Session context.** See "Plan footer" below.

#### If the user wants to review individual slides

Before entering plan mode, walk through slides one at a time. For each slide:

- Render an ASCII mockup showing the approximate layout — where text blocks sit, where images go, how the space is divided. Use actual content (summarized or hinted at) in the mockup, not placeholder labels.
- Describe what the finished slide will look like in one or two sentences.
- End with a low-friction cue: "If this looks good, say `next` to move on."

Do not use AskUserQuestion for individual slide review. The interaction should feel conversational, not transactional. The user says `next`, or they say what they want changed.

**When a change cascades:** If the user requests a change that would affect other slides (e.g., a style change, moving content from one slide to another, reordering sections), flag it before making it: "This would also affect slides 4, 7, and 9 — [brief description of how]. Want me to update those too?" Confirm before registering the change in the plan.

After all slides are reviewed, enter plan mode and write the build plan.

### Plan footer

The last section in the plan file must be a session context block. This ensures the agent can resume correctly if conversation context is compacted between planning and execution — which is common, since the plan is often approved with "clear context."

```
---
Session context (for post-compaction recovery):
- Involvement level: [Autopilot / Key Decisions / Full Control]
- Image budget: [approved/declined, estimated cost]
- QA approach: [see below]
- Design files read during planning: [list the 3-design-*.md files that were read]

Recovery steps — do these FIRST if conversation context was compacted:
1. Load the ppt-cli skill.
2. Read 2-usage-examples.md (for command composition patterns).
3. Read the design files listed above.
4. Re-read this plan file (important — it is the primary context for execution).
5. Generate the build script and execute it.
6. After building, read 2-behavior.md (for QA procedures) and run verification.
```

**QA approach by involvement level:**
- **Autopilot:** "Run full verification loop automatically after building. Do not ask."
- **Key Decisions:** "Ask the user before starting QA whether they want self-verification or prefer to review themselves."
- **Full Control:** "Ask the user, and offer to walk through each slide's screenshot together."

Include the appropriate line in the session context block based on the involvement level chosen in Step 0.

---

## Step 6: Build and verify

### The build script is mandatory

**Every presentation MUST be built through a build script.** Do not issue ppt-cli commands directly one at a time. Do not skip the script because it "feels faster" to run commands inline. The script is not an optional convenience — it is the build artifact that makes everything downstream work: QA fixes, tool upgrades, user-requested changes, and full rebuilds.

Without a script, every fix becomes bespoke hand-editing — staging XML, patching properties manually, rebuilding from raw OOXML. With a script, fixing a slide is: edit the function, re-run `bash build.sh 3`. If a ppt-cli bug is fixed or a default is improved between the initial build and QA, re-running the script picks up those improvements automatically across every slide. Running commands by hand throws away this capability entirely.

(`internals stage` is the right tool for surgical touch-ups that build commands genuinely cannot express — editing layout XML, theme colors, master slide properties. But if you find yourself staging XML to fix something the build commands handle, like text alignment or font styling, that is a signal you should have used a build script — not a signal to keep going by hand.)

### Prepare

Read `2-usage-examples.md` (in the same directory as this file) before writing the build script. It shows how ppt-cli commands compose in practice — command patterns, flag combinations, and workflows that are not obvious from `--help` alone.

### Generate the build script

Translate the plan into a build script. A template script lives at `build-template.sh` (in the same directory as this file). Copy it to `/tmp/ppt-cli-build-<deck-name>.sh` and fill in the slide functions. Read the template source — it includes helpers and patterns you should understand before writing your slide functions:

- `PPTX` and `TEMPLATE` variables (deck path and optional template name)
- Automatic deck creation if the file doesn't exist, and slide provisioning using a `LAYOUTS` map (defaults to Blank for slides without an explicit layout)
- A `shape_id` helper that captures the shape ID from ppt-cli JSON output
- An example `slide_1` function demonstrating the pattern, including idempotency (safe to re-run)
- A dispatcher that runs all slides or specific ones by number (`bash build.sh all`, `bash build.sh 3 7 12`)

Write the complete script in one pass — one `slide_N` function per slide. Each function must be idempotent: safe to re-run on a slide that already has content. The template explains the two patterns for this (Blank-layout slides vs. template-layout slides with placeholders). Build content back-to-front: background first, then panels, then text and images on top. Use the design system from the plan for all colors, fonts, positions, and sizes. Use `shape_id` to capture IDs for subsequent `set-font`/`set-fill` calls.

Writing all commands in one pass eliminates the thinking overhead between individual commands and cuts build time dramatically.

### Execute

Run the build script: `bash /tmp/ppt-cli-build-<deck-name>.sh all`. This builds all slides in one pass.

### Verify

Read `2-behavior.md` (in the same directory as this file) for the full verification loop and checklist. Then follow the QA approach recorded in the plan's session context block:

- **Autopilot:** Run the full verification loop from `2-behavior.md` automatically. Do not ask.
- **Key Decisions:** Ask the user whether they want you to self-verify and iterate, or prefer to review the output themselves.
- **Full Control:** Ask, and offer to walk through each slide's screenshot together.

**Rebuilding slides:** If the verification loop or user feedback identifies issues, update the relevant slide functions in the build script and re-run just those slides (`bash build.sh 3 7`). Because each function is idempotent (it cleans up before rebuilding), re-running replaces the slide's content cleanly. Fix the function, re-run, re-verify. Never fix issues by hand-editing XML or running ad-hoc commands outside the script — update the script and re-run it, so the fix is permanent and reproducible.

---

## General principles

These apply throughout the conversation, not to any specific step.

### Anticipate, don't interrogate

The best interaction is one where the user's next question is answered before they ask it. This does not mean dumping information preemptively — it means sequencing decisions so that each answer flows naturally from the last, and the user never has to wonder "why is it asking me this now?"

When the user's intent is clear from context, confirm the inference and move on. Do not ask questions the user already answered, even implicitly. "Make me a pitch deck for Series A investors" already tells you the audience, the purpose, the formality level, and the likely design direction. Confirming "so this is for investors, fairly formal, data-forward — I'd go with a clean business style" is good. Asking "who is the audience?" is tedious.

### Plain language, always

The user is not a designer. Terms like "60/20/10 dominance hierarchy," "visual motif," "half-bleed layout," and "stat callout" are internal vocabulary — use them in the plan, not in conversation with the user. Instead: "big numbers front and center," "an image filling half the slide," "a consistent visual thread tying the slides together."

When describing font choices, color palettes, or layout patterns, describe what they *look and feel like*, not their technical names. The user doesn't need to know it's Calibri — they need to know the text will look clean and modern.

### Don't ask what you can infer

Every question has a cost: it interrupts the user's flow, demands cognitive effort, and risks making the experience feel like a form. Before asking a question, check whether the answer is already implied by what the user said, by the context, or by common sense. If it is, state your assumption and move on. If you're wrong, the user will correct you — and that correction is less friction than the question would have been.

### Options are concrete

When presenting options, describe what each one *produces*, not what it *is* in the abstract. Do not present options that differ only in terminology — if the user can't tell the difference in the output, the choice is meaningless and should not be surfaced.

Where possible, show rather than describe. A three-line ASCII sketch of a slide layout communicates more than a paragraph describing it. A hex color shown next to a plain-language description ("deep navy — #1B2A4A") bridges the gap between accessible and precise.

### Respect the user's time

The involvement level set in Step 0 is a contract. If the user chose Autopilot, do not second-guess by surfacing "just one more question." If they chose Full Control, do not skip decisions you think are obvious — obvious to you is not obvious to everyone.

The fastest path through the conversation is not the one with the fewest questions — it is the one where every question earns its place and no answer is wasted. A single well-timed question that resolves three downstream decisions is worth more than skipping all three and getting one wrong.
