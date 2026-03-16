"""Tests for template commands and create --template integration."""

import json
import os
import zipfile


def _prepare_and_save(cli, tmpl_dir, name, src, description="Test template"):
    """Helper: prepare a template, write design-system.yaml, and save."""
    cli("template", "prepare", name, src)
    yaml_path = os.path.join(tmpl_dir, name, "design-system.yaml")
    screenshots_dir = os.path.join(tmpl_dir, name, "screenshots")
    # Reference any screenshots that exist so validation passes
    screenshot_refs = ""
    if os.path.isdir(screenshots_dir):
        for f in sorted(os.listdir(screenshots_dir)):
            if f.endswith(".png"):
                screenshot_refs += f"  - {f}\n"
    yaml_content = f"description: {description}\n"
    if screenshot_refs:
        yaml_content += f"screenshots:\n{screenshot_refs}"
    with open(yaml_path, "w") as f:
        f.write(yaml_content)
    return cli("template", "save", name)


def test_prepare_creates_directory(cli_with_template_dir, tmp_path):
    """Prepare creates directory structure and returns correct JSON."""
    cli, tmpl_dir = cli_with_template_dir

    src = str(tmp_path / "source.pptx")
    cli("create", src)

    rc, out, _ = cli("template", "prepare", "my-test", src)
    assert rc == 0
    data = json.loads(out)
    assert data["prepared"] == "my-test"
    assert os.path.isdir(data["template_dir"])
    assert os.path.isfile(data["template_pptx"])
    assert os.path.isdir(data["screenshots_dir"])
    assert data["layout_count"] > 0
    assert data["design_system_path"].endswith("design-system.yaml")


def test_prepare_errors_if_dir_exists(cli_with_template_dir, tmp_path):
    """Prepare errors if template directory already exists."""
    cli, tmpl_dir = cli_with_template_dir

    src = str(tmp_path / "source.pptx")
    cli("create", src)
    cli("template", "prepare", "exists-test", src)

    rc, _, err = cli("template", "prepare", "exists-test", src)
    assert rc != 0
    assert "already exists" in err


def test_save_validates_yaml_exists(cli_with_template_dir, tmp_path):
    """Save errors if design-system.yaml is missing."""
    cli, tmpl_dir = cli_with_template_dir

    src = str(tmp_path / "source.pptx")
    cli("create", src)
    cli("template", "prepare", "no-yaml", src)

    rc, _, err = cli("template", "save", "no-yaml")
    assert rc != 0
    assert "design-system.yaml" in err


def test_save_validates_description(cli_with_template_dir, tmp_path):
    """Save errors if description field is missing."""
    cli, tmpl_dir = cli_with_template_dir

    src = str(tmp_path / "source.pptx")
    cli("create", src)
    cli("template", "prepare", "no-desc", src)

    yaml_path = os.path.join(tmpl_dir, "no-desc", "design-system.yaml")
    with open(yaml_path, "w") as f:
        f.write("fonts:\n  heading: Arial\n")

    rc, _, err = cli("template", "save", "no-desc")
    assert rc != 0
    assert "description" in err


def test_save_validates_screenshot_references(cli_with_template_dir, tmp_path):
    """Save errors if screenshots exist but aren't referenced in yaml."""
    cli, tmpl_dir = cli_with_template_dir

    src = str(tmp_path / "source.pptx")
    cli("create", src)
    cli("template", "prepare", "unref-png", src)

    # Create a fake screenshot
    screenshots_dir = os.path.join(tmpl_dir, "unref-png", "screenshots")
    with open(os.path.join(screenshots_dir, "layout-fake.png"), "wb") as f:
        f.write(b"PNG")

    # Write yaml without referencing the screenshot
    yaml_path = os.path.join(tmpl_dir, "unref-png", "design-system.yaml")
    with open(yaml_path, "w") as f:
        f.write("description: Test\n")

    rc, _, err = cli("template", "save", "unref-png")
    assert rc != 0
    assert "layout-fake.png" in err


def test_save_succeeds_with_valid_prepare(cli_with_template_dir, tmp_path):
    """Full prepare + yaml + save workflow."""
    cli, tmpl_dir = cli_with_template_dir

    src = str(tmp_path / "source.pptx")
    cli("create", src)

    rc, out, _ = _prepare_and_save(cli, tmpl_dir, "full-test", src, "A full test")
    assert rc == 0
    data = json.loads(out)
    assert data["saved_template"] == "full-test"
    assert data["description"] == "A full test"
    assert data["layout_count"] > 0


def test_list_shows_yaml_path(cli_with_template_dir, tmp_path):
    """List shows two-line output with yaml path."""
    cli, tmpl_dir = cli_with_template_dir

    src = str(tmp_path / "source.pptx")
    cli("create", src)
    _prepare_and_save(cli, tmpl_dir, "listed", src, "Listed template")

    rc, out, _ = cli("template", "list")
    assert rc == 0
    assert "listed" in out
    assert "Listed template" in out
    assert "design-system.yaml" in out


def test_list_json_includes_design_system_path(cli_with_template_dir, tmp_path):
    """List --json includes design_system_path field."""
    cli, tmpl_dir = cli_with_template_dir

    src = str(tmp_path / "source.pptx")
    cli("create", src)
    _prepare_and_save(cli, tmpl_dir, "json-listed", src)

    rc, out, _ = cli("template", "list", "--json")
    assert rc == 0
    data = json.loads(out)
    assert len(data) == 1
    assert data[0]["name"] == "json-listed"
    assert data[0]["design_system_path"] is not None
    assert "design-system.yaml" in data[0]["design_system_path"]


def test_show_includes_design_system_path(cli_with_template_dir, tmp_path):
    """Show includes design_system_path."""
    cli, tmpl_dir = cli_with_template_dir

    src = str(tmp_path / "source.pptx")
    cli("create", src)
    _prepare_and_save(cli, tmpl_dir, "shown", src, "Shown template")

    rc, out, _ = cli("template", "show", "shown")
    assert rc == 0
    data = json.loads(out)
    assert data["name"] == "shown"
    assert data["description"] == "Shown template"
    assert data["design_system_path"] is not None
    assert "layouts" in data


def test_delete_removes_directory(cli_with_template_dir, tmp_path):
    """Delete removes entire template directory."""
    cli, tmpl_dir = cli_with_template_dir

    src = str(tmp_path / "source.pptx")
    cli("create", src)
    _prepare_and_save(cli, tmpl_dir, "to-delete", src)

    tmpl_dir_path = os.path.join(tmpl_dir, "to-delete")
    assert os.path.isdir(tmpl_dir_path)

    rc, out, _ = cli("template", "delete", "to-delete")
    assert rc == 0
    data = json.loads(out)
    assert data["deleted_template"] == "to-delete"
    assert not os.path.exists(tmpl_dir_path)

    # Verify it's gone from registry
    rc, _, _ = cli("template", "show", "to-delete")
    assert rc != 0


def test_rename_renames_directory(cli_with_template_dir, tmp_path):
    """Rename renames the template directory."""
    cli, tmpl_dir = cli_with_template_dir

    src = str(tmp_path / "source.pptx")
    cli("create", src)
    _prepare_and_save(cli, tmpl_dir, "old-name", src)

    rc, out, _ = cli("template", "rename", "old-name", "new-name")
    assert rc == 0
    data = json.loads(out)
    assert data["renamed"] == "old-name"
    assert data["to"] == "new-name"

    assert not os.path.exists(os.path.join(tmpl_dir, "old-name"))
    assert os.path.isdir(os.path.join(tmpl_dir, "new-name"))

    # Old name should be gone
    rc, _, _ = cli("template", "show", "old-name")
    assert rc != 0

    # New name should exist
    rc, out, _ = cli("template", "show", "new-name")
    assert rc == 0


def test_update_design_system(cli_with_template_dir, tmp_path):
    """Update-design-system replaces yaml."""
    cli, tmpl_dir = cli_with_template_dir

    src = str(tmp_path / "source.pptx")
    cli("create", src)
    _prepare_and_save(cli, tmpl_dir, "updatable", src, "Original")

    # Write new yaml
    new_yaml = str(tmp_path / "new-design.yaml")
    with open(new_yaml, "w") as f:
        f.write("description: Updated description\ncolors:\n  primary: '#FF0000'\n")

    rc, out, _ = cli("template", "update-design-system", "updatable", new_yaml)
    assert rc == 0
    data = json.loads(out)
    assert data["description"] == "Updated description"

    # Verify show reflects the new description
    rc, out, _ = cli("template", "show", "updatable")
    assert rc == 0
    show = json.loads(out)
    assert show["description"] == "Updated description"


def test_create_with_template_name(cli_with_template_dir, tmp_path):
    """Create a deck using a named template."""
    cli, tmpl_dir = cli_with_template_dir

    src = str(tmp_path / "tmpl-source.pptx")
    cli("create", src)
    _prepare_and_save(cli, tmpl_dir, "wide-tmpl", src)

    deck = str(tmp_path / "from-template.pptx")
    rc, out, _ = cli("create", deck, "--template", "wide-tmpl")
    assert rc == 0
    data = json.loads(out)
    assert data["template"] == "wide-tmpl"
    assert data["width"] == "13.33in"


def test_create_with_template_file(cli_with_template_dir, tmp_path):
    """Create a deck using a .pptx file path as template."""
    cli, _ = cli_with_template_dir

    src = str(tmp_path / "my-template.pptx")
    cli("create", src)

    deck = str(tmp_path / "from-file.pptx")
    rc, out, _ = cli("create", deck, "--template", src)
    assert rc == 0
    data = json.loads(out)
    assert data["template"] == src


def test_create_with_default_template(cli_with_template_dir, tmp_path):
    """Create uses default template when no --template specified."""
    cli, tmpl_dir = cli_with_template_dir

    src = str(tmp_path / "default-src.pptx")
    cli("create", src)
    _prepare_and_save(cli, tmpl_dir, "auto-tmpl", src)
    cli("template", "default", "auto-tmpl")

    deck = str(tmp_path / "auto.pptx")
    rc, out, _ = cli("create", deck)
    assert rc == 0
    data = json.loads(out)
    assert data["template"] == "auto-tmpl"
    assert data["width"] == "13.33in"


def test_template_invalid_name(cli_with_template_dir, tmp_path):
    """Template names must be kebab-case."""
    cli, _ = cli_with_template_dir

    src = str(tmp_path / "source.pptx")
    cli("create", src)

    rc, _, err = cli("template", "prepare", "Not Valid!", src)
    assert rc != 0
    assert "kebab" in err.lower()


def test_template_default_set_get_unset(cli_with_template_dir, tmp_path):
    """Set, get, and unset the default template."""
    cli, tmpl_dir = cli_with_template_dir

    src = str(tmp_path / "source.pptx")
    cli("create", src)
    _prepare_and_save(cli, tmpl_dir, "my-default", src)

    # Get default (none set)
    rc, out, _ = cli("template", "default")
    assert rc == 0
    assert json.loads(out)["default"] is None

    # Set default
    rc, out, _ = cli("template", "default", "my-default")
    assert rc == 0
    assert json.loads(out)["default"] == "my-default"

    # Verify
    rc, out, _ = cli("template", "default")
    assert rc == 0
    assert json.loads(out)["default"] == "my-default"

    # Unset
    rc, out, _ = cli("template", "default", "--unset")
    assert rc == 0
    assert json.loads(out)["default"] is None


def test_template_delete_unsets_default(cli_with_template_dir, tmp_path):
    """Deleting the default template unsets the default."""
    cli, tmpl_dir = cli_with_template_dir

    src = str(tmp_path / "source.pptx")
    cli("create", src)
    _prepare_and_save(cli, tmpl_dir, "def-tmpl", src)
    cli("template", "default", "def-tmpl")

    # Verify it's set
    rc, out, _ = cli("template", "default")
    assert json.loads(out)["default"] == "def-tmpl"

    # Delete it
    cli("template", "delete", "def-tmpl")

    # Default should be cleared
    rc, out, _ = cli("template", "default")
    assert json.loads(out)["default"] is None


def test_add_slide_with_layout(cli_with_template_dir, tmp_path):
    """Add a slide using --layout to target a specific layout."""
    cli, _ = cli_with_template_dir

    deck = str(tmp_path / "deck.pptx")
    cli("create", deck)

    rc, out, _ = cli("add-slide", deck, "--layout", "Blank")
    assert rc == 0
    data = json.loads(out)
    assert data["layout"] == "Blank"


def test_add_slide_layout_not_found(cli_with_template_dir, tmp_path):
    """Error when --layout name doesn't exist."""
    cli, _ = cli_with_template_dir

    deck = str(tmp_path / "deck.pptx")
    cli("create", deck)

    rc, _, err = cli("add-slide", deck, "--layout", "nonexistent-layout")
    assert rc != 0
    assert "not found" in err.lower()


# ── export / import tests ──


def test_export_produces_valid_zip(cli_with_template_dir, tmp_path):
    """Export produces a valid zip containing template.pptx and design-system.yaml."""
    cli, tmpl_dir = cli_with_template_dir

    src = str(tmp_path / "source.pptx")
    cli("create", src)
    _prepare_and_save(cli, tmpl_dir, "exportable", src, "Export test")

    rc, out, _ = cli("template", "export", "exportable")
    assert rc == 0
    data = json.loads(out)
    assert data["exported"] == "exportable"
    assert data["size"] > 0

    zip_path = data["output"]
    assert os.path.isfile(zip_path)
    with zipfile.ZipFile(zip_path) as zf:
        names = zf.namelist()
        assert "exportable/template.pptx" in names
        assert "exportable/design-system.yaml" in names


def test_export_default_filename(cli_with_template_dir, tmp_path):
    """Export default filename is <name>.zip in cwd."""
    cli, tmpl_dir = cli_with_template_dir

    src = str(tmp_path / "source.pptx")
    cli("create", src)
    _prepare_and_save(cli, tmpl_dir, "defname", src)

    rc, out, _ = cli("template", "export", "defname")
    assert rc == 0
    data = json.loads(out)
    assert data["output"].endswith("defname.zip")
    # cwd for the CLI is tmp_path
    assert os.path.dirname(data["output"]) == str(tmp_path)


def test_export_custom_output(cli_with_template_dir, tmp_path):
    """Export with -o writes to custom path."""
    cli, tmpl_dir = cli_with_template_dir

    src = str(tmp_path / "source.pptx")
    cli("create", src)
    _prepare_and_save(cli, tmpl_dir, "custom-out", src)

    custom = str(tmp_path / "my-export.zip")
    rc, out, _ = cli("template", "export", "custom-out", "-o", custom)
    assert rc == 0
    data = json.loads(out)
    assert data["output"] == custom
    assert os.path.isfile(custom)


def test_export_errors_if_not_found(cli_with_template_dir, tmp_path):
    """Export errors if template not found."""
    cli, _ = cli_with_template_dir

    rc, _, err = cli("template", "export", "nonexistent")
    assert rc != 0
    assert "not found" in err


def test_import_registers_template(cli_with_template_dir, tmp_path):
    """Import registers template from zip."""
    cli, tmpl_dir = cli_with_template_dir

    src = str(tmp_path / "source.pptx")
    cli("create", src)
    _prepare_and_save(cli, tmpl_dir, "importable", src, "Import test")

    # Export
    rc, out, _ = cli("template", "export", "importable")
    assert rc == 0
    zip_path = json.loads(out)["output"]

    # Delete original
    cli("template", "delete", "importable")

    # Import
    rc, out, _ = cli("template", "import", zip_path)
    assert rc == 0
    data = json.loads(out)
    assert data["imported"] == "importable"
    assert data["original_name"] == "importable"

    # Verify it's listed
    rc, out, _ = cli("template", "list", "--json")
    assert rc == 0
    templates = json.loads(out)
    assert any(t["name"] == "importable" for t in templates)


def test_import_uses_original_name(cli_with_template_dir, tmp_path):
    """Import uses original name from zip by default."""
    cli, tmpl_dir = cli_with_template_dir

    src = str(tmp_path / "source.pptx")
    cli("create", src)
    _prepare_and_save(cli, tmpl_dir, "orig-name", src)

    rc, out, _ = cli("template", "export", "orig-name")
    zip_path = json.loads(out)["output"]
    cli("template", "delete", "orig-name")

    rc, out, _ = cli("template", "import", zip_path)
    assert rc == 0
    assert json.loads(out)["imported"] == "orig-name"


def test_import_explicit_name(cli_with_template_dir, tmp_path):
    """Import with explicit name overrides the zip directory name."""
    cli, tmpl_dir = cli_with_template_dir

    src = str(tmp_path / "source.pptx")
    cli("create", src)
    _prepare_and_save(cli, tmpl_dir, "zip-name", src)

    rc, out, _ = cli("template", "export", "zip-name")
    zip_path = json.loads(out)["output"]
    cli("template", "delete", "zip-name")

    rc, out, _ = cli("template", "import", zip_path, "new-name")
    assert rc == 0
    data = json.loads(out)
    assert data["imported"] == "new-name"
    assert data["original_name"] == "zip-name"

    # Verify under new name
    rc, out, _ = cli("template", "show", "new-name")
    assert rc == 0


def test_import_errors_if_exists(cli_with_template_dir, tmp_path):
    """Import errors if name already exists."""
    cli, tmpl_dir = cli_with_template_dir

    src = str(tmp_path / "source.pptx")
    cli("create", src)
    _prepare_and_save(cli, tmpl_dir, "exists", src)

    rc, out, _ = cli("template", "export", "exists")
    zip_path = json.loads(out)["output"]

    rc, _, err = cli("template", "import", zip_path)
    assert rc != 0
    assert "already exists" in err


def test_import_errors_if_missing_pptx(cli_with_template_dir, tmp_path):
    """Import errors if zip missing template.pptx."""
    cli, _ = cli_with_template_dir

    # Create a zip with only design-system.yaml
    zip_path = str(tmp_path / "bad.zip")
    with zipfile.ZipFile(zip_path, "w") as zf:
        zf.writestr("bad-tmpl/design-system.yaml", "description: test\n")

    rc, _, err = cli("template", "import", zip_path)
    assert rc != 0
    assert "template.pptx" in err


def test_import_errors_if_missing_description(cli_with_template_dir, tmp_path):
    """Import errors if zip missing design-system.yaml description."""
    cli, tmpl_dir = cli_with_template_dir

    # Create a zip with template.pptx but no description in yaml
    src = str(tmp_path / "source.pptx")
    cli("create", src)

    zip_path = str(tmp_path / "no-desc.zip")
    with zipfile.ZipFile(zip_path, "w") as zf:
        zf.write(src, "no-desc/template.pptx")
        zf.writestr("no-desc/design-system.yaml", "fonts:\n  heading: Arial\n")

    rc, _, err = cli("template", "import", zip_path)
    assert rc != 0
    assert "description" in err


def test_import_validates_kebab_case(cli_with_template_dir, tmp_path):
    """Import validates kebab-case name."""
    cli, tmpl_dir = cli_with_template_dir

    src = str(tmp_path / "source.pptx")
    cli("create", src)
    _prepare_and_save(cli, tmpl_dir, "valid-name", src)

    rc, out, _ = cli("template", "export", "valid-name")
    zip_path = json.loads(out)["output"]
    cli("template", "delete", "valid-name")

    rc, _, err = cli("template", "import", zip_path, "Not Valid!")
    assert rc != 0
    assert "kebab" in err.lower()


def test_export_import_round_trip(cli_with_template_dir, tmp_path):
    """Round-trip: export -> delete -> import -> create --template works."""
    cli, tmpl_dir = cli_with_template_dir

    src = str(tmp_path / "source.pptx")
    cli("create", src)
    _prepare_and_save(cli, tmpl_dir, "round-trip", src, "Round trip test")

    # Export
    rc, out, _ = cli("template", "export", "round-trip")
    assert rc == 0
    zip_path = json.loads(out)["output"]

    # Delete
    cli("template", "delete", "round-trip")

    # Import
    rc, out, _ = cli("template", "import", zip_path)
    assert rc == 0

    # Create from imported template
    deck = str(tmp_path / "from-imported.pptx")
    rc, out, _ = cli("create", deck, "--template", "round-trip")
    assert rc == 0
    data = json.loads(out)
    assert data["template"] == "round-trip"
