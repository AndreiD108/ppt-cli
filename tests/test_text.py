"""Tests for text commands: set-text, set-title, set-notes, replace-text."""

import json


def _title_shape_id(slide_info):
    """Extract the title placeholder shape id from add-slide output."""
    for s in slide_info["shapes"]:
        if s["type"] == "placeholder" and "Title" in s["name"]:
            return s["id"]
    # Fallback: first placeholder
    for s in slide_info["shapes"]:
        if s["type"] == "placeholder":
            return s["id"]
    raise AssertionError(f"No placeholder found in {slide_info['shapes']}")


def test_set_text(cli, deck_with_slide):
    path, info = deck_with_slide
    sid = _title_shape_id(info)
    rc, out, _ = cli("set-text", path, "1", "--shape-id", str(sid), "Hello World")
    assert rc == 0
    data = json.loads(out)
    assert data["saved"] == path

    # Verify via dump
    rc, out, _ = cli("dump", path, "1")
    dump = json.loads(out)
    texts = [p["text"] for s in dump["shapes"] if "text" in s for p in s["text"]]
    assert "Hello World" in texts


def test_set_text_multiline(cli, deck_with_slide):
    path, info = deck_with_slide
    sid = _title_shape_id(info)
    rc, out, _ = cli("set-text", path, "1", "--shape-id", str(sid), "Line1\\nLine2")
    assert rc == 0

    rc, out, _ = cli("dump", path, "1")
    dump = json.loads(out)
    texts = [p["text"] for s in dump["shapes"] if "text" in s for p in s["text"]]
    assert "Line1" in texts
    assert "Line2" in texts


def test_set_title(cli, deck_with_slide):
    path, _ = deck_with_slide
    rc, out, _ = cli("set-title", path, "1", "My Title")
    assert rc == 0

    rc, out, _ = cli("peek", path, "1")
    assert "My Title" in out


def test_set_notes(cli, deck_with_slide):
    path, _ = deck_with_slide
    rc, out, _ = cli("set-notes", path, "1", "Speaker notes here")
    assert rc == 0

    rc, out, _ = cli("dump", path, "1")
    dump = json.loads(out)
    assert dump["notes"] == "Speaker notes here"


def test_replace_text(cli, deck_with_slide):
    path, info = deck_with_slide
    sid = _title_shape_id(info)
    cli("set-text", path, "1", "--shape-id", str(sid), "Hello World")

    rc, out, err = cli("replace-text", path, "Hello", "Goodbye")
    assert rc == 0
    # replace-text prints replacements to stderr
    assert "replacements" in err

    rc, out, _ = cli("dump", path, "1")
    dump = json.loads(out)
    texts = [p["text"] for s in dump["shapes"] if "text" in s for p in s["text"]]
    assert any("Goodbye" in t for t in texts)


def test_replace_text_not_found(cli, deck_with_slide):
    path, _ = deck_with_slide
    rc, _, err = cli("replace-text", path, "NONEXISTENT", "replacement")
    assert rc != 0
    assert "not found" in err
