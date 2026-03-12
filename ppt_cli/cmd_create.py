"""Create command."""

import json
import os

from .helpers import _die, _parse_length, Presentation, Inches
from .serialisation import _emu_to_in


def cmd_create(args):
    """Create a new empty .pptx file."""
    if os.path.exists(args.file) and not args.force:
        _die(f"file already exists: {args.file} (use --force to overwrite)")
    prs = Presentation()
    if args.width:
        prs.slide_width = _parse_length(args.width)
    if args.height:
        prs.slide_height = _parse_length(args.height)
    if args.widescreen:
        prs.slide_width = Inches(13.333)
        prs.slide_height = Inches(7.5)
    prs.save(args.file)
    print(json.dumps({
        "created": args.file,
        "width": _emu_to_in(prs.slide_width),
        "height": _emu_to_in(prs.slide_height),
        "layouts": [l.name for l in prs.slide_layouts],
    }))
