# ppt-cli

CLI tool for inspecting and modifying PowerPoint (`.pptx`) files. Designed for scripting and AI-agent workflows — every command produces JSON output.

```
ppt-cli create deck.pptx
ppt-cli add-slide deck.pptx --layout "Title Slide"
ppt-cli set-title deck.pptx 1 "Hello World"
ppt-cli peek deck.pptx
```

Run `ppt-cli --help` for the full command list.

## Setup

```
make install   # creates .venv, installs deps, installs ppt-cli wrapper
make test      # runs test suite
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
│   │                        #   Pt, Emu, RGBColor, PP_ALIGN
│   ├── serialisation.py     # _emu_to_in, _shape_type_str, _text_frame_to_list,
│   │                        #   _table_to_list, _shape_to_dict, _dump_slide, _peek_slide
│   ├── cmd_create.py        # cmd_create
│   ├── cmd_inspect.py       # cmd_info, cmd_list, cmd_dump, cmd_peek, cmd_screenshot
│   ├── cmd_text.py          # cmd_set_text, cmd_set_title, cmd_set_notes, cmd_replace_text
│   ├── cmd_structure.py     # cmd_add_slide, cmd_delete_slide, cmd_reorder, cmd_duplicate
│   ├── cmd_content.py       # cmd_add_image, cmd_add_textbox, cmd_add_table, cmd_delete_shape
│   └── cmd_style.py         # cmd_set_font, cmd_set_fill, cmd_set_position
├── tests/
│   ├── conftest.py          # cli() fixture (subprocess), tmp_pptx, deck_with_slide
│   ├── test_create.py
│   ├── test_inspect.py
│   ├── test_text.py
│   ├── test_structure.py
│   ├── test_content.py
│   └── test_style.py
├── Makefile
└── requirements.txt         # python-pptx, pytest
```

## Architecture rules

**Flat command modules.** Each `cmd_*.py` holds one group of related commands. No nested `commands/` subpackage. One file per functional area is the right granularity.

**`helpers.py` is the single import point for pptx types.** Command modules do `from .helpers import _open, _save, Inches, Pt` — never `from pptx import ...` directly. This keeps the pptx dependency centralized.

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
- **`conftest.py` fixtures:** `cli(tmp_path)` returns a runner function, `tmp_pptx` gives a fresh path, `deck_with_slide` creates a deck with one Title Slide and returns `(path, slide_info)`.
- **Test files mirror command modules:** `test_create.py` ↔ `cmd_create.py`, etc.

## Conventions

- All mutation commands print `{"saved": "path", ...}` JSON to stdout.
- Errors go to stderr and exit non-zero via `_die()`.
- Slides are 1-based. Shapes are addressed by `--shape-id` (the integer ID returned by `peek`/`dump`/`add-*`).
- Lengths accept units: `1in`, `72pt`, `2.5cm`, `100px`, `914400emu`. Default is inches.
- Colors are `#RRGGBB` or `RRGGBB`.
