"""Tests for structural commands: add-slide, delete-slide, reorder, duplicate-slide."""

import json


def test_add_slide_default_layout(cli, tmp_pptx):
    cli("create", tmp_pptx)
    rc, out, _ = cli("add-slide", tmp_pptx)
    assert rc == 0
    data = json.loads(out)
    assert "slide" in data
    assert "layout" in data
    assert "shapes" in data


def test_add_slide_named_layout(cli, tmp_pptx):
    cli("create", tmp_pptx)
    rc, out, _ = cli("add-slide", tmp_pptx, "--layout", "Blank")
    assert rc == 0
    data = json.loads(out)
    assert data["layout"] == "Blank"


def test_add_slide_at_position(cli, tmp_pptx):
    cli("create", tmp_pptx)
    cli("add-slide", tmp_pptx, "--layout", "Title Slide")
    cli("add-slide", tmp_pptx, "--layout", "Blank")
    # Insert a third slide at position 1
    rc, out, _ = cli("add-slide", tmp_pptx, "--layout", "Blank", "--at", "1")
    assert rc == 0
    data = json.loads(out)
    assert data["slide"] == 1

    # Verify 3 slides total
    rc, out, _ = cli("list", tmp_pptx)
    slides = json.loads(out)
    assert len(slides) == 3


def test_delete_slide(cli, tmp_pptx):
    cli("create", tmp_pptx)
    cli("add-slide", tmp_pptx)
    cli("add-slide", tmp_pptx)
    rc, out, _ = cli("delete-slide", tmp_pptx, "1")
    assert rc == 0
    data = json.loads(out)
    assert data["deleted_slide"] == 1
    assert data["slides_remaining"] == 1


def test_delete_slide_out_of_range(cli, tmp_pptx):
    cli("create", tmp_pptx)
    cli("add-slide", tmp_pptx)
    rc, _, err = cli("delete-slide", tmp_pptx, "5")
    assert rc != 0
    assert "out of range" in err


def test_reorder(cli, tmp_pptx):
    cli("create", tmp_pptx)
    cli("add-slide", tmp_pptx, "--layout", "Title Slide")
    cli("set-title", tmp_pptx, "1", "First")
    cli("add-slide", tmp_pptx, "--layout", "Title Slide")
    cli("set-title", tmp_pptx, "2", "Second")

    rc, out, _ = cli("reorder", tmp_pptx, "2", "--to", "1")
    assert rc == 0

    # Verify the order changed
    rc, out, _ = cli("peek", tmp_pptx, "1")
    assert "Second" in out


def test_duplicate_slide(cli, deck_with_slide):
    path, info = deck_with_slide
    # Set title so we can verify the duplicate
    cli("set-title", path, "1", "Original")

    rc, out, _ = cli("duplicate-slide", path, "1")
    assert rc == 0
    data = json.loads(out)
    assert data["new_slide"] == 2

    # Verify 2 slides now
    rc, out, _ = cli("list", path)
    slides = json.loads(out)
    assert len(slides) == 2
