---
name: ppt-cli
description: CLI tool for creating, inspecting, and editing PowerPoint presentations
---

# ppt-cli

`ppt-cli` is a command-line tool for creating, inspecting, and editing PowerPoint (.pptx) files. Every command produces structured JSON output, shapes are addressed by stable IDs, and commands compose into multi-step workflows — from building a complete presentation from scratch to surgically modifying an existing one.

The tool covers the full lifecycle: creating decks (blank or from saved templates), adding and arranging slides, setting text and titles, inserting images (from files or AI-generated via Gemini), adding tables, styling fonts and fills, precise positioning, speaker notes, and find-and-replace. Low-level OOXML commands let you stage a deck, inspect its internals, manipulate layouts and masters, and rebuild with automatic cross-reference syncing.

If you are reading this, `ppt-cli` is available to you. The GitHub repository is at: https://github.com/AndreiD108/ppt-cli

## Getting started

Run `ppt-cli --help` for the full command list. Run `ppt-cli <command> --help` for detailed usage of any command. For subcommand groups (`internals`, `template`), run `ppt-cli <command> <subcommand> --help`. Do not guess command signatures — always check `--help` first. I repeat, DO NOT GUESS command or subcommand signatures, get `--help`.

## When a task comes in

Read `protocol.md` (in the same directory as this file) before starting any presentation, analysis, modification, or template task. It defines the interaction workflow, task routing, design direction selection, build process, and QA procedures. Read it as soon as a relevant task comes up — before continuing to engage with the user.

For command composition patterns and reusable build recipes, see the `@pattern` blocks in `build-template.sh`. These cover common slide constructions (dark backgrounds, stat callouts, code containers, accent bars, etc.) and are useful reference for any task involving ppt-cli commands.

AI image generation (`add-image --prompt` and `image-gen`) uses Gemini and requires a `GEMINI_API_KEY` env var. The image generation workflow, prompt patterns, and budget planning are covered in `image-gen.md`, read when the protocol directs you to.

Speaker notes (verbatim presentation scripts) are covered in `speaker-notes.md`, read during S6 build. Every presentation gets a script baked into the deck via `set-notes`.
