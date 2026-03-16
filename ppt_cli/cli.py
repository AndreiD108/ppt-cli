"""Argparse setup and main entry point."""

import argparse

import sys

from .setup import _check_setup, _read_install_json, cmd_setup
from .cmd_create import cmd_create
from .cmd_inspect import cmd_info, cmd_list, cmd_dump, cmd_peek, cmd_screenshot
from .cmd_text import cmd_set_text, cmd_set_title, cmd_set_notes, cmd_replace_text
from .cmd_structure import cmd_add_slide, cmd_delete_slide, cmd_reorder, cmd_duplicate
from .cmd_content import cmd_add_image, cmd_add_textbox, cmd_add_table, cmd_delete_shape
from .cmd_image_gen import cmd_image_gen
from .cmd_style import cmd_set_font, cmd_set_fill, cmd_set_position
from .cmd_internals import (
    cmd_stage, cmd_analyze, cmd_fingerprint, cmd_build, cmd_build_template,
    cmd_delete_slide_internal, cmd_delete_layout, cmd_delete_master,
    cmd_duplicate_slide_internal, cmd_duplicate_layout, cmd_duplicate_master,
    cmd_add_layout,
)
from .cmd_template import (
    cmd_template_save, cmd_template_list, cmd_template_show,
    cmd_template_delete, cmd_template_rename, cmd_template_default,
)


def main():
    _epilog = """\
quick start:
  ppt-cli create deck.pptx && ppt-cli add-slide deck.pptx --layout "Title Slide"
  ppt-cli set-title deck.pptx 1 "Hello" && ppt-cli peek deck.pptx

addressing:  slides, masters, and layouts are 1-based. Shapes use --shape-id.
units:       1in, 2.5cm, 72pt, 100px, 914400emu (default: inches).
output:      all commands produce JSON.
cleanup:     delete temporary files and screenshots when you're done with them.
"""
    _install_data = _read_install_json()
    if _install_data and not _install_data.get("skill_installed"):
        _epilog += "tip:         run 'ppt-cli setup' to install the agent skill.\n"

    p = argparse.ArgumentParser(
        prog="ppt-cli",
        description="Inspect and modify PowerPoint (.pptx) presentations.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=_epilog,
    )
    sub = p.add_subparsers(dest="command", required=True)

    # ── create ──
    s = sub.add_parser("create", help="Create a new empty .pptx file")
    s.add_argument("file")
    s.add_argument("--width", help="Slide width (e.g. 10in)")
    s.add_argument("--height", help="Slide height (e.g. 7.5in)")
    s.add_argument("--legacy", action="store_true", help="Use 4:3 legacy aspect ratio (10x7.5in) instead of default 16:9")
    s.add_argument("--template", help="Template name or .pptx path")
    s.add_argument("--force", action="store_true", help="Overwrite existing file")
    s.set_defaults(func=cmd_create)

    # ── info ──
    s = sub.add_parser("info", help="Deck metadata (slides, dimensions, layouts)")
    s.add_argument("file")
    s.set_defaults(func=cmd_info)

    # ── list ──
    s = sub.add_parser("list", help="List slides with titles and shape counts")
    s.add_argument("file")
    s.set_defaults(func=cmd_list)

    # ── dump ──
    s = sub.add_parser("dump", help="Full JSON dump of slide(s) (see also: peek)",
                       description="Full structured JSON dump of slide shapes, positions, "
                       "text, and styles. For a compact overview with shape IDs and text "
                       "previews, use 'ppt-cli peek' instead.")
    s.add_argument("file")
    s.add_argument("slides", nargs="*", type=int, help="Slide number(s) (e.g. 1, or 1 3 5)")
    s.add_argument("--all", action="store_true", help="Dump all slides")
    s.set_defaults(func=cmd_dump)

    # ── peek ──
    s = sub.add_parser("peek", help="Compact summary: shape IDs, types, and text preview")
    s.add_argument("file")
    s.add_argument("slides", nargs="*", type=int, help="Slide number(s) (e.g. 1, or 1 3 5)")
    s.add_argument("--all", action="store_true", help="Peek all slides (default if no slide given)")
    s.set_defaults(func=cmd_peek)

    # ── screenshot ──
    s = sub.add_parser("screenshot", help="Render slide(s) as PNG (requires libreoffice)",
                       epilog="Note: first call on a file is slow (10+ seconds on a 50+ slide deck) "
                              "because libreoffice converts the entire deck to PDF. Subsequent calls "
                              "use the cached PDF and are near-instant.")
    s.add_argument("file")
    s.add_argument("slides", type=int, nargs="*", help="Slide number(s) (e.g. 1, or 1 3 5)")
    s.add_argument("--all", action="store_true", help="Render all slides")
    s.add_argument("-o", "--output", help="Output path (default: /tmp/ppt-cli-screenshots/<hash>-slides/slide_<number>.png)")
    s.add_argument("--dpi", type=int, help="Resolution (default 150)")
    s.set_defaults(func=cmd_screenshot)

    # ── set-text ──
    s = sub.add_parser("set-text", help="Set text on a shape (use \\\\n for newlines)")
    s.add_argument("file")
    s.add_argument("slide", type=int)
    s.add_argument("--shape-id", type=int, required=True)
    s.add_argument("text")
    s.add_argument("-o", "--output", help="Save to a new file instead of overwriting the input")
    s.set_defaults(func=cmd_set_text)

    # ── set-title ──
    s = sub.add_parser("set-title", help="Set slide title text")
    s.add_argument("file")
    s.add_argument("slide", type=int)
    s.add_argument("text")
    s.add_argument("-o", "--output", help="Save to a new file instead of overwriting the input")
    s.set_defaults(func=cmd_set_title)

    # ── set-notes ──
    s = sub.add_parser("set-notes", help="Set speaker notes")
    s.add_argument("file")
    s.add_argument("slide", type=int)
    s.add_argument("text")
    s.add_argument("-o", "--output", help="Save to a new file instead of overwriting the input")
    s.set_defaults(func=cmd_set_notes)

    # ── replace-text ──
    s = sub.add_parser("replace-text", help="Find and replace text across all slides")
    s.add_argument("file")
    s.add_argument("old", help="Text to find")
    s.add_argument("new", help="Replacement text")
    s.add_argument("-o", "--output", help="Save to a new file instead of overwriting the input")
    s.set_defaults(func=cmd_replace_text)

    # ── add-slide ──
    s = sub.add_parser("add-slide", help="Add a new slide")
    s.add_argument("file")
    s.add_argument("--layout", help="Layout name or index (default: first)")
    s.add_argument("--at", type=int, help="Insert at this position (1-based)")
    s.add_argument("-o", "--output", help="Save to a new file instead of overwriting the input")
    s.set_defaults(func=cmd_add_slide)

    # ── delete-slide ──
    s = sub.add_parser("delete-slide", help="Delete a slide")
    s.add_argument("file")
    s.add_argument("slide", type=int)
    s.add_argument("-o", "--output", help="Save to a new file instead of overwriting the input")
    s.set_defaults(func=cmd_delete_slide)

    # ── reorder ──
    s = sub.add_parser("reorder", help="Move a slide to a new position")
    s.add_argument("file")
    s.add_argument("slide", type=int, help="Slide to move (1-based)")
    s.add_argument("--to", type=int, required=True, help="Target position (1-based)")
    s.add_argument("-o", "--output", help="Save to a new file instead of overwriting the input")
    s.set_defaults(func=cmd_reorder)

    # ── duplicate-slide ──
    s = sub.add_parser("duplicate-slide", help="Duplicate a slide")
    s.add_argument("file")
    s.add_argument("slide", type=int)
    s.add_argument("-o", "--output", help="Save to a new file instead of overwriting the input")
    s.set_defaults(func=cmd_duplicate)

    # ── add-image ──
    s = sub.add_parser(
        "add-image",
        help="Add an image to a slide (from file or AI-generated)",
        description="Insert an image into a slide. Provide a local file path, "
        "or use --prompt to generate one with AI (requires GEMINI_API_KEY env var). "
        "--w/--h control the shape size on the slide regardless of image source.",
    )
    s.add_argument("file")
    s.add_argument("slide", type=int)
    s.add_argument("image", nargs="?", default=None,
                   help="Path to image file (omit when using --prompt)")
    s.add_argument("--prompt",
                   help="Generate image with AI from this description (requires GEMINI_API_KEY env var)")
    s.add_argument("--resolution", choices=["512", "1k", "2k"], default="1k",
                   help="Generated image pixel resolution (default: 1k). Only with --prompt")
    s.add_argument("--ratio",
                   help="Aspect ratio for generation (e.g. 16:9). Auto-guessed from --w/--h if both given. Only with --prompt")
    s.add_argument("--grounding", choices=["search", "image", "full"], default=None,
                   help="Ground generation with web search (search), image search (image), or both (full). Only with --prompt")
    s.add_argument("--reasoning", action="store_true",
                   help="Enable model reasoning for better results (slower). Only with --prompt")
    s.add_argument("--ref", nargs="+", metavar="IMAGE",
                   help="Reference image(s) for editing, style transfer, or compositing "
                        "(max 14). Files can be referenced by name in the prompt. Only with --prompt")
    s.add_argument("--x", help="Left position (e.g. 1in)")
    s.add_argument("--y", help="Top position")
    s.add_argument("--w", help="Width of the shape on the slide (e.g. 8in)")
    s.add_argument("--h", help="Height of the shape on the slide (e.g. 4.5in)")
    s.add_argument("-o", "--output", help="Save to a new file instead of overwriting the input")
    s.set_defaults(func=cmd_add_image)

    # ── image-gen ──
    s = sub.add_parser("image-gen",
                       help="Generate images with AI (requires GEMINI_API_KEY)")
    s.add_argument("prompt", help="Text description of the image to generate")
    s.add_argument("--resolution", choices=["512", "1k", "2k"], default="1k",
                   help="Pixel resolution (default: 1k)")
    s.add_argument("--ratio",
                   help="Aspect ratio (e.g. 16:9, 1:1)")
    s.add_argument("--grounding", choices=["search", "image", "full"], default=None,
                   help="Ground generation with web search (search), image search (image), or both (full)")
    s.add_argument("--reasoning", action="store_true",
                   help="Enable model reasoning for better results (slower)")
    s.add_argument("--ref", nargs="+", metavar="IMAGE",
                   help="Reference image(s) for editing, style transfer, or compositing "
                        "(max 14). Files can be referenced by name in the prompt")
    s.add_argument("--count", type=int, default=1,
                   help="Number of images to generate (in parallel)")
    s.add_argument("-o", "--output",
                   help="Output path (default: /tmp/ppt-cli/image-gen/{name}.png). "
                        "With --count N: appends _1, _2, etc. before extension")
    s.set_defaults(func=cmd_image_gen)

    # ── add-textbox ──
    s = sub.add_parser("add-textbox", help="Add a textbox to a slide")
    s.add_argument("file")
    s.add_argument("slide", type=int)
    s.add_argument("text")
    s.add_argument("--x", help="Left position (e.g. 1in)")
    s.add_argument("--y", help="Top position")
    s.add_argument("--w", help="Width")
    s.add_argument("--h", help="Height")
    s.add_argument("--font-size", type=float, help="Font size in points")
    s.add_argument("--font-color", help="Font color (#RRGGBB)")
    s.add_argument("--bold", action="store_true")
    s.add_argument("-o", "--output", help="Save to a new file instead of overwriting the input")
    s.set_defaults(func=cmd_add_textbox)

    # ── add-table ──
    s = sub.add_parser("add-table", help="Add a table from a CSV file")
    s.add_argument("file")
    s.add_argument("slide", type=int)
    s.add_argument("csv", help="Path to CSV file")
    s.add_argument("--x", help="Left position")
    s.add_argument("--y", help="Top position")
    s.add_argument("--w", help="Table width")
    s.add_argument("--h", help="Table height")
    s.add_argument("-o", "--output", help="Save to a new file instead of overwriting the input")
    s.set_defaults(func=cmd_add_table)

    # ── delete-shape ──
    s = sub.add_parser("delete-shape", help="Delete a shape from a slide")
    s.add_argument("file")
    s.add_argument("slide", type=int)
    s.add_argument("--shape-id", type=int, required=True)
    s.add_argument("-o", "--output", help="Save to a new file instead of overwriting the input")
    s.set_defaults(func=cmd_delete_shape)

    # ── set-font ──
    s = sub.add_parser("set-font", help="Set font properties on a shape")
    s.add_argument("file")
    s.add_argument("slide", type=int)
    s.add_argument("--shape-id", type=int, required=True)
    s.add_argument("--bold", action="store_true", default=None)
    s.add_argument("--no-bold", dest="bold", action="store_false")
    s.add_argument("--italic", action="store_true", default=None)
    s.add_argument("--no-italic", dest="italic", action="store_false")
    s.add_argument("--size", type=float, help="Font size in points")
    s.add_argument("--color", help="Font color (#RRGGBB)")
    s.add_argument("--name", help="Font family name")
    s.add_argument("-o", "--output", help="Save to a new file instead of overwriting the input")
    s.set_defaults(func=cmd_set_font)

    # ── set-fill ──
    s = sub.add_parser("set-fill", help="Set shape fill color")
    s.add_argument("file")
    s.add_argument("slide", type=int)
    s.add_argument("--shape-id", type=int, required=True)
    s.add_argument("--color", required=True, help="Fill color (#RRGGBB)")
    s.add_argument("-o", "--output", help="Save to a new file instead of overwriting the input")
    s.set_defaults(func=cmd_set_fill)

    # ── set-position ──
    s = sub.add_parser("set-position", help="Move or resize a shape")
    s.add_argument("file")
    s.add_argument("slide", type=int)
    s.add_argument("--shape-id", type=int, required=True)
    s.add_argument("--x", help="Left position")
    s.add_argument("--y", help="Top position")
    s.add_argument("--w", help="Width")
    s.add_argument("--h", help="Height")
    s.add_argument("-o", "--output", help="Save to a new file instead of overwriting the input")
    s.set_defaults(func=cmd_set_position)

    # ── internals ──
    s_int = sub.add_parser(
        "internals",
        help="Low-level OOXML operations (stage, build, analyze, mutate)",
        description="Extract a .pptx, inspect/edit the underlying XML, and rebuild. "
        "Single-file XML edits can be done directly on staged files; multi-file "
        "operations (delete/duplicate/add) that require cross-reference syncing "
        "are provided as subcommands.",
    )
    int_sub = s_int.add_subparsers(dest="internals_command", required=True)

    # internals stage
    s = int_sub.add_parser("stage", help="Extract a .pptx into a staging directory")
    s.add_argument("file")
    s.set_defaults(func=cmd_stage)

    # internals analyze
    s = int_sub.add_parser("analyze", help="Analyze layouts, masters, media, and usage")
    s.add_argument("file")
    s.add_argument("--json", action="store_true", help="Output as JSON")
    s.set_defaults(func=cmd_analyze)

    # internals fingerprint
    s = int_sub.add_parser("fingerprint", help="Shape-level fingerprint of slides")
    s.add_argument("file")
    s.add_argument("--slide", type=int, help="Specific slide number")
    s.add_argument("--json", action="store_true", help="Output as JSON")
    s.set_defaults(func=cmd_fingerprint)

    # internals build
    s = int_sub.add_parser("build", help="Rebuild a .pptx from a staged directory")
    s.add_argument("staged_dir")
    s.add_argument("output")
    s.add_argument("--clean", action="store_true", help="Prune unused layouts and media before building")
    s.set_defaults(func=cmd_build)

    # internals build-template
    s = int_sub.add_parser("build-template", help="Build and register a template from a staged directory")
    s.add_argument("staged_dir")
    s.add_argument("--name", required=True, help="Template name (kebab-case)")
    s.add_argument("--description", help="Template description")
    s.add_argument("-f", "--force", action="store_true", help="Overwrite existing template")
    s.set_defaults(func=cmd_build_template)

    # internals delete
    s_del = int_sub.add_parser("delete", help="Delete a slide, layout, or master")
    del_sub = s_del.add_subparsers(dest="delete_target", required=True)

    s = del_sub.add_parser("slide", help="Delete a slide")
    s.add_argument("file")
    s.add_argument("--slide", type=int, required=True)
    s.set_defaults(func=cmd_delete_slide_internal)

    s = del_sub.add_parser("layout", help="Delete a layout")
    s.add_argument("file")
    s.add_argument("--layout", required=True, help="Layout name")
    s.add_argument("--master", type=int, help="Master number (disambiguate)")
    s.set_defaults(func=cmd_delete_layout)

    s = del_sub.add_parser("master", help="Delete a slide master")
    s.add_argument("file")
    s.add_argument("--master", type=int, required=True)
    s.set_defaults(func=cmd_delete_master)

    # internals duplicate
    s_dup = int_sub.add_parser("duplicate", help="Duplicate a slide, layout, or master")
    dup_sub = s_dup.add_subparsers(dest="duplicate_target", required=True)

    s = dup_sub.add_parser("slide", help="Duplicate a slide")
    s.add_argument("file")
    s.add_argument("--slide", type=int, required=True)
    s.set_defaults(func=cmd_duplicate_slide_internal)

    s = dup_sub.add_parser("layout", help="Duplicate a layout")
    s.add_argument("file")
    s.add_argument("--source", required=True, help="Source layout name")
    s.add_argument("--name", required=True, help="New layout name")
    s.add_argument("--master", type=int, help="Master number (disambiguate)")
    s.set_defaults(func=cmd_duplicate_layout)

    s = dup_sub.add_parser("master", help="Duplicate a slide master")
    s.add_argument("file")
    s.add_argument("--master", type=int, required=True)
    s.add_argument("--name", required=True, help="New master name")
    s.set_defaults(func=cmd_duplicate_master)

    # internals add
    s_add = int_sub.add_parser("add", help="Add a new layout")
    add_sub = s_add.add_subparsers(dest="add_target", required=True)

    s = add_sub.add_parser("layout", help="Add a new blank layout")
    s.add_argument("file")
    s.add_argument("--name", required=True, help="Layout name")
    s.add_argument("--master", type=int, required=True, help="Master number")
    s.set_defaults(func=cmd_add_layout)

    # ── template ──
    s_tmpl = sub.add_parser(
        "template",
        help="Manage saved .pptx templates for reuse with 'create --template'",
        description="Save, list, and manage named .pptx templates. Templates are "
        "complete .pptx files stored in a platform-specific directory. Use "
        "'ppt-cli internals' to extract and edit template XML directly.",
    )
    tmpl_sub = s_tmpl.add_subparsers(dest="template_command", required=True)

    # template save
    s = tmpl_sub.add_parser("save", help="Save a .pptx as a named template")
    s.add_argument("name", help="Template name (kebab-case)")
    s.add_argument("file", help="Source .pptx file")
    s.add_argument("--description", help="Template description")
    s.add_argument("-f", "--force", action="store_true", help="Overwrite existing")
    s.set_defaults(func=cmd_template_save)

    # template list
    s = tmpl_sub.add_parser("list", help="List saved templates")
    s.add_argument("--json", action="store_true", help="Output as JSON")
    s.set_defaults(func=cmd_template_list)

    # template show
    s = tmpl_sub.add_parser("show", help="Show template details")
    s.add_argument("name")
    s.set_defaults(func=cmd_template_show)

    # template delete
    s = tmpl_sub.add_parser("delete", help="Delete a saved template")
    s.add_argument("name")
    s.set_defaults(func=cmd_template_delete)

    # template rename
    s = tmpl_sub.add_parser("rename", help="Rename a template")
    s.add_argument("old", help="Current name")
    s.add_argument("new", help="New name")
    s.add_argument("--description", help="New description")
    s.set_defaults(func=cmd_template_rename)

    # template default
    s = tmpl_sub.add_parser("default", help="Get/set the default template")
    s.add_argument("name", nargs="?", help="Template name to set as default")
    s.add_argument("--unset", action="store_true", help="Clear the default")
    s.set_defaults(func=cmd_template_default)

    # ── setup (hidden from --help in non-TTY contexts) ──
    _setup_help = "Re-run agent skill installation" if sys.stdin.isatty() else argparse.SUPPRESS
    s = sub.add_parser("setup", help=_setup_help)
    s.set_defaults(func=cmd_setup)

    args = p.parse_args()
    _check_setup(args.command)
    args.func(args)
