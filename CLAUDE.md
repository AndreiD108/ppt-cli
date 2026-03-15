# ppt-cli

CLI tool for inspecting and modifying PowerPoint (`.pptx`) files. Designed for scripting and AI-agent workflows — every command produces JSON output.

```
ppt-cli create deck.pptx
ppt-cli add-slide deck.pptx --layout "Title Slide"
ppt-cli set-title deck.pptx 1 "Hello World"
ppt-cli peek deck.pptx

ppt-cli add-image deck.pptx 1 --prompt "a bar chart of Q1 revenue" --w 8in --h 4.5in
ppt-cli image-gen "a sunset over mountains" --resolution 2k --ratio 16:9
ppt-cli image-gen "product icons" --count 4 -o icons.png

ppt-cli internals stage deck.pptx       # extract .pptx for XML editing
ppt-cli internals analyze deck.pptx     # layout/master/media inventory
ppt-cli internals build <dir> out.pptx  # rebuild from staged directory

ppt-cli template save corp deck.pptx    # save as named template
ppt-cli create new.pptx --template corp # create from template

ppt-cli setup                           # (re-)install the agent skill
```

Run `ppt-cli --help` for the full command list.

AI image generation (`add-image --prompt` and `image-gen`) uses Gemini 3.1 Flash (`gemini-3.1-flash-image-preview`) and requires a `GEMINI_API_KEY` env var.

## Setup

```
make install      # creates .venv, installs deps, installs ppt-cli wrapper
make test         # runs test suite
make clean-cache  # remove /tmp staging dirs and screenshot cache
make uninstall
```

## Project structure

```
ppt-cli/
├── ppt_cli/                # Python package (entry: python3 -m ppt_cli)
│   ├── __init__.py          # __version__ only
│   ├── __main__.py          # venv bootstrap, calls main()
│   ├── cli.py               # argparse setup, imports all cmd_* functions
│   ├── helpers.py           # _die, _parse_length, _parse_color, _open, _get_slide,
│   │                        #   _find_shape, _save + re-exports: Presentation, Inches,
│   │                        #   Pt, Emu, RGBColor
│   ├── serialisation.py     # _emu_to_in, _shape_type_str, _text_frame_to_list,
│   │                        #   _table_to_list, _shape_to_dict, _dump_slide, _peek_slide
│   ├── cmd_create.py        # cmd_create
│   ├── cmd_inspect.py       # cmd_info, cmd_list, cmd_dump, cmd_peek, cmd_screenshot
│   ├── cmd_text.py          # cmd_set_text, cmd_set_title, cmd_set_notes, cmd_replace_text
│   ├── cmd_structure.py     # cmd_add_slide, cmd_delete_slide, cmd_reorder, cmd_duplicate
│   ├── cmd_content.py       # cmd_add_image, cmd_add_textbox, cmd_add_table, cmd_delete_shape
│   ├── cmd_image_gen.py     # cmd_image_gen (standalone AI image generation)
│   ├── image_gen.py         # Google Gemini image generation engine (generate_image, generate_image_name)
│   ├── cmd_style.py         # cmd_set_font, cmd_set_fill, cmd_set_position
│   ├── cmd_internals.py     # stage, analyze, fingerprint, build, build-template,
│   │                        #   delete/duplicate/add for slide/layout/master
│   ├── cmd_template.py      # save, list, show, delete, rename, default
│   ├── staging.py           # staging dir management (hash, extract, resolve)
│   ├── ooxml.py             # low-level OOXML: XML parse/write, .rels CRUD,
│   │                        #   Content_Types CRUD, build, validate, prune
│   ├── template_registry.py # platform-specific template dir, registry.json CRUD
│   └── setup.py             # first-run setup, install.json CRUD, skill hash,
│                            #   _check_setup (pre-command hook), cmd_setup
├── tests/
│   ├── conftest.py          # cli(), tmp_pptx, deck_with_slide, staged_deck,
│   │                        #   cli_with_template_dir
│   ├── test_create.py
│   ├── test_inspect.py
│   ├── test_text.py
│   ├── test_structure.py
│   ├── test_content.py
│   ├── test_image_gen.py
│   ├── test_style.py
│   ├── test_internals_stage.py
│   ├── test_internals_mutate.py
│   ├── test_template.py
│   └── test_setup.py
├── Makefile
└── requirements.txt         # python-pptx, google-genai, Pillow, pytest
```

## Architecture rules

**Flat command modules.** Each `cmd_*.py` holds one group of related commands. No nested `commands/` subpackage. One file per functional area is the right granularity.

**`helpers.py` is the single import point for pptx types.** Command modules do `from .helpers import _open, _save, Inches, Pt` — never `from pptx import ...` directly. This keeps the pptx dependency centralized. (Exception: `ooxml.py` uses `lxml` directly for XML manipulation, and `cmd_internals.py`/`cmd_template.py` import `Presentation` through helpers for reading built files.)

**`serialisation.py` is pure data transformation.** It receives pptx objects as arguments but never opens files or calls `_die`. It has no side effects.

**`cli.py` is argparse only.** It imports `cmd_*` functions, wires them to subparsers via `set_defaults(func=...)`, and calls `args.func(args)`. No business logic lives here.

**`__main__.py` owns the venv bootstrap.** It's the only file that manipulates `sys.path`. The bootstrap adds `.venv/lib/pythonX.Y/site-packages` so the tool works without activating the venv.

## How to add a new command

1. Pick the right `cmd_*.py` or create a new `cmd_foo.py` if it's a new functional area.
2. Write the function: `def cmd_foo(args):` — use helpers from `helpers.py`, serialisation from `serialisation.py`.
3. In `cli.py`: import the function, add a subparser, wire it with `s.set_defaults(func=cmd_foo)`.
4. Add a test in the matching `test_*.py`. Tests are black-box subprocess tests — they call the CLI and assert on stdout/stderr/return code. Use the `cli` fixture from `conftest.py`.
5. Run `make test`.

## Testing philosophy

- **Black-box subprocess tests.** Every test calls the CLI as a subprocess, exactly like a user would. No internal imports in tests.
- **Each test creates its own data.** The `cli("create", ...)` command is the starting point. No shared fixture files.
- **`conftest.py` fixtures:** `cli(tmp_path)` returns a runner function, `tmp_pptx` gives a fresh path, `deck_with_slide` creates a deck with one Title Slide and returns `(path, slide_info)`, `staged_deck` creates and stages a deck, `cli_with_template_dir` provides a CLI runner with an isolated `PPT_CLI_TEMPLATE_DIR`.
- **Test files mirror command modules:** `test_create.py` ↔ `cmd_create.py`, etc.

## Conventions

- All mutation commands print `{"saved": "path", ...}` JSON to stdout.
- Errors go to stderr and exit non-zero via `_die()`.
- Slides are 1-based. Shapes are addressed by `--shape-id` (the integer ID returned by `peek`/`dump`/`add-*`).
- Lengths accept units: `1in`, `72pt`, `2.5cm`, `100px`, `914400emu`. Default is inches.
- Colors are `#RRGGBB` or `RRGGBB`.
- Hidden slides are flagged in `info`, `list`, `dump`, and `peek` output.
- `screenshot` requires LibreOffice; cached PDFs and PNGs go to `/tmp/ppt-cli-screenshots/`.
- **Skill updates require a version bump.** When changing files in `ppt_cli/skill/`, bump `__version__` in `__init__.py`. The first-run system uses version-gating: if the version matches `install.json`, the skill hash is never checked. A version bump triggers the hash comparison, and if SKILL.md changed, a silent auto-update pushes the new skill to installed agents.
