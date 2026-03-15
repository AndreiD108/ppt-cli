"""Low-level OOXML primitives for manipulating extracted .pptx contents."""

import os
import re
import zipfile

from lxml import etree

# ── Namespace constants ──
NS_A = "http://schemas.openxmlformats.org/drawingml/2006/main"
NS_R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
NS_P = "http://schemas.openxmlformats.org/presentationml/2006/main"
NS_CT = "http://schemas.openxmlformats.org/package/2006/content-types"
NS_REL = "http://schemas.openxmlformats.org/package/2006/relationships"

# Relationship type URIs
RT_SLIDE = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide"
RT_SLIDE_LAYOUT = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout"
RT_SLIDE_MASTER = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideMaster"
RT_THEME = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/theme"
RT_NOTES_SLIDE = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/notesSlide"

# Content types
CT_SLIDE = "application/vnd.openxmlformats-officedocument.presentationml.slide+xml"
CT_SLIDE_LAYOUT = "application/vnd.openxmlformats-officedocument.presentationml.slideLayout+xml"
CT_SLIDE_MASTER = "application/vnd.openxmlformats-officedocument.presentationml.slideMaster+xml"
CT_NOTES_SLIDE = "application/vnd.openxmlformats-officedocument.presentationml.notesSlide+xml"
CT_THEME = "application/vnd.openxmlformats-officedocument.theme+xml"


# ── XML read/write ──

def _parse_xml(path):
    """Parse an XML file, return lxml Element."""
    parser = etree.XMLParser(remove_blank_text=False)
    return etree.parse(path, parser).getroot()


def _write_xml(root, path):
    """Write an lxml Element tree to a file."""
    tree = root if isinstance(root, etree._ElementTree) else root.getroottree()
    tree.write(path, xml_declaration=True, encoding="UTF-8", standalone=True)


# ── .rels helpers ──

def _rels_path_for(xml_path):
    """Compute the .rels path for a given XML file path.

    e.g. 'ppt/presentation.xml' -> 'ppt/_rels/presentation.xml.rels'
    """
    d = os.path.dirname(xml_path)
    f = os.path.basename(xml_path)
    return os.path.join(d, "_rels", f + ".rels")


def _get_rels(staged, part):
    """Get all relationships for a part. Returns list of {id, type, target}."""
    rels_file = os.path.join(staged, _rels_path_for(part))
    if not os.path.isfile(rels_file):
        return []
    root = _parse_xml(rels_file)
    result = []
    for rel in root.findall(f"{{{NS_REL}}}Relationship"):
        result.append({
            "id": rel.get("Id"),
            "type": rel.get("Type"),
            "target": rel.get("Target"),
        })
    return result


def _add_rel(staged, part, rel_type, target):
    """Add a relationship to a part's .rels file. Returns the new rId."""
    rels_file = os.path.join(staged, _rels_path_for(part))
    rels_dir = os.path.dirname(rels_file)
    os.makedirs(rels_dir, exist_ok=True)

    if os.path.isfile(rels_file):
        root = _parse_xml(rels_file)
    else:
        root = etree.Element(f"{{{NS_REL}}}Relationships")

    # Find next rId
    existing_ids = set()
    for rel in root.findall(f"{{{NS_REL}}}Relationship"):
        existing_ids.add(rel.get("Id"))
    n = 1
    while f"rId{n}" in existing_ids:
        n += 1
    new_id = f"rId{n}"

    etree.SubElement(root, f"{{{NS_REL}}}Relationship", attrib={
        "Id": new_id, "Type": rel_type, "Target": target,
    })
    _write_xml(root, rels_file)
    return new_id


def _remove_rel(staged, part, rid):
    """Remove a relationship by rId from a part's .rels file."""
    rels_file = os.path.join(staged, _rels_path_for(part))
    if not os.path.isfile(rels_file):
        return
    root = _parse_xml(rels_file)
    for rel in root.findall(f"{{{NS_REL}}}Relationship"):
        if rel.get("Id") == rid:
            root.remove(rel)
            break
    _write_xml(root, rels_file)


def _find_rel_by_target(staged, part, target):
    """Find a relationship by target path. Returns {id, type, target} or None."""
    for rel in _get_rels(staged, part):
        if rel["target"] == target:
            return rel
    return None


def _find_rel_by_type(staged, part, rel_type):
    """Find all relationships of a given type. Returns list of {id, type, target}."""
    return [r for r in _get_rels(staged, part) if r["type"] == rel_type]


# ── Content_Types helpers ──

def _content_types_path(staged):
    return os.path.join(staged, "[Content_Types].xml")


def _add_content_type_override(staged, part_name, content_type):
    """Add an Override element to [Content_Types].xml."""
    ct_path = _content_types_path(staged)
    root = _parse_xml(ct_path)
    # Check if override already exists
    for ov in root.findall(f"{{{NS_CT}}}Override"):
        if ov.get("PartName") == part_name:
            ov.set("ContentType", content_type)
            _write_xml(root, ct_path)
            return
    etree.SubElement(root, f"{{{NS_CT}}}Override", attrib={
        "PartName": part_name, "ContentType": content_type,
    })
    _write_xml(root, ct_path)


def _remove_content_type_override(staged, part_name):
    """Remove an Override element from [Content_Types].xml."""
    ct_path = _content_types_path(staged)
    root = _parse_xml(ct_path)
    for ov in root.findall(f"{{{NS_CT}}}Override"):
        if ov.get("PartName") == part_name:
            root.remove(ov)
            break
    _write_xml(root, ct_path)


# ── presentation.xml helpers ──

def _pres_path(staged):
    return os.path.join(staged, "ppt", "presentation.xml")


def _get_slide_ids(staged):
    """Get list of {id, rid} from presentation.xml sldIdLst."""
    root = _parse_xml(_pres_path(staged))
    sld_id_lst = root.find(f"{{{NS_P}}}sldIdLst")
    if sld_id_lst is None:
        return []
    result = []
    for sld_id in sld_id_lst.findall(f"{{{NS_P}}}sldId"):
        result.append({
            "id": sld_id.get("id"),
            "rid": sld_id.get(f"{{{NS_R}}}id"),
        })
    return result


def _next_slide_id(staged):
    """Return the next available slide id number."""
    ids = _get_slide_ids(staged)
    if not ids:
        return 256
    return max(int(s["id"]) for s in ids) + 1


# ── Part numbering ──

def _next_part_number(staged, subdir, prefix):
    """Scan dir for {prefix}N.xml, return max(N)+1."""
    d = os.path.join(staged, subdir)
    if not os.path.isdir(d):
        return 1
    pat = re.compile(rf"^{re.escape(prefix)}(\d+)\.xml$")
    nums = []
    for f in os.listdir(d):
        m = pat.match(f)
        if m:
            nums.append(int(m.group(1)))
    return max(nums) + 1 if nums else 1


# ── Build / validate ──

def _build_pptx(staged, output):
    """Build a .pptx from a staged directory."""
    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as zf:
        for dirpath, _dirs, files in os.walk(staged):
            for f in files:
                full = os.path.join(dirpath, f)
                arcname = os.path.relpath(full, staged)
                zf.write(full, arcname)


def _validate_staged(staged):
    """Check Content_Types overrides resolve, .rels targets exist. Returns list of warnings."""
    warnings = []
    ct_path = _content_types_path(staged)
    if not os.path.isfile(ct_path):
        warnings.append("[Content_Types].xml is missing")
        return warnings

    root = _parse_xml(ct_path)
    for ov in root.findall(f"{{{NS_CT}}}Override"):
        part_name = ov.get("PartName")
        # PartName is like /ppt/slides/slide1.xml — strip leading /
        rel_path = part_name.lstrip("/")
        full = os.path.join(staged, rel_path)
        if not os.path.isfile(full):
            warnings.append(f"Content_Types override target missing: {part_name}")

    # Check .rels targets
    for dirpath, _dirs, files in os.walk(staged):
        for f in files:
            if not f.endswith(".rels"):
                continue
            rels_full = os.path.join(dirpath, f)
            rels_root = _parse_xml(rels_full)
            rels_dir = os.path.dirname(rels_full)
            # .rels files are in _rels/ subdir; targets are relative to parent
            parent_dir = os.path.dirname(rels_dir)
            for rel in rels_root.findall(f"{{{NS_REL}}}Relationship"):
                target = rel.get("Target")
                if target and not target.startswith("http"):
                    target_full = os.path.normpath(os.path.join(parent_dir, target))
                    if not os.path.exists(target_full):
                        warnings.append(f"Broken rel in {os.path.relpath(rels_full, staged)}: {target}")

    return warnings


def _prune_unused(staged):
    """Remove unused layouts and orphaned media. Returns summary dict."""
    summary = {"removed_layouts": [], "removed_media": []}

    # Find which layouts are referenced by slides
    used_layouts = set()
    slides_dir = os.path.join(staged, "ppt", "slides")
    if os.path.isdir(slides_dir):
        for f in os.listdir(slides_dir):
            if f.startswith("slide") and f.endswith(".xml"):
                rels = _get_rels(staged, f"ppt/slides/{f}")
                for r in rels:
                    if r["type"] == RT_SLIDE_LAYOUT:
                        used_layouts.add(r["target"])

    # Find all layouts
    layouts_dir = os.path.join(staged, "ppt", "slideLayouts")
    if os.path.isdir(layouts_dir):
        for f in os.listdir(layouts_dir):
            if f.startswith("slideLayout") and f.endswith(".xml"):
                layout_part = f"ppt/slideLayouts/{f}"
                # The target in slide .rels is relative: ../slideLayouts/slideLayoutN.xml
                rel_target = f"../slideLayouts/{f}"
                if rel_target not in used_layouts:
                    # Remove layout file, its .rels, content type, and master references
                    _remove_layout_files(staged, f)
                    summary["removed_layouts"].append(f)

    # Find all referenced media
    referenced_media = set()
    for dirpath, _dirs, files in os.walk(staged):
        for fn in files:
            if not fn.endswith(".rels"):
                continue
            rels = _parse_xml(os.path.join(dirpath, fn))
            parent_dir = os.path.dirname(os.path.dirname(os.path.join(dirpath, fn)))
            for rel in rels.findall(f"{{{NS_REL}}}Relationship"):
                target = rel.get("Target", "")
                if "media/" in target:
                    full_target = os.path.normpath(os.path.join(parent_dir, target))
                    referenced_media.add(full_target)

    # Find all media files and remove unreferenced
    media_dir = os.path.join(staged, "ppt", "media")
    if os.path.isdir(media_dir):
        for f in os.listdir(media_dir):
            full = os.path.join(media_dir, f)
            if full not in referenced_media:
                os.remove(full)
                summary["removed_media"].append(f)

    return summary


def _remove_layout_files(staged, layout_filename):
    """Remove a layout file, its .rels, content type override, and master references."""
    layout_path = os.path.join(staged, "ppt", "slideLayouts", layout_filename)
    layout_rels = os.path.join(staged, "ppt", "slideLayouts", "_rels", layout_filename + ".rels")

    if os.path.isfile(layout_path):
        os.remove(layout_path)
    if os.path.isfile(layout_rels):
        os.remove(layout_rels)

    _remove_content_type_override(staged, f"/ppt/slideLayouts/{layout_filename}")

    # Remove from master .rels and master XML sldLayoutIdLst
    masters_dir = os.path.join(staged, "ppt", "slideMasters")
    if os.path.isdir(masters_dir):
        for mf in os.listdir(masters_dir):
            if mf.startswith("slideMaster") and mf.endswith(".xml"):
                master_part = f"ppt/slideMasters/{mf}"
                target = f"../slideLayouts/{layout_filename}"
                rel = _find_rel_by_target(staged, master_part, target)
                if rel:
                    _remove_rel(staged, master_part, rel["id"])
                    _remove_layout_from_master_xml(staged, master_part, rel["id"])


def _remove_layout_from_master_xml(staged, master_part, rid):
    """Remove sldLayoutId entry from master's sldLayoutIdLst."""
    master_path = os.path.join(staged, master_part)
    if not os.path.isfile(master_path):
        return
    root = _parse_xml(master_path)
    lst = root.find(f"{{{NS_P}}}sldLayoutIdLst")
    if lst is None:
        return
    for entry in lst.findall(f"{{{NS_P}}}sldLayoutId"):
        if entry.get(f"{{{NS_R}}}id") == rid:
            lst.remove(entry)
            break
    _write_xml(root, master_path)
