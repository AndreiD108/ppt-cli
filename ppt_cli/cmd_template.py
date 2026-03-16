"""Template command handlers: prepare, save, list, show, delete, rename, default, update-design-system, export, import."""

import json
import os
import shutil
import subprocess
import tempfile
import zipfile

from .helpers import _die, _find_libreoffice_optional, Presentation
from .template_registry import (
    _template_dir, _ensure_template_dir, _load_registry, _save_registry,
    _validate_template_name, _save_to_registry, _get_template_path,
    _get_template_dir_path, _get_design_system_path,
    _read_description_from_yaml, _validate_design_system, _slugify_layout_name,
)


def _pptx_to_pdf(lo, snap, pptx_path):
    """Convert a pptx to PDF via LibreOffice. Returns (pdf_path, work_dir) or (None, None)."""
    abs_file = os.path.abspath(pptx_path)

    if snap:
        work_dir = os.path.expanduser("~/snap/libreoffice/common/.ppt-cli-tmp")
        os.makedirs(work_dir, exist_ok=True)
        src_copy = os.path.join(work_dir, os.path.basename(abs_file))
        shutil.copy2(abs_file, src_copy)
        convert_src = src_copy
    else:
        work_dir = tempfile.mkdtemp()
        convert_src = abs_file

    r = subprocess.run(
        [lo, "--headless", "--convert-to", "pdf",
         "--outdir", work_dir, convert_src],
        capture_output=True,
    )
    if r.returncode != 0:
        shutil.rmtree(work_dir, ignore_errors=True)
        return None, None

    pdfs = [f for f in os.listdir(work_dir) if f.endswith(".pdf")]
    if not pdfs:
        shutil.rmtree(work_dir, ignore_errors=True)
        return None, None

    return os.path.join(work_dir, pdfs[0]), work_dir


def _extract_slides_from_pdf(pdf_path, slide_specs, screenshots_dir, dpi=150):
    """Extract multiple slides from a PDF. slide_specs: list of (slide_num, filename).
    Returns list of generated filenames."""
    generated = []
    for slide_num, filename in slide_specs:
        output = os.path.join(screenshots_dir, filename)
        out_stem = os.path.splitext(output)[0]
        try:
            r = subprocess.run(
                ["pdftoppm", "-png", "-singlefile",
                 "-f", str(slide_num), "-l", str(slide_num),
                 "-r", str(dpi), pdf_path, out_stem],
                capture_output=True,
            )
            if r.returncode == 0:
                generated.append(filename)
        except FileNotFoundError:
            return generated
    return generated


def _generate_screenshots(lo, snap, pptx_path, screenshots_dir, dpi=150):
    """Generate layout and existing-slide screenshots. Returns list of generated filenames.

    Single LibreOffice invocation: copies the pptx, appends one slide per layout
    at the end, converts to PDF once, then extracts all slides via pdftoppm.
    """
    generated = []
    prs = Presentation(pptx_path)
    existing_count = len(prs.slides)

    # Build a combined pptx: existing slides + one per layout
    tmp_dir = tempfile.mkdtemp()
    try:
        combined_pptx = os.path.join(tmp_dir, "combined.pptx")
        combined = Presentation(pptx_path)
        layout_names = []
        for layout in combined.slide_layouts:
            combined.slides.add_slide(layout)
            layout_names.append(layout.name)
        combined.save(combined_pptx)

        pdf_path, pdf_work_dir = _pptx_to_pdf(lo, snap, combined_pptx)
        if not pdf_path:
            return generated

        try:
            specs = []
            # Existing slides
            for i in range(1, existing_count + 1):
                slide = prs.slides[i - 1]
                slug = _slugify_layout_name(slide.slide_layout.name)
                specs.append((i, f"slide-{i}-{slug}.png"))
            # Layout showcase slides (after existing)
            for j, name in enumerate(layout_names):
                slug = _slugify_layout_name(name)
                specs.append((existing_count + j + 1, f"layout-{slug}.png"))
            generated = _extract_slides_from_pdf(pdf_path, specs, screenshots_dir, dpi)
        finally:
            shutil.rmtree(pdf_work_dir, ignore_errors=True)
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)

    return generated


def cmd_template_prepare(args):
    name = args.name
    try:
        _validate_template_name(name)
    except ValueError as e:
        _die(str(e))

    if not os.path.isfile(args.file):
        _die(f"file not found: {args.file}")

    tmpl_dir = _ensure_template_dir()
    dest_dir = os.path.join(tmpl_dir, name)

    if os.path.exists(dest_dir):
        _die(f"template directory {name!r} already exists")

    # Create directory structure
    os.makedirs(dest_dir)
    screenshots_dir = os.path.join(dest_dir, "screenshots")
    os.makedirs(screenshots_dir)

    # Copy pptx
    pptx_dest = os.path.join(dest_dir, "template.pptx")
    shutil.copy2(args.file, pptx_dest)

    # Get layout info
    prs = Presentation(pptx_dest)
    layout_names = [sl.name for sl in prs.slide_layouts]
    slide_count = len(prs.slides)

    # Generate screenshots (graceful degradation; skip if PPT_CLI_NO_SCREENSHOTS set)
    screenshots = []
    lo, snap = (None, None) if os.environ.get("PPT_CLI_NO_SCREENSHOTS") else _find_libreoffice_optional()
    if lo:
        screenshots = _generate_screenshots(lo, snap, pptx_dest, screenshots_dir)

    result = {
        "prepared": name,
        "template_dir": dest_dir,
        "template_pptx": pptx_dest,
        "screenshots_dir": screenshots_dir,
        "design_system_path": os.path.join(dest_dir, "design-system.yaml"),
        "layouts": layout_names,
        "layout_count": len(layout_names),
        "slide_count": slide_count,
        "screenshots": screenshots,
    }
    print(json.dumps(result, indent=2))


def cmd_template_save(args):
    name = args.name
    try:
        _validate_template_name(name)
    except ValueError as e:
        _die(str(e))

    tmpl_dir = _ensure_template_dir()
    dest_dir = os.path.join(tmpl_dir, name)

    # Validate prepared directory
    if not os.path.isdir(dest_dir):
        _die(f"template directory {name!r} not found (run 'template prepare' first)")

    pptx_path = os.path.join(dest_dir, "template.pptx")
    if not os.path.isfile(pptx_path):
        _die(f"template.pptx not found in {dest_dir}")

    # Validate design system
    errors = _validate_design_system(dest_dir)
    if errors:
        _die("design-system.yaml validation failed:\n  " + "\n  ".join(errors))

    # Register
    _save_to_registry(name)

    # Get layout info
    prs = Presentation(pptx_path)
    layout_names = [sl.name for sl in prs.slide_layouts]
    desc = _read_description_from_yaml(os.path.join(dest_dir, "design-system.yaml"))

    print(json.dumps({
        "saved_template": name,
        "path": pptx_path,
        "description": desc or "",
        "layouts": layout_names,
        "layout_count": len(layout_names),
    }))


def cmd_template_list(args):
    registry = _load_registry()
    templates = registry.get("templates", {})
    default = registry.get("default")

    if getattr(args, "json", False):
        items = []
        for name, entry in sorted(templates.items()):
            item = {"name": name, **entry, "is_default": name == default}
            yaml_path = _get_design_system_path(name)
            item["description"] = _read_description_from_yaml(yaml_path) or ""
            item["design_system_path"] = yaml_path if os.path.isfile(yaml_path) else None
            # Add layout count
            path = _get_template_path(name)
            if path and os.path.isfile(path):
                try:
                    prs = Presentation(path)
                    item["layout_count"] = len(list(prs.slide_layouts))
                except Exception:
                    item["layout_count"] = None
            items.append(item)
        print(json.dumps(items, indent=2))
    else:
        if not templates:
            print("No templates saved. Use 'ppt-cli template prepare' to start.")
            return
        for name, entry in sorted(templates.items()):
            marker = " [default]" if name == default else ""
            yaml_path = _get_design_system_path(name)
            desc = _read_description_from_yaml(yaml_path) or ""
            desc_str = f"  {desc}" if desc else ""
            # Get layout count
            layout_info = ""
            path = _get_template_path(name)
            if path and os.path.isfile(path):
                try:
                    prs = Presentation(path)
                    count = len(list(prs.slide_layouts))
                    layout_info = f"  ({count} layouts)"
                except Exception:
                    pass
            print(f"  {name}{marker}{desc_str}{layout_info}")
            if os.path.isfile(yaml_path):
                print(f"    {yaml_path}")


def cmd_template_show(args):
    name = args.name
    registry = _load_registry()

    if name not in registry.get("templates", {}):
        _die(f"template {name!r} not found")

    entry = registry["templates"][name]
    path = _get_template_path(name)
    is_default = registry.get("default") == name
    yaml_path = _get_design_system_path(name)

    desc = _read_description_from_yaml(yaml_path) or ""

    result = {
        "name": name,
        "path": path,
        "description": desc,
        "design_system_path": yaml_path if os.path.isfile(yaml_path) else None,
        "is_default": is_default,
        "created": entry.get("created"),
        "updated": entry.get("updated"),
    }

    if path and os.path.isfile(path):
        try:
            prs = Presentation(path)
            layouts = []
            for sl in prs.slide_layouts:
                layout_info = {"name": sl.name, "placeholders": []}
                for ph in sl.placeholders:
                    layout_info["placeholders"].append({
                        "idx": ph.placeholder_format.idx,
                        "type": str(ph.placeholder_format.type),
                        "name": ph.name,
                    })
                layouts.append(layout_info)
            result["layouts"] = layouts
        except Exception as e:
            result["error"] = str(e)

    print(json.dumps(result, indent=2))


def cmd_template_delete(args):
    name = args.name
    registry = _load_registry()

    if name not in registry.get("templates", {}):
        _die(f"template {name!r} not found")

    tmpl_dir_path = _get_template_dir_path(name)
    if os.path.isdir(tmpl_dir_path):
        shutil.rmtree(tmpl_dir_path)

    # Remove from registry
    del registry["templates"][name]

    # Unset default if this was the default
    if registry.get("default") == name:
        registry["default"] = None

    _save_registry(registry)
    print(json.dumps({"deleted_template": name}))


def cmd_template_rename(args):
    old_name = args.old
    new_name = args.new
    registry = _load_registry()

    if old_name not in registry.get("templates", {}):
        _die(f"template {old_name!r} not found")

    try:
        _validate_template_name(new_name)
    except ValueError as e:
        _die(str(e))

    if new_name in registry["templates"] and new_name != old_name:
        _die(f"template {new_name!r} already exists")

    entry = registry["templates"].pop(old_name)

    tmpl_base = _template_dir()
    old_dir = os.path.join(tmpl_base, old_name)
    new_dir = os.path.join(tmpl_base, new_name)
    if os.path.isdir(old_dir):
        os.rename(old_dir, new_dir)

    registry["templates"][new_name] = entry

    # Update default if needed
    if registry.get("default") == old_name:
        registry["default"] = new_name

    _save_registry(registry)
    print(json.dumps({"renamed": old_name, "to": new_name}))


def cmd_template_update_design_system(args):
    name = args.name
    registry = _load_registry()

    if name not in registry.get("templates", {}):
        _die(f"template {name!r} not found")

    yaml_file = args.yaml_file
    if not os.path.isfile(yaml_file):
        _die(f"file not found: {yaml_file}")

    # Parse and validate
    import yaml
    with open(yaml_file) as f:
        try:
            data = yaml.safe_load(f.read())
        except yaml.YAMLError as e:
            _die(f"invalid YAML: {e}")

    if not isinstance(data, dict) or not data.get("description"):
        _die("design-system.yaml must have a 'description' field")

    # Copy to template directory
    dest = _get_design_system_path(name)
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    shutil.copy2(yaml_file, dest)

    # Update registry timestamp
    from datetime import datetime, timezone
    registry["templates"][name]["updated"] = datetime.now(timezone.utc).isoformat()
    _save_registry(registry)

    print(json.dumps({
        "updated_design_system": name,
        "design_system_path": dest,
        "description": data.get("description", ""),
    }))


def cmd_template_default(args):
    registry = _load_registry()

    if args.unset:
        registry["default"] = None
        _save_registry(registry)
        print(json.dumps({"default": None}))
        return

    if args.name:
        name = args.name
        if name not in registry.get("templates", {}):
            _die(f"template {name!r} not found")
        registry["default"] = name
        _save_registry(registry)
        print(json.dumps({"default": name}))
    else:
        default = registry.get("default")
        print(json.dumps({"default": default}))


def cmd_template_export(args):
    name = args.name
    registry = _load_registry()

    if name not in registry.get("templates", {}):
        _die(f"template {name!r} not found")

    tmpl_dir_path = _get_template_dir_path(name)
    if not os.path.isdir(tmpl_dir_path):
        _die(f"template directory {name!r} not found")

    output = args.output or os.path.join(os.getcwd(), f"{name}.zip")
    output = os.path.abspath(output)

    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, _dirs, files in os.walk(tmpl_dir_path):
            for fname in files:
                full = os.path.join(root, fname)
                arcname = os.path.join(name, os.path.relpath(full, tmpl_dir_path))
                zf.write(full, arcname)

    size = os.path.getsize(output)
    print(json.dumps({"exported": name, "output": output, "size": size}))


def cmd_template_import(args):
    zip_path = args.zip_path
    if not os.path.isfile(zip_path):
        _die(f"file not found: {zip_path}")

    if not zipfile.is_zipfile(zip_path):
        _die(f"not a valid zip file: {zip_path}")

    with zipfile.ZipFile(zip_path, "r") as zf:
        names = zf.namelist()
        if not names:
            _die("zip file is empty")

        # Find common top-level directory
        top_dirs = set()
        for n in names:
            parts = n.split("/")
            if parts[0]:
                top_dirs.add(parts[0])
        if len(top_dirs) != 1:
            _die("zip must contain a single top-level directory")
        original_name = top_dirs.pop()

    target_name = args.name or original_name

    try:
        _validate_template_name(target_name)
    except ValueError as e:
        _die(str(e))

    tmpl_base = _ensure_template_dir()
    dest_dir = os.path.join(tmpl_base, target_name)

    if os.path.exists(dest_dir):
        _die(f"template {target_name!r} already exists")

    # Extract to temp dir first to avoid partial state on error
    tmp_dir = tempfile.mkdtemp()
    try:
        with zipfile.ZipFile(zip_path, "r") as zf:
            zf.extractall(tmp_dir)

        extracted = os.path.join(tmp_dir, original_name)
        if not os.path.isdir(extracted):
            _die("zip does not contain the expected directory structure")

        # Validate contents
        if not os.path.isfile(os.path.join(extracted, "template.pptx")):
            _die("zip missing required file: template.pptx")

        errors = _validate_design_system(extracted)
        if errors:
            _die("import validation failed:\n  " + "\n  ".join(errors))

        # Move into template dir
        shutil.move(extracted, dest_dir)
    except SystemExit:
        raise
    except Exception as e:
        _die(f"import failed: {e}")
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)

    # Register
    _save_to_registry(target_name)

    print(json.dumps({
        "imported": target_name,
        "template_dir": dest_dir,
        "original_name": original_name,
    }))
