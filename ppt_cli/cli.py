"""Argparse setup and main entry point."""

import argparse

from .cmd_create import cmd_create
from .cmd_inspect import cmd_info, cmd_list, cmd_dump, cmd_peek, cmd_screenshot
from .cmd_text import cmd_set_text, cmd_set_title, cmd_set_notes, cmd_replace_text
from .cmd_structure import cmd_add_slide, cmd_delete_slide, cmd_reorder, cmd_duplicate
from .cmd_content import cmd_add_image, cmd_add_textbox, cmd_add_table, cmd_delete_shape
from .cmd_style import cmd_set_font, cmd_set_fill, cmd_set_position


def main():
    p = argparse.ArgumentParser(
        prog="ppt-cli",
        description="Inspect and modify PowerPoint (.pptx) presentations.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""\
workflow:
  ppt-cli create deck.pptx [--widescreen]
    → {"created":"deck.pptx", "layouts":["Title Slide","Blank",...]}

  ppt-cli add-slide deck.pptx --layout "Title Slide"
    → {"saved":"deck.pptx", "slide":1, "layout":"Title Slide",
       "shapes":[{"id":2,"name":"Title 1","type":"placeholder"},
                 {"id":3,"name":"Subtitle 2","type":"placeholder"}]}

  ppt-cli set-text deck.pptx 1 --shape-id 2 "Hello World"
  ppt-cli add-textbox deck.pptx 1 "Body text" --x 1in --y 3in --w 8in
    → {"saved":"deck.pptx", "shape_id":4, "name":"TextBox 1"}

  ppt-cli peek deck.pptx          # compact overview of all slides
    → slide 1: Hello World  [Title Slide]  (2 shapes)
        id=2  placeholder  Title 1  "Hello World"
        id=3  placeholder  Subtitle 2  "Some subtitle"
  ppt-cli dump deck.pptx 1       # full JSON when you need positions/styles

addressing:  slides are 1-based numbers, shapes are targeted by --shape-id
             (returned by add-*/peek/dump). Use peek for quick overview, dump for details.
units:       1in, 2.5cm, 72pt, 100px, 914400emu (default: inches)
output:      all commands produce JSON. Mutation commands return created IDs.
""",
    )
    sub = p.add_subparsers(dest="command", required=True)

    # ── create ──
    s = sub.add_parser("create", help="Create a new empty .pptx file")
    s.add_argument("file")
    s.add_argument("--width", help="Slide width (e.g. 10in)")
    s.add_argument("--height", help="Slide height (e.g. 7.5in)")
    s.add_argument("--widescreen", action="store_true", help="Use 16:9 widescreen (13.333x7.5in)")
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
    s.add_argument("slide", nargs="?", type=int)
    s.add_argument("--all", action="store_true", help="Dump all slides")
    s.set_defaults(func=cmd_dump)

    # ── peek ──
    s = sub.add_parser("peek", help="Compact summary: shape IDs, types, and text preview")
    s.add_argument("file")
    s.add_argument("slide", nargs="?", type=int)
    s.add_argument("--all", action="store_true", help="Peek all slides (default if no slide given)")
    s.set_defaults(func=cmd_peek)

    # ── screenshot ──
    s = sub.add_parser("screenshot", help="Render slide as PNG (requires libreoffice)")
    s.add_argument("file")
    s.add_argument("slide", type=int)
    s.add_argument("output", nargs="?", help="Output PNG path (default: slide_N.png)")
    s.add_argument("--dpi", type=int, help="Resolution (default 150)")
    s.set_defaults(func=cmd_screenshot)

    # ── set-text ──
    s = sub.add_parser("set-text", help="Set text on a shape (use \\\\n for newlines)")
    s.add_argument("file")
    s.add_argument("slide", type=int)
    s.add_argument("--shape-id", type=int, required=True)
    s.add_argument("text")
    s.add_argument("-o", "--output", help="Save to different file")
    s.set_defaults(func=cmd_set_text)

    # ── set-title ──
    s = sub.add_parser("set-title", help="Set slide title text")
    s.add_argument("file")
    s.add_argument("slide", type=int)
    s.add_argument("text")
    s.add_argument("-o", "--output")
    s.set_defaults(func=cmd_set_title)

    # ── set-notes ──
    s = sub.add_parser("set-notes", help="Set speaker notes")
    s.add_argument("file")
    s.add_argument("slide", type=int)
    s.add_argument("text")
    s.add_argument("-o", "--output")
    s.set_defaults(func=cmd_set_notes)

    # ── replace-text ──
    s = sub.add_parser("replace-text", help="Find and replace text across all slides")
    s.add_argument("file")
    s.add_argument("old", help="Text to find")
    s.add_argument("new", help="Replacement text")
    s.add_argument("-o", "--output")
    s.set_defaults(func=cmd_replace_text)

    # ── add-slide ──
    s = sub.add_parser("add-slide", help="Add a new slide")
    s.add_argument("file")
    s.add_argument("--layout", help="Layout name or index (default: first)")
    s.add_argument("--at", type=int, help="Insert at this position (1-based)")
    s.add_argument("-o", "--output")
    s.set_defaults(func=cmd_add_slide)

    # ── delete-slide ──
    s = sub.add_parser("delete-slide", help="Delete a slide")
    s.add_argument("file")
    s.add_argument("slide", type=int)
    s.add_argument("-o", "--output")
    s.set_defaults(func=cmd_delete_slide)

    # ── reorder ──
    s = sub.add_parser("reorder", help="Move a slide to a new position")
    s.add_argument("file")
    s.add_argument("slide", type=int, help="Slide to move (1-based)")
    s.add_argument("--to", type=int, required=True, help="Target position (1-based)")
    s.add_argument("-o", "--output")
    s.set_defaults(func=cmd_reorder)

    # ── duplicate-slide ──
    s = sub.add_parser("duplicate-slide", help="Duplicate a slide")
    s.add_argument("file")
    s.add_argument("slide", type=int)
    s.add_argument("-o", "--output")
    s.set_defaults(func=cmd_duplicate)

    # ── add-image ──
    s = sub.add_parser("add-image", help="Add an image to a slide")
    s.add_argument("file")
    s.add_argument("slide", type=int)
    s.add_argument("image", help="Path to image file")
    s.add_argument("--x", help="Left position (e.g. 1in)")
    s.add_argument("--y", help="Top position")
    s.add_argument("--w", help="Width")
    s.add_argument("--h", help="Height")
    s.add_argument("-o", "--output")
    s.set_defaults(func=cmd_add_image)

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
    s.add_argument("-o", "--output")
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
    s.add_argument("-o", "--output")
    s.set_defaults(func=cmd_add_table)

    # ── delete-shape ──
    s = sub.add_parser("delete-shape", help="Delete a shape from a slide")
    s.add_argument("file")
    s.add_argument("slide", type=int)
    s.add_argument("--shape-id", type=int, required=True)
    s.add_argument("-o", "--output")
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
    s.add_argument("-o", "--output")
    s.set_defaults(func=cmd_set_font)

    # ── set-fill ──
    s = sub.add_parser("set-fill", help="Set shape fill color")
    s.add_argument("file")
    s.add_argument("slide", type=int)
    s.add_argument("--shape-id", type=int, required=True)
    s.add_argument("--color", required=True, help="Fill color (#RRGGBB)")
    s.add_argument("-o", "--output")
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
    s.add_argument("-o", "--output")
    s.set_defaults(func=cmd_set_position)

    args = p.parse_args()
    args.func(args)
