"""Text editing commands: set-text, set-title, set-notes, replace-text."""

import json
import sys
from copy import deepcopy

from .helpers import _die, _open, _get_slide, _find_shape, _save, _parse_inline_markdown


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
    all_runs = [_parse_inline_markdown(line) for line in lines]
    has_md = any(b or i for runs in all_runs for _, b, i in runs)

    for idx, line_runs in enumerate(all_runs):
        para = tf.paragraphs[0] if idx == 0 else tf.add_paragraph()
        for text, md_bold, md_italic in line_runs:
            run = para.add_run()
            run.text = text
            for k, v in font_props.items():
                if k in ("bold", "italic") and has_md:
                    continue
                if k == "color":
                    run.font.color.rgb = v
                elif k == "size":
                    run.font.size = v
                elif k == "name":
                    run.font.name = v
                else:
                    setattr(run.font, k, v)
            if md_bold:
                run.font.bold = True
            if md_italic:
                run.font.italic = True

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


_NS = "{http://schemas.openxmlformats.org/drawingml/2006/main}"


def _make_run_elem(text, rPr=None):
    """Create an <a:r> element with optional rPr and text."""
    from lxml import etree
    r = etree.Element(f"{_NS}r")
    if rPr is not None:
        r.append(rPr)
    t = etree.SubElement(r, f"{_NS}t")
    t.text = text
    t.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
    return r


def _paragraph_replace(para, search_text, repl_runs, formatting_aware,
                        search_bold=None, search_italic=None):
    """Replace search_text across run boundaries in a paragraph.
    Returns the number of replacements made."""
    runs = list(para.runs)
    if not runs:
        return 0

    # Snapshot run data
    run_data = []
    for run in runs:
        rPr = run._r.find(f"{_NS}rPr")
        run_data.append({
            "text": run.text or "",
            "rPr": deepcopy(rPr) if rPr is not None else None,
            "bold": bool(run.font.bold),
            "italic": bool(run.font.italic),
        })

    full_text = "".join(rd["text"] for rd in run_data)
    if search_text not in full_text:
        return 0

    # char_to_run[i] = index into run_data for character i
    char_to_run = []
    for i, rd in enumerate(run_data):
        char_to_run.extend([i] * len(rd["text"]))

    # Find all non-overlapping matches (with optional formatting check)
    matches = []
    pos = 0
    while pos < len(full_text):
        idx = full_text.find(search_text, pos)
        if idx == -1:
            break
        # Formatting filter: every run spanned by the match must satisfy it
        if search_bold is not None or search_italic is not None:
            match_ris = set(char_to_run[p] for p in range(idx, idx + len(search_text)))
            ok = True
            for ri in match_ris:
                if search_bold and not run_data[ri]["bold"]:
                    ok = False
                    break
                if search_italic and not run_data[ri]["italic"]:
                    ok = False
                    break
            if not ok:
                pos = idx + 1
                continue
        matches.append((idx, idx + len(search_text)))
        pos = idx + len(search_text)

    if not matches:
        return 0

    # Build output segments
    segments = []
    pos = 0
    for m_start, m_end in matches:
        if m_start > pos:
            segments.append(("keep", pos, m_start))
        segments.append(("replace", m_start, m_end))
        pos = m_end
    if pos < len(full_text):
        segments.append(("keep", pos, len(full_text)))

    # Build new run elements
    new_elems = []
    for seg in segments:
        if seg[0] == "keep":
            _, start, end = seg
            i = start
            while i < end:
                ri = char_to_run[i]
                j = i + 1
                while j < end and char_to_run[j] == ri:
                    j += 1
                rPr = deepcopy(run_data[ri]["rPr"]) if run_data[ri]["rPr"] else None
                new_elems.append(_make_run_elem(full_text[i:j], rPr))
                i = j
        else:  # replace
            _, m_start, m_end = seg
            template_rPr = run_data[char_to_run[m_start]]["rPr"]
            for md_text, bold, italic in repl_runs:
                rPr = deepcopy(template_rPr) if template_rPr else None
                if formatting_aware:
                    if (bold or italic) and rPr is None:
                        from lxml import etree
                        rPr = etree.Element(f"{_NS}rPr")
                    if rPr is not None:
                        if bold:
                            rPr.set("b", "1")
                        elif "b" in rPr.attrib:
                            del rPr.attrib["b"]
                        if italic:
                            rPr.set("i", "1")
                        elif "i" in rPr.attrib:
                            del rPr.attrib["i"]
                new_elems.append(_make_run_elem(md_text, rPr))

    # Remove old runs and insert new ones
    p_elem = para._p
    for run in runs:
        p_elem.remove(run._r)

    insert_idx = 0
    for i, child in enumerate(p_elem):
        if child.tag == f"{_NS}pPr":
            insert_idx = i + 1

    for j, r_elem in enumerate(new_elems):
        p_elem.insert(insert_idx + j, r_elem)

    return len(matches)


def cmd_replace_text(args):
    prs = _open(args.file)
    search_runs = _parse_inline_markdown(args.old)
    repl_runs = _parse_inline_markdown(args.new)

    search_text = "".join(t for t, _, _ in search_runs)
    search_has_md = any(b or i for _, b, i in search_runs)
    repl_has_md = any(b or i for _, b, i in repl_runs)
    formatting_aware = search_has_md or repl_has_md

    # For formatted search, get required formatting from the single span
    search_bold = search_italic = None
    if search_has_md and len(search_runs) == 1:
        _, search_bold, search_italic = search_runs[0]

    count = 0
    for slide in prs.slides:
        for shape in slide.shapes:
            if shape.has_text_frame:
                for para in shape.text_frame.paragraphs:
                    count += _paragraph_replace(
                        para, search_text, repl_runs, formatting_aware,
                        search_bold, search_italic,
                    )
    if count == 0:
        _die(f"text {search_text!r} not found in any slide")
    _save(prs, args.file, args.output)
    print(json.dumps({"replacements": count}), file=sys.stderr)
