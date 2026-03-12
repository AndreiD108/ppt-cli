"""Content insertion commands: add-image, add-textbox, add-table, delete-shape."""

import csv
import os

from .helpers import (_die, _open, _get_slide, _find_shape, _save,
                      _parse_length, _parse_color, Inches, Pt)


def cmd_add_image(args):
    prs = _open(args.file)
    slide = _get_slide(prs, args.slide)
    x = _parse_length(args.x) if args.x else Inches(1)
    y = _parse_length(args.y) if args.y else Inches(1)
    w = _parse_length(args.w) if args.w else None
    h = _parse_length(args.h) if args.h else None

    if not os.path.isfile(args.image):
        _die(f"image not found: {args.image}")

    kwargs = {"image_file": args.image, "left": x, "top": y}
    if w:
        kwargs["width"] = w
    if h:
        kwargs["height"] = h
    pic = slide.shapes.add_picture(**kwargs)
    _save(prs, args.file, args.output,
          extra={"shape_id": pic.shape_id, "name": pic.name})


def cmd_add_textbox(args):
    prs = _open(args.file)
    slide = _get_slide(prs, args.slide)
    x = _parse_length(args.x) if args.x else Inches(1)
    y = _parse_length(args.y) if args.y else Inches(1)
    w = _parse_length(args.w) if args.w else Inches(4)
    h = _parse_length(args.h) if args.h else Inches(1)

    txBox = slide.shapes.add_textbox(x, y, w, h)
    tf = txBox.text_frame
    tf.word_wrap = True

    lines = args.text.split("\\n") if "\\n" in args.text else [args.text]
    for i, line in enumerate(lines):
        para = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        run = para.add_run()
        run.text = line
        if args.font_size:
            run.font.size = Pt(args.font_size)
        if args.font_color:
            run.font.color.rgb = _parse_color(args.font_color)
        if args.bold:
            run.font.bold = True

    _save(prs, args.file, args.output,
          extra={"shape_id": txBox.shape_id, "name": txBox.name})


def cmd_add_table(args):
    prs = _open(args.file)
    slide = _get_slide(prs, args.slide)
    x = _parse_length(args.x) if args.x else Inches(1)
    y = _parse_length(args.y) if args.y else Inches(2)

    if not os.path.isfile(args.csv):
        _die(f"csv file not found: {args.csv}")
    with open(args.csv, newline="") as f:
        rows = list(csv.reader(f))
    if not rows:
        _die("csv file is empty")

    n_rows = len(rows)
    n_cols = max(len(r) for r in rows)
    w = _parse_length(args.w) if args.w else Inches(n_cols * 1.5)
    h = _parse_length(args.h) if args.h else Inches(n_rows * 0.4)

    table_shape = slide.shapes.add_table(n_rows, n_cols, x, y, w, h)
    table = table_shape.table

    for ri, row in enumerate(rows):
        for ci, val in enumerate(row):
            if ci < n_cols:
                table.cell(ri, ci).text = val

    _save(prs, args.file, args.output,
          extra={"shape_id": table_shape.shape_id, "name": table_shape.name,
                 "rows": n_rows, "cols": n_cols})


def cmd_delete_shape(args):
    prs = _open(args.file)
    slide = _get_slide(prs, args.slide)
    shape = _find_shape(slide, args.shape_id)
    sp = shape._element
    sp.getparent().remove(sp)
    _save(prs, args.file, args.output)
