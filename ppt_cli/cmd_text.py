"""Text editing commands: set-text, set-title, set-notes, replace-text."""

import json
import sys

from .helpers import _die, _open, _get_slide, _find_shape, _save


def cmd_set_text(args):
    prs = _open(args.file)
    slide = _get_slide(prs, args.slide)
    shape = _find_shape(slide, args.shape_id)
    if not shape.has_text_frame:
        _die(f"shape {args.shape_id} has no text frame")

    tf = shape.text_frame
    first_para = tf.paragraphs[0]
    font_props = {}
    if first_para.runs:
        run = first_para.runs[0]
        if run.font.bold is not None:
            font_props["bold"] = run.font.bold
        if run.font.italic is not None:
            font_props["italic"] = run.font.italic
        if run.font.size is not None:
            font_props["size"] = run.font.size
        try:
            if run.font.color and run.font.color.rgb:
                font_props["color"] = run.font.color.rgb
        except (AttributeError, TypeError):
            pass
        if run.font.name:
            font_props["name"] = run.font.name

    tf.clear()
    lines = args.text.split("\\n") if "\\n" in args.text else [args.text]
    for i, line in enumerate(lines):
        para = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        run = para.add_run()
        run.text = line
        for k, v in font_props.items():
            if k == "color":
                run.font.color.rgb = v
            elif k == "size":
                run.font.size = v
            elif k == "name":
                run.font.name = v
            else:
                setattr(run.font, k, v)

    _save(prs, args.file, args.output)


def cmd_set_title(args):
    prs = _open(args.file)
    slide = _get_slide(prs, args.slide)
    for shape in slide.shapes:
        if shape.is_placeholder and shape.placeholder_format.idx == 0:
            shape.text = args.text
            _save(prs, args.file, args.output)
            return
    _die("no title placeholder found on this slide")


def cmd_set_notes(args):
    prs = _open(args.file)
    slide = _get_slide(prs, args.slide)
    if not slide.has_notes_slide:
        slide.notes_slide  # creates notes slide
    slide.notes_slide.notes_text_frame.text = args.text
    _save(prs, args.file, args.output)


def cmd_replace_text(args):
    prs = _open(args.file)
    count = 0
    for slide in prs.slides:
        for shape in slide.shapes:
            if shape.has_text_frame:
                for para in shape.text_frame.paragraphs:
                    for run in para.runs:
                        if args.old in run.text:
                            run.text = run.text.replace(args.old, args.new)
                            count += 1
    if count == 0:
        _die(f"text {args.old!r} not found in any slide")
    _save(prs, args.file, args.output)
    print(json.dumps({"replacements": count}), file=sys.stderr)
