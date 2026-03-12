"""Tests for internals delete, duplicate, and add commands."""

import json
import os


def test_delete_slide(cli, tmp_pptx):
    """Delete a slide from a staged deck."""
    cli("create", tmp_pptx)
    cli("add-slide", tmp_pptx, "--layout", "Title Slide")

    # Stage first
    rc, out, _ = cli("internals", "stage", tmp_pptx)
    assert rc == 0
    staged = json.loads(out)["staged"]

    rc, out, _ = cli("internals", "delete", "slide", staged, "--slide", "1")
    assert rc == 0
    data = json.loads(out)
    assert data["deleted"] == "slide"
    assert data["slides_remaining"] == 0


def test_delete_slide_via_cli(cli, tmp_pptx):
    """Delete slide using .pptx path (auto-stages)."""
    cli("create", tmp_pptx)
    cli("add-slide", tmp_pptx, "--layout", "Title Slide")
    cli("add-slide", tmp_pptx, "--layout", "Blank")

    rc, out, _ = cli("internals", "delete", "slide", tmp_pptx, "--slide", "1")
    assert rc == 0
    data = json.loads(out)
    assert data["deleted"] == "slide"
    assert data["slides_remaining"] == 1


def test_delete_layout(cli, tmp_pptx, tmp_path):
    """Delete an unused layout."""
    cli("create", tmp_pptx)
    # Add a slide with Title Slide layout, then try to delete Blank layout (unused)
    cli("add-slide", tmp_pptx, "--layout", "Title Slide")

    # Stage first to get layout names
    rc, out, _ = cli("internals", "analyze", tmp_pptx, "--json")
    assert rc == 0
    data = json.loads(out)
    layout_names = [l["name"] for l in data["layouts"]]
    # Find a layout that is unused (used_by_slides == 0)
    unused = [l for l in data["layouts"] if l["used_by_slides"] == 0]
    assert len(unused) > 0, f"No unused layouts found in {layout_names}"

    target = unused[0]["name"]
    rc, out, _ = cli("internals", "delete", "layout", tmp_pptx, "--layout", target)
    assert rc == 0
    data = json.loads(out)
    assert data["deleted"] == "layout"
    assert data["layout"] == target


def test_delete_layout_in_use_fails(cli, tmp_pptx):
    """Cannot delete a layout that is used by a slide."""
    cli("create", tmp_pptx)
    cli("add-slide", tmp_pptx, "--layout", "Title Slide")

    rc, out, err = cli("internals", "delete", "layout", tmp_pptx, "--layout", "Title Slide")
    assert rc != 0
    assert "in use" in err


def test_duplicate_slide(cli, tmp_pptx, tmp_path):
    """Duplicate a slide at the OOXML level."""
    cli("create", tmp_pptx)
    cli("add-slide", tmp_pptx, "--layout", "Title Slide")
    cli("set-title", tmp_pptx, "1", "Original Title")

    rc, out, _ = cli("internals", "duplicate", "slide", tmp_pptx, "--slide", "1")
    assert rc == 0
    data = json.loads(out)
    assert data["duplicated"] == "slide"
    assert data["source_slide"] == 1

    # Build and verify 2 slides
    staged = data["staged"]
    rebuilt = str(tmp_path / "rebuilt.pptx")
    rc, out, _ = cli("internals", "build", staged, rebuilt)
    assert rc == 0

    rc, info_out, _ = cli("info", rebuilt)
    assert rc == 0
    info = json.loads(info_out)
    assert info["slides"] == 2


def test_duplicate_layout(cli, tmp_pptx, tmp_path):
    """Duplicate a layout."""
    cli("create", tmp_pptx)
    cli("add-slide", tmp_pptx, "--layout", "Title Slide")

    rc, out, _ = cli("internals", "duplicate", "layout", tmp_pptx,
                      "--source", "Title Slide", "--name", "Title Slide Copy")
    assert rc == 0
    data = json.loads(out)
    assert data["duplicated"] == "layout"
    assert data["name"] == "Title Slide Copy"

    # Build and verify new layout exists
    staged = data["staged"]
    rebuilt = str(tmp_path / "rebuilt.pptx")
    rc, out, _ = cli("internals", "build", staged, rebuilt)
    assert rc == 0

    rc, info_out, _ = cli("info", rebuilt)
    info = json.loads(info_out)
    assert "Title Slide Copy" in info["layouts"]


def test_duplicate_master(cli, tmp_pptx, tmp_path):
    """Duplicate a slide master."""
    cli("create", tmp_pptx)

    rc, out, _ = cli("internals", "duplicate", "master", tmp_pptx,
                      "--master", "1", "--name", "Custom Master")
    assert rc == 0
    data = json.loads(out)
    assert data["duplicated"] == "master"
    assert data["new_name"] == "Custom Master"

    # Build and verify
    staged = data["staged"]
    rebuilt = str(tmp_path / "rebuilt.pptx")
    rc, out, _ = cli("internals", "build", staged, rebuilt)
    assert rc == 0

    # Analyze to verify 2 masters
    rc, out, _ = cli("internals", "analyze", rebuilt, "--json")
    assert rc == 0
    analyze = json.loads(out)
    assert len(analyze["masters"]) == 2


def test_add_layout(cli, tmp_pptx, tmp_path):
    """Add a new blank layout to a master."""
    cli("create", tmp_pptx)

    rc, out, _ = cli("internals", "add", "layout", tmp_pptx,
                      "--name", "My Custom Layout", "--master", "1")
    assert rc == 0
    data = json.loads(out)
    assert data["added"] == "layout"
    assert data["name"] == "My Custom Layout"

    # Build and verify
    staged = data["staged"]
    rebuilt = str(tmp_path / "rebuilt.pptx")
    rc, out, _ = cli("internals", "build", staged, rebuilt)
    assert rc == 0

    rc, info_out, _ = cli("info", rebuilt)
    info = json.loads(info_out)
    assert "My Custom Layout" in info["layouts"]


def test_delete_master(cli, tmp_pptx, tmp_path):
    """Delete a slide master (requires duplicating first so we have 2)."""
    cli("create", tmp_pptx)

    # First duplicate to get 2 masters
    rc, out, _ = cli("internals", "duplicate", "master", tmp_pptx,
                      "--master", "1", "--name", "Extra Master")
    assert rc == 0
    staged = json.loads(out)["staged"]

    # Now delete master 2
    rc, out, _ = cli("internals", "delete", "master", staged, "--master", "2")
    assert rc == 0
    data = json.loads(out)
    assert data["deleted"] == "master"

    # Build and verify 1 master
    rebuilt = str(tmp_path / "rebuilt.pptx")
    rc, out, _ = cli("internals", "build", staged, rebuilt)
    assert rc == 0

    rc, out, _ = cli("internals", "analyze", rebuilt, "--json")
    analyze = json.loads(out)
    assert len(analyze["masters"]) == 1


def test_delete_last_master_fails(cli, tmp_pptx):
    """Cannot delete the only master."""
    cli("create", tmp_pptx)

    rc, out, err = cli("internals", "delete", "master", tmp_pptx, "--master", "1")
    assert rc != 0
    assert "last" in err.lower()
