"""Styling commands: set-font, set-fill, set-position."""

from .helpers import (_die, _open, _get_slide, _find_shape, _save,
                      _parse_length, _parse_color, Pt)


def cmd_set_font(args):
    prs = _open(args.file)
    slide = _get_slide(prs, args.slide)
    shape = _find_shape(slide, args.shape_id)
    if not shape.has_text_frame:
        _die(f"shape {args.shape_id} has no text frame")

    for para in shape.text_frame.paragraphs:
        for run in para.runs:
            if args.bold is not None:
                run.font.bold = args.bold
            if args.italic is not None:
                run.font.italic = args.italic
            if args.size is not None:
                run.font.size = Pt(args.size)
            if args.color:
                run.font.color.rgb = _parse_color(args.color)
            if args.name:
                run.font.name = args.name

    _save(prs, args.file, args.output)


def cmd_set_fill(args):
    prs = _open(args.file)
    slide = _get_slide(prs, args.slide)
    shape = _find_shape(slide, args.shape_id)

    fill = shape.fill
    fill.solid()
    fill.fore_color.rgb = _parse_color(args.color)

    _save(prs, args.file, args.output)


def cmd_set_position(args):
    prs = _open(args.file)
    slide = _get_slide(prs, args.slide)
    shape = _find_shape(slide, args.shape_id)

    if args.x is not None:
        shape.left = _parse_length(args.x)
    if args.y is not None:
        shape.top = _parse_length(args.y)
    if args.w is not None:
        shape.width = _parse_length(args.w)
    if args.h is not None:
        shape.height = _parse_length(args.h)

    _save(prs, args.file, args.output)
