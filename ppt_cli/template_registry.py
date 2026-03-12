"""Template registry: platform-specific directory, registry.json CRUD."""

import json
import os
import re
import sys
from datetime import datetime, timezone


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


def _save_to_registry(name, description, filename):
    """Add or update a template in the registry."""
    registry = _load_registry()
    now = datetime.now(timezone.utc).isoformat()
    if name in registry["templates"]:
        registry["templates"][name]["description"] = description
        registry["templates"][name]["filename"] = filename
        registry["templates"][name]["updated"] = now
    else:
        registry["templates"][name] = {
            "description": description,
            "filename": filename,
            "created": now,
            "updated": now,
        }
    _save_registry(registry)


def _get_template_path(name):
    """Get the full path to a template's .pptx file. Returns None if not found."""
    registry = _load_registry()
    entry = registry["templates"].get(name)
    if not entry:
        return None
    return os.path.join(_template_dir(), entry["filename"])


def _get_default_template():
    """Get the default template name, or None."""
    registry = _load_registry()
    return registry.get("default")
