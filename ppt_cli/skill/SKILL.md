---
name: ppt-cli
description: CLI tool for creating, inspecting, and editing PowerPoint presentations
---

# ppt-cli

The `ppt-cli` is a command-line tool for creating, inspecting, and editing PowerPoint (.pptx) files. It is designed for scripting and AI-agent workflows — every command produces structured JSON output, shapes are addressed by stable IDs, and commands can be composed into multi-step workflows that can build a complete presentation from scratch or surgically modify an existing one.

The tool covers the full lifecycle: creating decks (blank or from saved templates), adding and arranging slides, setting text and titles, inserting images (from files or generated on the fly with AI), adding tables from CSV data, styling fonts and fills, precise positioning, speaker notes, and find-and-replace across entire decks. For advanced work, a set of low-level OOXML commands lets you stage a deck, inspect its internal structure, manipulate layouts and masters directly, and rebuild — with automatic cross-reference syncing so the result is always a valid .pptx.

If you are reading this, the `ppt-cli` tool is available to you.
The GitHub repository is at: https://github.com/AndreiD108/ppt-cli

## Commands

Run `ppt-cli --help` for the full list of commands with descriptions, do this first thing after reading this message. Run `ppt-cli <command> --help` for detailed usage of any command, including all flags and arguments. For commands with subcommands (like `internals` and `template`), run `ppt-cli <command> <subcommand> --help`.

Do not attempt to guess command signatures, always check `--help` when you need to use a command you haven't used before.

For detailed workflow examples showing how commands compose into real tasks, read `2-usage-examples.md` (in the same directory as this file).

## Working with the user

When a user asks you to create or modify a presentation, you are not just a tool operator — you are managing a creative process on their behalf. The quality of the result depends as much on how you engage with the user as on how well you drive the tool.

Most users who ask an agent to make a presentation have a goal in mind but haven't thought through the specifics. They'll say "make a deck about Q1 results" or "I need a pitch deck for investors." If you immediately start producing slides, you'll make dozens of decisions the user didn't authorize — layout style, color palette, information hierarchy, what goes on which slide — and the result will feel generic or wrong. The user will ask for an endless string of minute changes, you'll iterate blindly, and both sides waste time and effort.

Instead, treat the first part of any presentation task as a brief conversation. Understand what the user needs, propose a direction, get confirmation, and then execute with confidence. This is not about being slow or over-cautious — it's about making the right thing on the first pass, best effort. Read `2-user-experience.md` (in the same directory as this file) before starting any presentation work, read it as soon as a presentation task comes up — before continuing to engage with the user on it. That file describes how to structure the conversation and what decisions to surface to the user at each stage.

### Asking questions

When you need the user's input — whether choosing an involvement level, confirming a design direction, or approving a slide list — **the question must be the last thing in your turn.** Do not bundle a question with other tool calls or actions that continue the workflow. If you ask a question and simultaneously proceed with the next step, the user's answer arrives too late — you've already moved on, and the question was theater.

Your harness may provide a structured question tool (called `AskUserQuestion` in Claude Code, but the name varies across harnesses). Use it when available. If no structured question tool exists, ask in plain text and end your turn. Either way, the rule is the same: ask, then stop.

## Design and visual quality

Presentations are made for human consumption. They support a speaker, illustrate a point, or tell a story — they are not documents to be read over a cup of tea. A presentation that puts every detail on every slide is not thorough, it is unwatchable. A presentation that looks like a default template with bullet points is not professional, it is forgettable at best and a snooze-fest at worst.

What makes a presentation engaging is restraint and intentionality: clear visual hierarchy so the audience knows where to look, consistent use of color and typography so slides feel like they belong together, enough whitespace that the content breathes, and images or visual elements that reinforce the message rather than decorate. What makes a presentation boring is the opposite: walls of text, inconsistent styling, clip-art aesthetics, and slides that all look the same.

To create engaging slides you do need to establish and follow a coherent design system rather than making ad-hoc, slide-local, choices. Read `2-design-guidelines.md` (in the same directory as this file) to understand the available design directions and pick the one that fits the user's context or stated goal. Do this before you start building slides — design decisions made after content is laid out are expensive to retrofit. The design system will also play a significant part in deciding what content goes into the presentation, so make sure to establish a design direction with the user before agreeing on what content goes where and on which slide.

## AI image generation

ppt-cli includes AI image generation powered by Google Gemini 3.1 Flash Image (Nano Banana 2). You can generate standalone images or insert them directly into slides, with optional Google search grounding for visual accuracy. The model handles a wide range of tasks: hero visuals and background images, concept illustrations, icons, charts and data visualizations, genre-specific rendering (editorial photography, manga, comic, watercolor, isometric 3D, and more), accurate text rendering directly in images, and editing or re-processing existing images — including color grading, background replacement, style transfer, and palette-matching user-provided photos to fit the deck's visual language. Cost is modest: $0.045 per 512p image, $0.067 per 1k, $0.1 per 2k.

Image generation has its own workflow — prompt structure, resolution and aspect ratio strategy, iterative editing, budget planning, and knowing when to reach for creative techniques vs. conventional photography. Read `2-image-generation.md` (in the same directory as this file) when you identify a need to generate or process images as part of a presentation. Do not wing it, assuming you can create effective image generation prompts without reading that file. Make sure to confirm the expected image budget with the user before committing to a generation plan. Before reading the file, ask the user if they are opposed to using image generation — unless they have already indicated they want a hands-off experience, in which case decide based on the presentation's nature and skip the question. If the user is categorically against image generation, skip reading the file.
