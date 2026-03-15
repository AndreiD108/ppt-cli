"""Template command handlers: save, list, show, delete, rename, default."""

import json
import os
import shutil

from .helpers import _die, Presentation
from .template_registry import (
    _template_dir, _ensure_template_dir, _load_registry, _save_registry,
    _validate_template_name, _save_to_registry, _get_template_path,
)


def cmd_template_save(args):
    name = args.name
    try:
        _validate_template_name(name)
    except ValueError as e:
        _die(str(e))

    if not os.path.isfile(args.file):
        _die(f"file not found: {args.file}")

    tmpl_dir = _ensure_template_dir()
    filename = f"{name}.pptx"
    dest = os.path.join(tmpl_dir, filename)

    if os.path.isfile(dest) and not args.force:
        _die(f"template {name!r} already exists (use -f to overwrite)")

    shutil.copy2(args.file, dest)
    _save_to_registry(name, args.description or "", filename)

    # Print layout summary
    prs = Presentation(dest)
    layout_names = [sl.name for sl in prs.slide_layouts]
    print(json.dumps({
        "saved_template": name,
        "path": dest,
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
            print("No templates saved. Use 'ppt-cli template save' to add one.")
            print("Use 'ppt-cli internals' to extract and edit template XML directly.")
            return
        for name, entry in sorted(templates.items()):
            marker = " [default]" if name == default else ""
            desc = entry.get("description", "")
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


def cmd_template_show(args):
    name = args.name
    registry = _load_registry()

    if name not in registry.get("templates", {}):
        _die(f"template {name!r} not found")

    entry = registry["templates"][name]
    path = _get_template_path(name)
    is_default = registry.get("default") == name

    result = {
        "name": name,
        "path": path,
        "description": entry.get("description", ""),
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

    entry = registry["templates"][name]
    path = _get_template_path(name)

    # Remove file
    if path and os.path.isfile(path):
        os.remove(path)

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

    # Rename file
    tmpl_dir = _template_dir()
    old_path = os.path.join(tmpl_dir, entry["filename"])
    new_filename = f"{new_name}.pptx"
    new_path = os.path.join(tmpl_dir, new_filename)
    if os.path.isfile(old_path):
        os.rename(old_path, new_path)
    entry["filename"] = new_filename

    if args.description is not None:
        entry["description"] = args.description

    registry["templates"][new_name] = entry

    # Update default if needed
    if registry.get("default") == old_name:
        registry["default"] = new_name

    _save_registry(registry)
    print(json.dumps({"renamed": old_name, "to": new_name}))


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
