"""Internals command handlers: stage, build, analyze, fingerprint, and multi-file mutations."""

import json
import os
import re
import shutil
import sys

from lxml import etree

from .helpers import _die, Presentation
from .staging import _stage, _resolve_staged_or_file, _staging_dir
from .ooxml import (
    NS_A, NS_R, NS_P, NS_CT, NS_REL,
    RT_SLIDE, RT_SLIDE_LAYOUT, RT_SLIDE_MASTER, RT_THEME, RT_NOTES_SLIDE,
    CT_SLIDE, CT_SLIDE_LAYOUT, CT_SLIDE_MASTER, CT_NOTES_SLIDE, CT_THEME,
    _parse_xml, _write_xml, _rels_path_for,
    _get_rels, _add_rel, _remove_rel, _find_rel_by_target, _find_rel_by_type,
    _add_content_type_override, _remove_content_type_override,
    _get_slide_ids, _next_slide_id, _next_part_number,
    _build_pptx, _validate_staged, _prune_unused,
    _pres_path, _remove_layout_from_master_xml,
)
from .template_registry import (
    _validate_template_name, _ensure_template_dir, _save_to_registry,
    _get_template_path,
)


# ── stage ──

def cmd_stage(args):
    staged = _stage(args.file)
    print(json.dumps({"staged": staged}))


# ── analyze ──

def cmd_analyze(args):
    staged = _resolve_staged_or_file(args.file)
    result = _analyze(staged)
    if getattr(args, "json", False):
        print(json.dumps(result, indent=2))
    else:
        _print_analyze_text(result)


def _analyze(staged):
    """Build analysis data from a staged directory."""
    # Gather slide -> layout mapping
    slides = []
    slides_dir = os.path.join(staged, "ppt", "slides")
    if os.path.isdir(slides_dir):
        slide_files = sorted(
            [f for f in os.listdir(slides_dir) if re.match(r"slide\d+\.xml$", f)],
            key=lambda f: int(re.search(r"(\d+)", f).group(1)),
        )
        for sf in slide_files:
            rels = _get_rels(staged, f"ppt/slides/{sf}")
            layout_target = None
            for r in rels:
                if r["type"] == RT_SLIDE_LAYOUT:
                    layout_target = r["target"]
                    break
            slides.append({"file": sf, "layout": layout_target})

    # Gather layouts
    layouts = []
    layouts_dir = os.path.join(staged, "ppt", "slideLayouts")
    layout_slide_count = {}
    for s in slides:
        lt = s.get("layout")
        if lt:
            layout_slide_count[lt] = layout_slide_count.get(lt, 0) + 1

    if os.path.isdir(layouts_dir):
        layout_files = sorted(
            [f for f in os.listdir(layouts_dir) if re.match(r"slideLayout\d+\.xml$", f)],
            key=lambda f: int(re.search(r"(\d+)", f).group(1)),
        )
        for lf in layout_files:
            layout_path = os.path.join(layouts_dir, lf)
            root = _parse_xml(layout_path)
            csld = root.find(f"{{{NS_P}}}cSld")
            name = csld.get("name", "") if csld is not None else ""

            # Find master via layout's .rels
            rels = _get_rels(staged, f"ppt/slideLayouts/{lf}")
            master = None
            for r in rels:
                if r["type"] == RT_SLIDE_MASTER:
                    master = r["target"]
                    break

            # Extract placeholders
            placeholders = []
            if csld is not None:
                sp_tree = csld.find(f"{{{NS_P}}}spTree")
                if sp_tree is not None:
                    for sp in sp_tree:
                        nv = sp.find(f"{{{NS_P}}}nvSpPr")
                        if nv is None:
                            continue
                        nv_pr = nv.find(f"{{{NS_P}}}nvPr")
                        if nv_pr is None:
                            continue
                        ph = nv_pr.find(f"{{{NS_P}}}ph")
                        if ph is not None:
                            placeholders.append({
                                "type": ph.get("type", "body"),
                                "idx": ph.get("idx", ""),
                            })

            rel_target = f"../slideLayouts/{lf}"
            used_by = layout_slide_count.get(rel_target, 0)
            layouts.append({
                "file": lf,
                "name": name,
                "master": master,
                "placeholders": placeholders,
                "used_by_slides": used_by,
            })

    # Gather masters
    masters = []
    masters_dir = os.path.join(staged, "ppt", "slideMasters")
    if os.path.isdir(masters_dir):
        master_files = sorted(
            [f for f in os.listdir(masters_dir) if re.match(r"slideMaster\d+\.xml$", f)],
            key=lambda f: int(re.search(r"(\d+)", f).group(1)),
        )
        for mf in master_files:
            master_path = os.path.join(masters_dir, mf)
            root = _parse_xml(master_path)
            csld = root.find(f"{{{NS_P}}}cSld")
            name = csld.get("name", "") if csld is not None else ""
            rels = _get_rels(staged, f"ppt/slideMasters/{mf}")
            theme = None
            for r in rels:
                if r["type"] == RT_THEME:
                    theme = r["target"]
                    break
            layout_count = sum(1 for r in rels if r["type"] == RT_SLIDE_LAYOUT)
            masters.append({
                "file": mf,
                "name": name,
                "theme": theme,
                "layout_count": layout_count,
            })

    # Gather media
    media = []
    media_dir = os.path.join(staged, "ppt", "media")
    if os.path.isdir(media_dir):
        for f in sorted(os.listdir(media_dir)):
            full = os.path.join(media_dir, f)
            media.append({"file": f, "size": os.path.getsize(full)})

    return {
        "slides": slides,
        "layouts": layouts,
        "masters": masters,
        "media": media,
    }


def _print_analyze_text(data):
    print(f"Slides: {len(data['slides'])}")
    print(f"Masters: {len(data['masters'])}")
    for m in data["masters"]:
        print(f"  {m['file']}: {m['name']!r} ({m['layout_count']} layouts, theme: {m['theme']})")
    print(f"Layouts: {len(data['layouts'])}")
    for l in data["layouts"]:
        used = f" [{l['used_by_slides']} slides]" if l["used_by_slides"] else " [unused]"
        phs = ", ".join(p["type"] for p in l["placeholders"]) if l["placeholders"] else "none"
        print(f"  {l['file']}: {l['name']!r}{used} (placeholders: {phs})")
    if data["media"]:
        total = sum(m["size"] for m in data["media"])
        print(f"Media: {len(data['media'])} files ({total:,} bytes)")
        for m in data["media"]:
            print(f"  {m['file']}: {m['size']:,} bytes")
    else:
        print("Media: none")


# ── fingerprint ──

def cmd_fingerprint(args):
    prs = Presentation(args.file)
    result = []
    if args.slide:
        slides_to_check = [args.slide]
    else:
        slides_to_check = list(range(1, len(prs.slides) + 1))

    for sn in slides_to_check:
        slide = prs.slides[sn - 1]
        shapes = []
        for shape in slide.shapes:
            info = {
                "id": shape.shape_id,
                "name": shape.name,
                "type": str(shape.shape_type),
                "left": shape.left,
                "top": shape.top,
                "width": shape.width,
                "height": shape.height,
            }
            if shape.has_text_frame:
                tf = shape.text_frame
                if tf.paragraphs:
                    first_para = tf.paragraphs[0]
                    if first_para.runs:
                        run = first_para.runs[0]
                        info["font_size"] = run.font.size
                        if run.font.color and run.font.color.rgb:
                            info["font_color"] = str(run.font.color.rgb)
            if hasattr(shape, "fill"):
                try:
                    fill = shape.fill
                    if fill.type is not None:
                        info["fill_type"] = str(fill.type)
                except Exception:
                    pass
            shapes.append(info)
        result.append({"slide": sn, "layout": slide.slide_layout.name, "shapes": shapes})

    if getattr(args, "json", False):
        print(json.dumps(result, indent=2, default=str))
    else:
        for sr in result:
            print(f"Slide {sr['slide']}: layout={sr['layout']!r}, {len(sr['shapes'])} shapes")
            for sh in sr["shapes"]:
                print(f"  {sh['name']} (id={sh['id']}) @ ({sh['left']},{sh['top']}) "
                      f"size=({sh['width']}x{sh['height']})")


# ── build ──

def cmd_build(args):
    staged = args.staged_dir
    if not os.path.isdir(staged):
        _die(f"not a directory: {staged}")
    if args.clean:
        summary = _prune_unused(staged)
        if summary["removed_layouts"] or summary["removed_media"]:
            print(json.dumps({"pruned": summary}), file=sys.stderr)
    warnings = _validate_staged(staged)
    if warnings:
        for w in warnings:
            print(f"warning: {w}", file=sys.stderr)
    _build_pptx(staged, args.output)
    print(json.dumps({"built": args.output, "warnings": warnings}))


# ── build-template ──

def cmd_build_template(args):
    try:
        _validate_template_name(args.name)
    except ValueError as e:
        _die(str(e))

    staged = args.staged_dir
    if not os.path.isdir(staged):
        _die(f"not a directory: {staged}")

    tmpl_dir = _ensure_template_dir()
    filename = f"{args.name}.pptx"
    dest = os.path.join(tmpl_dir, filename)

    if os.path.isfile(dest) and not args.force:
        _die(f"template {args.name!r} already exists (use -f to overwrite)")

    warnings = _validate_staged(staged)
    if warnings:
        for w in warnings:
            print(f"warning: {w}", file=sys.stderr)

    _build_pptx(staged, dest)
    _save_to_registry(args.name, args.description or "", filename)

    # Print summary
    prs = Presentation(dest)
    layout_names = [sl.name for sl in prs.slide_layouts]
    print(json.dumps({
        "template": args.name,
        "path": dest,
        "layouts": layout_names,
        "warnings": warnings,
    }))


# ── Multi-file mutations: delete ──

def cmd_delete_slide_internal(args):
    staged = _resolve_staged_or_file(args.file)
    slide_ids = _get_slide_ids(staged)
    n = args.slide
    if n < 1 or n > len(slide_ids):
        _die(f"slide {n} out of range (deck has {len(slide_ids)} slides)")

    sid = slide_ids[n - 1]
    rid = sid["rid"]

    # Find slide file from presentation.xml.rels
    pres_rels = _get_rels(staged, "ppt/presentation.xml")
    slide_file = None
    for r in pres_rels:
        if r["id"] == rid:
            slide_file = r["target"]
            break

    if not slide_file:
        _die(f"cannot find slide file for rId {rid}")

    # slide_file is like "slides/slide1.xml" (relative to ppt/)
    slide_path = os.path.join(staged, "ppt", slide_file)
    slide_rels_path = os.path.join(staged, _rels_path_for(os.path.join("ppt", slide_file)))

    # Check for notes slide
    slide_rels = _get_rels(staged, os.path.join("ppt", slide_file))
    for r in slide_rels:
        if r["type"] == RT_NOTES_SLIDE:
            notes_target = r["target"]
            # notes target relative to ppt/slides/ -> ppt/notesSlides/...
            notes_full = os.path.normpath(os.path.join(os.path.dirname(slide_path), notes_target))
            notes_rels = os.path.join(
                staged, _rels_path_for(
                    os.path.relpath(notes_full, staged)
                )
            )
            if os.path.isfile(notes_full):
                _remove_content_type_override(
                    staged, "/" + os.path.relpath(notes_full, staged)
                )
                os.remove(notes_full)
            if os.path.isfile(notes_rels):
                os.remove(notes_rels)

    # Remove slide file and its .rels
    if os.path.isfile(slide_path):
        os.remove(slide_path)
    if os.path.isfile(slide_rels_path):
        os.remove(slide_rels_path)

    # Update presentation.xml - remove sldId
    pres_root = _parse_xml(_pres_path(staged))
    sld_id_lst = pres_root.find(f"{{{NS_P}}}sldIdLst")
    if sld_id_lst is not None:
        for el in sld_id_lst.findall(f"{{{NS_P}}}sldId"):
            if el.get(f"{{{NS_R}}}id") == rid:
                sld_id_lst.remove(el)
                break
    _write_xml(pres_root, _pres_path(staged))

    # Remove from presentation.xml.rels
    _remove_rel(staged, "ppt/presentation.xml", rid)

    # Remove from [Content_Types].xml
    part_name = "/" + os.path.join("ppt", slide_file).replace("\\", "/")
    _remove_content_type_override(staged, part_name)

    print(json.dumps({
        "deleted": "slide",
        "slide": n,
        "staged": staged,
        "slides_remaining": len(slide_ids) - 1,
    }))


def cmd_delete_layout(args):
    staged = _resolve_staged_or_file(args.file)
    layout_name = args.layout
    master_num = args.master

    # Find the layout file by name
    layouts_dir = os.path.join(staged, "ppt", "slideLayouts")
    if not os.path.isdir(layouts_dir):
        _die("no slideLayouts directory found")

    target_file = None
    for f in sorted(os.listdir(layouts_dir)):
        if not (f.startswith("slideLayout") and f.endswith(".xml")):
            continue
        root = _parse_xml(os.path.join(layouts_dir, f))
        csld = root.find(f"{{{NS_P}}}cSld")
        name = csld.get("name", "") if csld is not None else ""
        if name == layout_name:
            # If master specified, check this layout belongs to that master
            if master_num is not None:
                rels = _get_rels(staged, f"ppt/slideLayouts/{f}")
                master_target = None
                for r in rels:
                    if r["type"] == RT_SLIDE_MASTER:
                        master_target = r["target"]
                        break
                if master_target:
                    expected = f"../slideMasters/slideMaster{master_num}.xml"
                    if master_target != expected:
                        continue
            target_file = f
            break

    if not target_file:
        _die(f"layout {layout_name!r} not found")

    # Check layout is not in use by any slide
    slides_dir = os.path.join(staged, "ppt", "slides")
    if os.path.isdir(slides_dir):
        for sf in os.listdir(slides_dir):
            if not (sf.startswith("slide") and sf.endswith(".xml")):
                continue
            rels = _get_rels(staged, f"ppt/slides/{sf}")
            for r in rels:
                if r["type"] == RT_SLIDE_LAYOUT and r["target"] == f"../slideLayouts/{target_file}":
                    _die(f"layout {layout_name!r} is in use by {sf}")

    # Remove layout files and references
    layout_path = os.path.join(layouts_dir, target_file)
    layout_rels = os.path.join(layouts_dir, "_rels", target_file + ".rels")

    # Find which master owns this layout and remove from master
    masters_dir = os.path.join(staged, "ppt", "slideMasters")
    if os.path.isdir(masters_dir):
        for mf in os.listdir(masters_dir):
            if not (mf.startswith("slideMaster") and mf.endswith(".xml")):
                continue
            master_part = f"ppt/slideMasters/{mf}"
            target = f"../slideLayouts/{target_file}"
            rel = _find_rel_by_target(staged, master_part, target)
            if rel:
                _remove_rel(staged, master_part, rel["id"])
                _remove_layout_from_master_xml(staged, master_part, rel["id"])

    if os.path.isfile(layout_path):
        os.remove(layout_path)
    if os.path.isfile(layout_rels):
        os.remove(layout_rels)

    _remove_content_type_override(staged, f"/ppt/slideLayouts/{target_file}")

    print(json.dumps({
        "deleted": "layout",
        "layout": layout_name,
        "file": target_file,
        "staged": staged,
    }))


def cmd_delete_master(args):
    staged = _resolve_staged_or_file(args.file)
    n = args.master
    master_file = f"slideMaster{n}.xml"
    master_part = f"ppt/slideMasters/{master_file}"
    master_path = os.path.join(staged, master_part)

    if not os.path.isfile(master_path):
        _die(f"master {n} not found")

    # Check this isn't the last master
    masters_dir = os.path.join(staged, "ppt", "slideMasters")
    master_count = len([f for f in os.listdir(masters_dir)
                        if f.startswith("slideMaster") and f.endswith(".xml")])
    if master_count <= 1:
        _die("cannot delete the last slide master")

    # Get master's relationships to find owned layouts and theme
    master_rels = _get_rels(staged, master_part)
    owned_layouts = [r["target"] for r in master_rels if r["type"] == RT_SLIDE_LAYOUT]
    theme_targets = [r["target"] for r in master_rels if r["type"] == RT_THEME]

    # Check no slides reference layouts owned by this master
    slides_dir = os.path.join(staged, "ppt", "slides")
    if os.path.isdir(slides_dir):
        for sf in os.listdir(slides_dir):
            if not (sf.startswith("slide") and sf.endswith(".xml")):
                continue
            rels = _get_rels(staged, f"ppt/slides/{sf}")
            for r in rels:
                if r["type"] == RT_SLIDE_LAYOUT:
                    # Layout target from slide is ../slideLayouts/X, from master is ../slideLayouts/X
                    layout_file = os.path.basename(r["target"])
                    for ol in owned_layouts:
                        if os.path.basename(ol) == layout_file:
                            _die(f"cannot delete master {n}: layout {layout_file} is in use by {sf}")

    # Delete owned layouts
    deleted_layouts = []
    for lt in owned_layouts:
        layout_file = os.path.basename(lt)
        layout_path = os.path.join(staged, "ppt", "slideLayouts", layout_file)
        layout_rels_path = os.path.join(staged, "ppt", "slideLayouts", "_rels", layout_file + ".rels")
        if os.path.isfile(layout_path):
            os.remove(layout_path)
        if os.path.isfile(layout_rels_path):
            os.remove(layout_rels_path)
        _remove_content_type_override(staged, f"/ppt/slideLayouts/{layout_file}")
        deleted_layouts.append(layout_file)

    # Delete theme if not shared by another master
    deleted_theme = None
    for tt in theme_targets:
        theme_file = os.path.basename(tt)
        # Check if any other master references this theme
        shared = False
        for mf in os.listdir(masters_dir):
            if mf == master_file or not (mf.startswith("slideMaster") and mf.endswith(".xml")):
                continue
            other_rels = _get_rels(staged, f"ppt/slideMasters/{mf}")
            for r in other_rels:
                if r["type"] == RT_THEME and os.path.basename(r["target"]) == theme_file:
                    shared = True
                    break
            if shared:
                break
        if not shared:
            theme_path = os.path.join(staged, "ppt", "theme", theme_file)
            theme_rels = os.path.join(staged, "ppt", "theme", "_rels", theme_file + ".rels")
            if os.path.isfile(theme_path):
                os.remove(theme_path)
            if os.path.isfile(theme_rels):
                os.remove(theme_rels)
            _remove_content_type_override(staged, f"/ppt/theme/{theme_file}")
            deleted_theme = theme_file

    # Delete master file and its .rels
    if os.path.isfile(master_path):
        os.remove(master_path)
    master_rels_path = os.path.join(staged, "ppt", "slideMasters", "_rels", master_file + ".rels")
    if os.path.isfile(master_rels_path):
        os.remove(master_rels_path)

    # Update presentation.xml - remove sldMasterId
    pres_root = _parse_xml(_pres_path(staged))
    master_id_lst = pres_root.find(f"{{{NS_P}}}sldMasterIdLst")
    if master_id_lst is not None:
        pres_rels = _get_rels(staged, "ppt/presentation.xml")
        master_rid = None
        for r in pres_rels:
            if r["target"] == f"slideMasters/{master_file}":
                master_rid = r["id"]
                break
        if master_rid:
            for el in master_id_lst.findall(f"{{{NS_P}}}sldMasterId"):
                if el.get(f"{{{NS_R}}}id") == master_rid:
                    master_id_lst.remove(el)
                    break
    _write_xml(pres_root, _pres_path(staged))

    # Remove from presentation.xml.rels
    pres_rels = _get_rels(staged, "ppt/presentation.xml")
    for r in pres_rels:
        if r["target"] == f"slideMasters/{master_file}":
            _remove_rel(staged, "ppt/presentation.xml", r["id"])
            break

    _remove_content_type_override(staged, f"/ppt/slideMasters/{master_file}")

    print(json.dumps({
        "deleted": "master",
        "master": n,
        "staged": staged,
        "deleted_layouts": deleted_layouts,
        "deleted_theme": deleted_theme,
    }))


# ── Multi-file mutations: duplicate ──

def cmd_duplicate_slide_internal(args):
    staged = _resolve_staged_or_file(args.file)
    slide_ids = _get_slide_ids(staged)
    n = args.slide
    if n < 1 or n > len(slide_ids):
        _die(f"slide {n} out of range (deck has {len(slide_ids)} slides)")

    sid = slide_ids[n - 1]
    rid = sid["rid"]

    # Find source slide file
    pres_rels = _get_rels(staged, "ppt/presentation.xml")
    src_file = None
    for r in pres_rels:
        if r["id"] == rid:
            src_file = r["target"]
            break

    if not src_file:
        _die(f"cannot find slide file for rId {rid}")

    # Determine new slide number
    new_num = _next_part_number(staged, "ppt/slides", "slide")
    new_file = f"slides/slide{new_num}.xml"
    new_full = os.path.join(staged, "ppt", new_file)

    # Copy slide file
    src_full = os.path.join(staged, "ppt", src_file)
    os.makedirs(os.path.dirname(new_full), exist_ok=True)
    shutil.copy2(src_full, new_full)

    # Copy slide .rels if exists
    src_rels = os.path.join(staged, _rels_path_for(os.path.join("ppt", src_file)))
    new_rels = os.path.join(staged, _rels_path_for(os.path.join("ppt", new_file)))
    if os.path.isfile(src_rels):
        os.makedirs(os.path.dirname(new_rels), exist_ok=True)
        shutil.copy2(src_rels, new_rels)

    # Handle notes slide - duplicate if exists
    src_slide_rels = _get_rels(staged, os.path.join("ppt", src_file))
    for r in src_slide_rels:
        if r["type"] == RT_NOTES_SLIDE:
            src_notes = r["target"]  # ../notesSlides/notesSlideN.xml
            src_notes_full = os.path.normpath(
                os.path.join(os.path.dirname(src_full), src_notes)
            )
            if os.path.isfile(src_notes_full):
                new_notes_num = _next_part_number(staged, "ppt/notesSlides", "notesSlide")
                new_notes_file = f"notesSlide{new_notes_num}.xml"
                new_notes_full = os.path.join(staged, "ppt", "notesSlides", new_notes_file)
                shutil.copy2(src_notes_full, new_notes_full)
                # Copy notes .rels
                src_notes_rels = os.path.join(
                    staged, _rels_path_for(
                        os.path.relpath(src_notes_full, staged)
                    )
                )
                new_notes_rels = os.path.join(
                    staged, _rels_path_for(f"ppt/notesSlides/{new_notes_file}")
                )
                if os.path.isfile(src_notes_rels):
                    os.makedirs(os.path.dirname(new_notes_rels), exist_ok=True)
                    shutil.copy2(src_notes_rels, new_notes_rels)
                # Update new slide's .rels to point to new notes
                new_slide_rels_data = _get_rels(staged, os.path.join("ppt", new_file))
                for nr in new_slide_rels_data:
                    if nr["type"] == RT_NOTES_SLIDE:
                        _remove_rel(staged, os.path.join("ppt", new_file), nr["id"])
                        _add_rel(staged, os.path.join("ppt", new_file), RT_NOTES_SLIDE,
                                 f"../notesSlides/{new_notes_file}")
                        break
                _add_content_type_override(
                    staged, f"/ppt/notesSlides/{new_notes_file}", CT_NOTES_SLIDE
                )

    # Add to presentation.xml.rels
    new_rid = _add_rel(staged, "ppt/presentation.xml", RT_SLIDE, new_file)

    # Add to presentation.xml sldIdLst
    new_id = _next_slide_id(staged)
    pres_root = _parse_xml(_pres_path(staged))
    sld_id_lst = pres_root.find(f"{{{NS_P}}}sldIdLst")
    if sld_id_lst is None:
        sld_id_lst = etree.SubElement(pres_root, f"{{{NS_P}}}sldIdLst")
    etree.SubElement(sld_id_lst, f"{{{NS_P}}}sldId", attrib={
        "id": str(new_id),
        f"{{{NS_R}}}id": new_rid,
    })
    _write_xml(pres_root, _pres_path(staged))

    # Add to [Content_Types].xml
    _add_content_type_override(staged, f"/ppt/{new_file}", CT_SLIDE)

    print(json.dumps({
        "duplicated": "slide",
        "source_slide": n,
        "new_file": new_file,
        "staged": staged,
    }))


def cmd_duplicate_layout(args):
    staged = _resolve_staged_or_file(args.file)
    source_name = args.source
    new_name = args.name
    master_num = args.master

    # Find source layout
    layouts_dir = os.path.join(staged, "ppt", "slideLayouts")
    if not os.path.isdir(layouts_dir):
        _die("no slideLayouts directory found")

    src_file = None
    for f in sorted(os.listdir(layouts_dir)):
        if not (f.startswith("slideLayout") and f.endswith(".xml")):
            continue
        root = _parse_xml(os.path.join(layouts_dir, f))
        csld = root.find(f"{{{NS_P}}}cSld")
        name = csld.get("name", "") if csld is not None else ""
        if name == source_name:
            if master_num is not None:
                rels = _get_rels(staged, f"ppt/slideLayouts/{f}")
                master_target = None
                for r in rels:
                    if r["type"] == RT_SLIDE_MASTER:
                        master_target = r["target"]
                        break
                if master_target != f"../slideMasters/slideMaster{master_num}.xml":
                    continue
            src_file = f
            break

    if not src_file:
        _die(f"layout {source_name!r} not found")

    # Copy layout file
    new_num = _next_part_number(staged, "ppt/slideLayouts", "slideLayout")
    new_file = f"slideLayout{new_num}.xml"
    src_full = os.path.join(layouts_dir, src_file)
    new_full = os.path.join(layouts_dir, new_file)
    shutil.copy2(src_full, new_full)

    # Update the name in the new file
    root = _parse_xml(new_full)
    csld = root.find(f"{{{NS_P}}}cSld")
    if csld is not None:
        csld.set("name", new_name)
    _write_xml(root, new_full)

    # Copy .rels
    src_rels = os.path.join(layouts_dir, "_rels", src_file + ".rels")
    new_rels = os.path.join(layouts_dir, "_rels", new_file + ".rels")
    if os.path.isfile(src_rels):
        os.makedirs(os.path.dirname(new_rels), exist_ok=True)
        shutil.copy2(src_rels, new_rels)

    # Find the master that owns the source layout and add the new layout
    master_file = None
    master_part = None
    src_layout_rels = _get_rels(staged, f"ppt/slideLayouts/{src_file}")
    for r in src_layout_rels:
        if r["type"] == RT_SLIDE_MASTER:
            master_file = os.path.basename(r["target"])
            master_part = f"ppt/slideMasters/{master_file}"
            break

    if master_part:
        new_rid = _add_rel(staged, master_part, RT_SLIDE_LAYOUT, f"../slideLayouts/{new_file}")
        # Add to master's sldLayoutIdLst
        master_path = os.path.join(staged, master_part)
        master_root = _parse_xml(master_path)
        lst = master_root.find(f"{{{NS_P}}}sldLayoutIdLst")
        if lst is None:
            lst = etree.SubElement(master_root, f"{{{NS_P}}}sldLayoutIdLst")
        # Find a unique id
        existing_ids = set()
        for entry in lst.findall(f"{{{NS_P}}}sldLayoutId"):
            existing_ids.add(int(entry.get("id", "0")))
        new_layout_id = max(existing_ids) + 1 if existing_ids else 2147483649
        etree.SubElement(lst, f"{{{NS_P}}}sldLayoutId", attrib={
            "id": str(new_layout_id),
            f"{{{NS_R}}}id": new_rid,
        })
        _write_xml(master_root, master_path)

    _add_content_type_override(staged, f"/ppt/slideLayouts/{new_file}", CT_SLIDE_LAYOUT)

    print(json.dumps({
        "duplicated": "layout",
        "source": source_name,
        "name": new_name,
        "file": new_file,
        "staged": staged,
    }))


def cmd_duplicate_master(args):
    staged = _resolve_staged_or_file(args.file)
    n = args.master
    new_name = args.name

    master_file = f"slideMaster{n}.xml"
    master_part = f"ppt/slideMasters/{master_file}"
    master_path = os.path.join(staged, master_part)

    if not os.path.isfile(master_path):
        _die(f"master {n} not found")

    # Copy master file
    new_num = _next_part_number(staged, "ppt/slideMasters", "slideMaster")
    new_master_file = f"slideMaster{new_num}.xml"
    new_master_part = f"ppt/slideMasters/{new_master_file}"
    new_master_path = os.path.join(staged, new_master_part)
    shutil.copy2(master_path, new_master_path)

    # Update name
    root = _parse_xml(new_master_path)
    csld = root.find(f"{{{NS_P}}}cSld")
    if csld is not None:
        csld.set("name", new_name)
    _write_xml(root, new_master_path)

    # Copy master .rels
    src_rels = os.path.join(staged, "ppt", "slideMasters", "_rels", master_file + ".rels")
    new_rels = os.path.join(staged, "ppt", "slideMasters", "_rels", new_master_file + ".rels")
    if os.path.isfile(src_rels):
        os.makedirs(os.path.dirname(new_rels), exist_ok=True)
        shutil.copy2(src_rels, new_rels)

    # Duplicate all owned layouts and remap
    old_master_rels = _get_rels(staged, master_part)
    layout_map = {}  # old_target -> new_target

    for r in old_master_rels:
        if r["type"] == RT_SLIDE_LAYOUT:
            old_layout_file = os.path.basename(r["target"])
            new_layout_num = _next_part_number(staged, "ppt/slideLayouts", "slideLayout")
            new_layout_file = f"slideLayout{new_layout_num}.xml"

            # Copy layout file
            src_layout = os.path.join(staged, "ppt", "slideLayouts", old_layout_file)
            dst_layout = os.path.join(staged, "ppt", "slideLayouts", new_layout_file)
            if os.path.isfile(src_layout):
                shutil.copy2(src_layout, dst_layout)

            # Copy layout .rels and update master reference
            src_layout_rels = os.path.join(staged, "ppt", "slideLayouts", "_rels", old_layout_file + ".rels")
            dst_layout_rels = os.path.join(staged, "ppt", "slideLayouts", "_rels", new_layout_file + ".rels")
            if os.path.isfile(src_layout_rels):
                os.makedirs(os.path.dirname(dst_layout_rels), exist_ok=True)
                shutil.copy2(src_layout_rels, dst_layout_rels)
                # Update the master reference in the new layout's .rels
                rels_root = _parse_xml(dst_layout_rels)
                for rel_el in rels_root.findall(f"{{{NS_REL}}}Relationship"):
                    if rel_el.get("Type") == RT_SLIDE_MASTER:
                        rel_el.set("Target", f"../slideMasters/{new_master_file}")
                _write_xml(rels_root, dst_layout_rels)

            layout_map[r["target"]] = f"../slideLayouts/{new_layout_file}"
            _add_content_type_override(staged, f"/ppt/slideLayouts/{new_layout_file}", CT_SLIDE_LAYOUT)

    # Update new master's .rels: remap layout targets
    if os.path.isfile(new_rels):
        rels_root = _parse_xml(new_rels)
        for rel_el in rels_root.findall(f"{{{NS_REL}}}Relationship"):
            old_target = rel_el.get("Target")
            if old_target in layout_map:
                rel_el.set("Target", layout_map[old_target])
        _write_xml(rels_root, new_rels)

    # Update new master's sldLayoutIdLst with new rIds
    new_master_root = _parse_xml(new_master_path)
    lst = new_master_root.find(f"{{{NS_P}}}sldLayoutIdLst")
    if lst is not None:
        # Re-read the updated rels to get correct rId mapping
        new_master_rels = _get_rels(staged, new_master_part)
        layout_rid_map = {}
        for r in new_master_rels:
            if r["type"] == RT_SLIDE_LAYOUT:
                layout_rid_map[r["target"]] = r["id"]
        # Update existing entries
        for entry in lst.findall(f"{{{NS_P}}}sldLayoutId"):
            old_rid = entry.get(f"{{{NS_R}}}id")
            # Find what the old rid pointed to in original rels and map to new
            for r in old_master_rels:
                if r["id"] == old_rid and r["target"] in layout_map:
                    new_target = layout_map[r["target"]]
                    if new_target in layout_rid_map:
                        entry.set(f"{{{NS_R}}}id", layout_rid_map[new_target])
                    break
    _write_xml(new_master_root, new_master_path)

    # Add new master to presentation.xml.rels
    new_rid = _add_rel(staged, "ppt/presentation.xml", RT_SLIDE_MASTER,
                        f"slideMasters/{new_master_file}")

    # Add to presentation.xml sldMasterIdLst
    pres_root = _parse_xml(_pres_path(staged))
    master_id_lst = pres_root.find(f"{{{NS_P}}}sldMasterIdLst")
    if master_id_lst is None:
        master_id_lst = etree.SubElement(pres_root, f"{{{NS_P}}}sldMasterIdLst")
    existing_ids = set()
    for entry in master_id_lst.findall(f"{{{NS_P}}}sldMasterId"):
        existing_ids.add(int(entry.get("id", "0")))
    new_master_id = max(existing_ids) + 1 if existing_ids else 2147483648
    etree.SubElement(master_id_lst, f"{{{NS_P}}}sldMasterId", attrib={
        "id": str(new_master_id),
        f"{{{NS_R}}}id": new_rid,
    })
    _write_xml(pres_root, _pres_path(staged))

    _add_content_type_override(staged, f"/ppt/slideMasters/{new_master_file}", CT_SLIDE_MASTER)

    print(json.dumps({
        "duplicated": "master",
        "source_master": n,
        "new_file": new_master_file,
        "new_name": new_name,
        "duplicated_layouts": list(layout_map.values()),
        "staged": staged,
    }))


# ── Multi-file mutations: add ──

def cmd_add_layout(args):
    staged = _resolve_staged_or_file(args.file)
    layout_name = args.name
    master_num = args.master

    master_file = f"slideMaster{master_num}.xml"
    master_part = f"ppt/slideMasters/{master_file}"
    master_path = os.path.join(staged, master_part)

    if not os.path.isfile(master_path):
        _die(f"master {master_num} not found")

    # Create a minimal layout XML
    new_num = _next_part_number(staged, "ppt/slideLayouts", "slideLayout")
    new_file = f"slideLayout{new_num}.xml"
    new_path = os.path.join(staged, "ppt", "slideLayouts", new_file)

    nsmap = {
        "a": NS_A,
        "r": NS_R,
        "p": NS_P,
    }
    root = etree.Element(f"{{{NS_P}}}sldLayout", nsmap=nsmap)
    root.set("type", "blank")
    root.set("preserve", "1")
    csld = etree.SubElement(root, f"{{{NS_P}}}cSld", name=layout_name)
    sp_tree = etree.SubElement(csld, f"{{{NS_P}}}spTree")
    nv_grp = etree.SubElement(sp_tree, f"{{{NS_P}}}nvGrpSpPr")
    c_nv_pr = etree.SubElement(nv_grp, f"{{{NS_P}}}cNvPr", id="1", name="")
    etree.SubElement(nv_grp, f"{{{NS_P}}}cNvGrpSpPr")
    etree.SubElement(nv_grp, f"{{{NS_P}}}nvPr")
    etree.SubElement(sp_tree, f"{{{NS_P}}}grpSpPr")

    os.makedirs(os.path.dirname(new_path), exist_ok=True)
    _write_xml(root, new_path)

    # Create .rels for the layout pointing to the master
    _add_rel(staged, f"ppt/slideLayouts/{new_file}", RT_SLIDE_MASTER,
             f"../slideMasters/{master_file}")

    # Add to master's .rels
    new_rid = _add_rel(staged, master_part, RT_SLIDE_LAYOUT, f"../slideLayouts/{new_file}")

    # Add to master's sldLayoutIdLst
    master_root = _parse_xml(master_path)
    lst = master_root.find(f"{{{NS_P}}}sldLayoutIdLst")
    if lst is None:
        lst = etree.SubElement(master_root, f"{{{NS_P}}}sldLayoutIdLst")
    existing_ids = set()
    for entry in lst.findall(f"{{{NS_P}}}sldLayoutId"):
        existing_ids.add(int(entry.get("id", "0")))
    new_layout_id = max(existing_ids) + 1 if existing_ids else 2147483649
    etree.SubElement(lst, f"{{{NS_P}}}sldLayoutId", attrib={
        "id": str(new_layout_id),
        f"{{{NS_R}}}id": new_rid,
    })
    _write_xml(master_root, master_path)

    _add_content_type_override(staged, f"/ppt/slideLayouts/{new_file}", CT_SLIDE_LAYOUT)

    print(json.dumps({
        "added": "layout",
        "name": layout_name,
        "file": new_file,
        "master": master_num,
        "staged": staged,
    }))
