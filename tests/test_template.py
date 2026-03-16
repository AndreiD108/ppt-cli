"""Tests for template commands and create --template integration."""

import json
import os


def test_template_save_and_list(cli_with_template_dir, tmp_path):
    """Save a template and list it."""
    cli, tmpl_dir = cli_with_template_dir

    # Create a source deck
    src = str(tmp_path / "source.pptx")
    rc, _, _ = cli("create", src)
    assert rc == 0

    # Save as template
    rc, out, _ = cli("template", "save", "my-template", src, "--description", "Test template")
    assert rc == 0
    data = json.loads(out)
    assert data["saved_template"] == "my-template"
    assert len(data["layouts"]) > 0

    # List templates
    rc, out, _ = cli("template", "list")
    assert rc == 0
    assert "my-template" in out


def test_template_list_json(cli_with_template_dir, tmp_path):
    """Template list --json returns structured data."""
    cli, _ = cli_with_template_dir

    src = str(tmp_path / "source.pptx")
    cli("create", src)
    cli("template", "save", "test-tmpl", src)

    rc, out, _ = cli("template", "list", "--json")
    assert rc == 0
    data = json.loads(out)
    assert len(data) == 1
    assert data[0]["name"] == "test-tmpl"


def test_template_show(cli_with_template_dir, tmp_path):
    """Show template details."""
    cli, _ = cli_with_template_dir

    src = str(tmp_path / "source.pptx")
    cli("create", src)
    cli("template", "save", "corp", src, "--description", "Corporate")

    rc, out, _ = cli("template", "show", "corp")
    assert rc == 0
    data = json.loads(out)
    assert data["name"] == "corp"
    assert data["description"] == "Corporate"
    assert "layouts" in data
    assert len(data["layouts"]) > 0


def test_template_delete(cli_with_template_dir, tmp_path):
    """Delete a template."""
    cli, tmpl_dir = cli_with_template_dir

    src = str(tmp_path / "source.pptx")
    cli("create", src)
    cli("template", "save", "to-delete", src)

    rc, out, _ = cli("template", "delete", "to-delete")
    assert rc == 0
    data = json.loads(out)
    assert data["deleted_template"] == "to-delete"

    # Verify it's gone
    rc, out, _ = cli("template", "show", "to-delete")
    assert rc != 0


def test_template_rename(cli_with_template_dir, tmp_path):
    """Rename a template."""
    cli, _ = cli_with_template_dir

    src = str(tmp_path / "source.pptx")
    cli("create", src)
    cli("template", "save", "old-name", src)

    rc, out, _ = cli("template", "rename", "old-name", "new-name", "--description", "Updated")
    assert rc == 0
    data = json.loads(out)
    assert data["renamed"] == "old-name"
    assert data["to"] == "new-name"

    # Old name should be gone
    rc, _, _ = cli("template", "show", "old-name")
    assert rc != 0

    # New name should exist
    rc, out, _ = cli("template", "show", "new-name")
    assert rc == 0
    show = json.loads(out)
    assert show["description"] == "Updated"


def test_template_default_set_get_unset(cli_with_template_dir, tmp_path):
    """Set, get, and unset the default template."""
    cli, _ = cli_with_template_dir

    src = str(tmp_path / "source.pptx")
    cli("create", src)
    cli("template", "save", "my-default", src)

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


def test_create_with_template_name(cli_with_template_dir, tmp_path):
    """Create a deck using a named template."""
    cli, _ = cli_with_template_dir

    # Create and save a template
    src = str(tmp_path / "tmpl-source.pptx")
    cli("create", src)
    cli("template", "save", "wide-tmpl", src)

    # Create from template
    deck = str(tmp_path / "from-template.pptx")
    rc, out, _ = cli("create", deck, "--template", "wide-tmpl")
    assert rc == 0
    data = json.loads(out)
    assert data["template"] == "wide-tmpl"
    assert data["width"] == "13.33in"


def test_create_with_template_file(cli_with_template_dir, tmp_path):
    """Create a deck using a .pptx file path as template."""
    cli, _ = cli_with_template_dir

    # Create a source template file
    src = str(tmp_path / "my-template.pptx")
    cli("create", src)

    # Create from file path
    deck = str(tmp_path / "from-file.pptx")
    rc, out, _ = cli("create", deck, "--template", src)
    assert rc == 0
    data = json.loads(out)
    assert data["template"] == src


def test_create_with_default_template(cli_with_template_dir, tmp_path):
    """Create uses default template when no --template specified."""
    cli, _ = cli_with_template_dir

    src = str(tmp_path / "default-src.pptx")
    cli("create", src)
    cli("template", "save", "auto-tmpl", src)
    cli("template", "default", "auto-tmpl")

    deck = str(tmp_path / "auto.pptx")
    rc, out, _ = cli("create", deck)
    assert rc == 0
    data = json.loads(out)
    assert data["template"] == "auto-tmpl"
    assert data["width"] == "13.33in"


def test_template_save_force_overwrite(cli_with_template_dir, tmp_path):
    """Save with -f overwrites existing template."""
    cli, _ = cli_with_template_dir

    src = str(tmp_path / "source.pptx")
    cli("create", src)
    cli("template", "save", "overwrite-me", src)

    # Save again without -f should fail
    rc, _, err = cli("template", "save", "overwrite-me", src)
    assert rc != 0
    assert "already exists" in err

    # Save with -f should succeed
    rc, out, _ = cli("template", "save", "overwrite-me", src, "-f")
    assert rc == 0


def test_template_invalid_name(cli_with_template_dir, tmp_path):
    """Template names must be kebab-case."""
    cli, _ = cli_with_template_dir

    src = str(tmp_path / "source.pptx")
    cli("create", src)

    rc, _, err = cli("template", "save", "Not Valid!", src)
    assert rc != 0
    assert "kebab" in err.lower()


def test_add_slide_with_layout(cli_with_template_dir, tmp_path):
    """Add a slide using --layout to target a specific layout."""
    cli, _ = cli_with_template_dir

    deck = str(tmp_path / "deck.pptx")
    cli("create", deck)

    # Add slide with specific layout
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


def test_template_delete_unsets_default(cli_with_template_dir, tmp_path):
    """Deleting the default template unsets the default."""
    cli, _ = cli_with_template_dir

    src = str(tmp_path / "source.pptx")
    cli("create", src)
    cli("template", "save", "def-tmpl", src)
    cli("template", "default", "def-tmpl")

    # Verify it's set
    rc, out, _ = cli("template", "default")
    assert json.loads(out)["default"] == "def-tmpl"

    # Delete it
    cli("template", "delete", "def-tmpl")

    # Default should be cleared
    rc, out, _ = cli("template", "default")
    assert json.loads(out)["default"] is None
