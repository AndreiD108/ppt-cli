"""Tests for inspection commands: info, list, dump, peek."""

import json


def test_info(cli, deck_with_slide):
    path, _ = deck_with_slide
    rc, out, _ = cli("info", path)
    assert rc == 0
    data = json.loads(out)
    assert data["slides"] == 1
    assert "width" in data
    assert "height" in data
    assert isinstance(data["layouts"], list)


def test_list(cli, deck_with_slide):
    path, _ = deck_with_slide
    rc, out, _ = cli("list", path)
    assert rc == 0
    data = json.loads(out)
    assert len(data) == 1
    assert data[0]["slide"] == 1
    assert "shapes" in data[0]


def test_dump_single_slide(cli, deck_with_slide):
    path, _ = deck_with_slide
    rc, out, _ = cli("dump", path, "1")
    assert rc == 0
    data = json.loads(out)
    assert data["slide_number"] == 1
    assert "shapes" in data
    assert "layout" in data


def test_dump_all(cli, deck_with_slide):
    path, _ = deck_with_slide
    # Add a second slide
    cli("add-slide", path)
    rc, out, _ = cli("dump", path, "--all")
    assert rc == 0
    data = json.loads(out)
    assert isinstance(data, list)
    assert len(data) == 2


def test_dump_requires_slide_or_all(cli, deck_with_slide):
    path, _ = deck_with_slide
    rc, _, err = cli("dump", path)
    assert rc != 0
    assert "specify" in err.lower() or "slide" in err.lower()


def test_peek_single_slide(cli, deck_with_slide):
    path, _ = deck_with_slide
    rc, out, _ = cli("peek", path, "1")
    assert rc == 0
    assert "slide 1:" in out
    assert "shapes)" in out


def test_peek_all(cli, deck_with_slide):
    path, _ = deck_with_slide
    cli("add-slide", path)
    rc, out, _ = cli("peek", path, "--all")
    assert rc == 0
    assert "slide 1:" in out
    assert "slide 2:" in out


def test_peek_default_is_all(cli, deck_with_slide):
    """peek with no slide number defaults to showing all slides."""
    path, _ = deck_with_slide
    rc, out, _ = cli("peek", path)
    assert rc == 0
    assert "slide 1:" in out
