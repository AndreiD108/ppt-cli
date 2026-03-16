"""Create command."""

import json
import os

from .helpers import _die, _parse_length, Presentation, Inches
from .serialisation import _emu_to_in
from .template_registry import _get_template_path, _get_default_template


def cmd_create(args):
    """Create a new empty .pptx file."""
    if os.path.exists(args.file) and not args.force:
        _die(f"file already exists: {args.file} (use --force to overwrite)")

    template_path = None
    template_name = None
    if hasattr(args, "template") and args.template:
        if os.path.isfile(args.template):
            template_path = args.template
        else:
            template_path = _get_template_path(args.template)
            if not template_path or not os.path.isfile(template_path):
                _die(f"template {args.template!r} not found (not a file path or registered name)")
            template_name = args.template
    else:
        default = _get_default_template()
        if default:
            template_path = _get_template_path(default)
            if template_path and os.path.isfile(template_path):
                template_name = default
            else:
                template_path = None

    prs = Presentation(template_path) if template_path else Presentation()

    # Default to 16:9 widescreen unless a template provides its own dimensions
    if not template_path:
        prs.slide_width = Inches(13.333)
        prs.slide_height = Inches(7.5)
    if args.legacy:
        prs.slide_width = Inches(10)
        prs.slide_height = Inches(7.5)
    if args.width:
        prs.slide_width = _parse_length(args.width)
    if args.height:
        prs.slide_height = _parse_length(args.height)
    prs.save(args.file)
    result = {
        "created": args.file,
        "width": _emu_to_in(prs.slide_width),
        "height": _emu_to_in(prs.slide_height),
        "layouts": [l.name for l in prs.slide_layouts],
    }
    if template_path:
        result["template"] = template_name or template_path
    print(json.dumps(result))
