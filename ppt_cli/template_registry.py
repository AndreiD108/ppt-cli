"""Template registry: platform-specific directory, registry.json CRUD."""

import json
import os
import re
import sys
from datetime import datetime, timezone

import yaml


def _template_dir():
    """Return the template directory path, respecting PPT_CLI_TEMPLATE_DIR env var."""
    override = os.environ.get("PPT_CLI_TEMPLATE_DIR")
    if override:
        return override
    if sys.platform == "darwin":
        return os.path.expanduser("~/Library/Application Support/ppt-cli/templates")
    return os.path.expanduser("~/.config/ppt-cli/templates")


def _ensure_template_dir():
    """Create the template directory if it doesn't exist. Returns the path."""
    d = _template_dir()
    os.makedirs(d, exist_ok=True)
    return d


def _registry_path():
    return os.path.join(_template_dir(), "registry.json")


def _load_registry():
    """Load registry.json. Returns a dict with version, default, templates."""
    path = _registry_path()
    if not os.path.isfile(path):
        return {"version": 1, "default": None, "templates": {}}
    with open(path) as f:
        return json.load(f)


def _save_registry(registry):
    """Save registry.json."""
    _ensure_template_dir()
    path = _registry_path()
    with open(path, "w") as f:
        json.dump(registry, f, indent=2)


def _validate_template_name(name):
    """Validate template name is kebab-case. Returns True or raises ValueError."""
    if not re.match(r"^[a-z0-9]+(-[a-z0-9]+)*$", name):
        raise ValueError(
            f"invalid template name: {name!r} "
            "(must be kebab-case: lowercase letters, digits, hyphens)"
        )
    return True


def _save_to_registry(name):
    """Add or update a template in the registry."""
    registry = _load_registry()
    now = datetime.now(timezone.utc).isoformat()
    if name in registry["templates"]:
        registry["templates"][name]["updated"] = now
    else:
        registry["templates"][name] = {
            "created": now,
            "updated": now,
        }
    _save_registry(registry)


def _get_template_dir_path(name):
    """Return <template_dir>/<name>/."""
    return os.path.join(_template_dir(), name)


def _get_template_path(name):
    """Get the full path to a template's .pptx file. Returns None if not found."""
    path = os.path.join(_template_dir(), name, "template.pptx")
    if os.path.isfile(path):
        return path
    return None


def _get_design_system_path(name):
    """Return <template_dir>/<name>/design-system.yaml."""
    return os.path.join(_template_dir(), name, "design-system.yaml")


def _read_description_from_yaml(yaml_path):
    """Read description field from a design-system.yaml. Returns str or None."""
    if not os.path.isfile(yaml_path):
        return None
    with open(yaml_path) as f:
        data = yaml.safe_load(f)
    if not isinstance(data, dict):
        return None
    return data.get("description")


def _validate_design_system(tmpl_dir_path):
    """Validate design-system.yaml in a template directory.

    Returns list of error strings (empty = valid).
    """
    errors = []
    yaml_path = os.path.join(tmpl_dir_path, "design-system.yaml")
    if not os.path.isfile(yaml_path):
        errors.append("design-system.yaml not found")
        return errors

    with open(yaml_path) as f:
        raw = f.read()

    try:
        data = yaml.safe_load(raw)
    except yaml.YAMLError as e:
        errors.append(f"invalid YAML: {e}")
        return errors

    if not isinstance(data, dict):
        errors.append("design-system.yaml must be a YAML mapping")
        return errors

    if not data.get("description"):
        errors.append("design-system.yaml missing required 'description' field")

    # Check that all PNGs in screenshots/ are referenced in yaml text
    screenshots_dir = os.path.join(tmpl_dir_path, "screenshots")
    if os.path.isdir(screenshots_dir):
        pngs = [f for f in os.listdir(screenshots_dir) if f.endswith(".png")]
        for png in pngs:
            if png not in raw:
                errors.append(f"screenshot {png!r} not referenced in design-system.yaml")

    return errors


def _slugify_layout_name(name):
    """'Title Slide' -> 'title-slide' for screenshot filenames."""
    slug = name.lower().strip()
    slug = re.sub(r"[^a-z0-9]+", "-", slug)
    slug = slug.strip("-")
    return slug or "unnamed"


def _get_default_template():
    """Get the default template name, or None."""
    registry = _load_registry()
    return registry.get("default")
