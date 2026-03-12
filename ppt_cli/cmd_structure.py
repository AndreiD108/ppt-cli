"""Structural commands: add-slide, delete-slide, reorder, duplicate-slide."""

import copy

from .helpers import _die, _open, _get_slide, _save
from .serialisation import _shape_type_str


def cmd_add_slide(args):
    prs = _open(args.file)

    layout = None
    if args.layout:
        for sl in prs.slide_layouts:
            if sl.name.lower() == args.layout.lower():
                layout = sl
                break
        if layout is None:
            try:
                idx = int(args.layout)
                layout = prs.slide_layouts[idx]
            except (ValueError, IndexError):
                names = [sl.name for sl in prs.slide_layouts]
                _die(f"layout {args.layout!r} not found. Available: {names}")
    else:
        layout = prs.slide_layouts[0]

    slide = prs.slides.add_slide(layout)
    new_idx = len(prs.slides)

    if args.at is not None:
        _move_slide(prs, new_idx, args.at)
        new_idx = args.at

    shapes = [{"id": s.shape_id, "name": s.name, "type": _shape_type_str(s)}
              for s in slide.shapes]
    _save(prs, args.file, args.output,
          extra={"slide": new_idx, "layout": layout.name, "shapes": shapes})


def cmd_delete_slide(args):
    prs = _open(args.file)
    if args.slide < 1 or args.slide > len(prs.slides):
        _die(f"slide {args.slide} out of range")

    sldIdEl = prs.slides._sldIdLst[args.slide - 1]
    # Use proper namespace for r:id attribute
    ns = '{http://schemas.openxmlformats.org/officeDocument/2006/relationships}'
    rId = sldIdEl.get(f'{ns}id')
    if rId is not None:
        prs.part.drop_rel(rId)
    prs.slides._sldIdLst.remove(sldIdEl)

    _save(prs, args.file, args.output,
          extra={"deleted_slide": args.slide, "slides_remaining": len(prs.slides)})


def cmd_reorder(args):
    prs = _open(args.file)
    _move_slide(prs, args.slide, args.to)
    _save(prs, args.file, args.output)


def _move_slide(prs, from_pos, to_pos):
    """Move slide from from_pos to to_pos (both 1-based)."""
    slides = prs.slides._sldIdLst
    total = len(slides)
    if from_pos < 1 or from_pos > total:
        _die(f"source slide {from_pos} out of range")
    if to_pos < 1 or to_pos > total:
        _die(f"target position {to_pos} out of range")

    el = slides[from_pos - 1]
    slides.remove(el)
    if to_pos - 1 >= len(slides):
        slides.append(el)
    else:
        slides.insert(to_pos - 1, el)


def cmd_duplicate(args):
    prs = _open(args.file)
    slide = _get_slide(prs, args.slide)

    new_slide = prs.slides.add_slide(slide.slide_layout)

    for shape in list(new_slide.shapes):
        sp = shape._element
        sp.getparent().remove(sp)

    for shape in slide.shapes:
        el = copy.deepcopy(shape._element)
        new_slide.shapes._spTree.append(el)

    for rel in slide.part.rels.values():
        if "image" in rel.reltype:
            new_slide.part.rels.get_or_add(rel.reltype, rel.target_part)

    _save(prs, args.file, args.output,
          extra={"new_slide": len(prs.slides)})
