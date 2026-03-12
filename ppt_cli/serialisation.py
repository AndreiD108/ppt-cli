"""Serialisation helpers — shape/slide to dict/text."""


def _emu_to_in(val):
    if val is None:
        return None
    return f"{val / 914400:.2f}in"


def _shape_type_str(shape):
    if shape.is_placeholder:
        return "placeholder"
    st = shape.shape_type
    if st is None:
        return "unknown"
    type_map = {
        1: "auto_shape", 5: "freeform", 6: "group", 13: "picture",
        17: "text_box", 19: "table", 32: "chart",
    }
    return type_map.get(int(st), str(st))


def _text_frame_to_list(tf):
    paragraphs = []
    for para in tf.paragraphs:
        p = {}
        p["text"] = "".join(run.text for run in para.runs) or para.text
        if para.level and para.level > 0:
            p["level"] = para.level
        pPr = para._pPr
        if pPr is not None:
            ns = "{http://schemas.openxmlformats.org/drawingml/2006/main}"
            has_buNone = pPr.find(f"{ns}buNone") is not None
            has_buChar = pPr.find(f"{ns}buChar") is not None
            has_buAuto = pPr.find(f"{ns}buAutoNum") is not None
            if (has_buChar or has_buAuto) and not has_buNone:
                p["bullet"] = True
        if para.runs:
            run = para.runs[0]
            if run.font.bold:
                p["bold"] = True
            if run.font.italic:
                p["italic"] = True
            if run.font.size:
                p["size"] = run.font.size.pt
            try:
                if run.font.color and run.font.color.rgb:
                    p["color"] = f"#{run.font.color.rgb}"
            except (AttributeError, TypeError):
                pass
        paragraphs.append(p)
    return paragraphs


def _table_to_list(table):
    rows = []
    for row in table.rows:
        rows.append([cell.text for cell in row.cells])
    return rows


def _shape_to_dict(shape):
    d = {
        "id": shape.shape_id,
        "name": shape.name,
        "type": _shape_type_str(shape),
        "position": {
            "x": _emu_to_in(shape.left),
            "y": _emu_to_in(shape.top),
            "w": _emu_to_in(shape.width),
            "h": _emu_to_in(shape.height),
        },
    }
    if shape.has_text_frame:
        d["text"] = _text_frame_to_list(shape.text_frame)
    if shape.has_table:
        d["table"] = _table_to_list(shape.table)
    if hasattr(shape, "image"):
        try:
            d["image"] = {"content_type": shape.image.content_type}
        except Exception:
            pass
    if shape.is_placeholder:
        d["placeholder_idx"] = shape.placeholder_format.idx
    return d


def _dump_slide(slide, num):
    notes = None
    if slide.has_notes_slide:
        notes = slide.notes_slide.notes_text_frame.text
    return {
        "slide_number": num,
        "layout": slide.slide_layout.name if slide.slide_layout else None,
        "shapes": [_shape_to_dict(s) for s in slide.shapes],
        "notes": notes,
    }


def _peek_slide(slide, num):
    """Compact one-line-per-shape summary of a slide."""
    lines = []
    title = None
    for shape in slide.shapes:
        if shape.is_placeholder and shape.placeholder_format.idx == 0:
            title = shape.text
            break
    lines.append(f"slide {num}: {title or '(untitled)'}"
                 f"  [{slide.slide_layout.name}]"
                 f"  ({len(slide.shapes)} shapes)")

    for shape in slide.shapes:
        sid = shape.shape_id
        stype = _shape_type_str(shape)
        name = shape.name

        preview = ""
        if shape.has_text_frame:
            text = shape.text_frame.text.replace("\n", " | ")
            if len(text) > 80:
                text = text[:77] + "..."
            preview = text
        elif shape.has_table:
            t = shape.table
            preview = f"[table {len(t.rows)}x{len(t.columns)}]"
        elif hasattr(shape, "image"):
            try:
                preview = f"[image {shape.image.content_type}]"
            except Exception:
                preview = "[image]"

        parts = [f"  id={sid}", stype, name]
        if preview:
            parts.append(f'"{preview}"')
        lines.append("  ".join(parts))

    return "\n".join(lines)
