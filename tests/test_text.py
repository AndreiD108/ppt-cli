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


# ── Markdown formatting tests ──


def test_set_text_markdown_bold(cli, deck_with_slide):
    path, info = deck_with_slide
    sid = _title_shape_id(info)
    rc, out, _ = cli("set-text", path, "1", "--shape-id", str(sid),
                      "**Header** body")
    assert rc == 0

    rc, out, _ = cli("dump", path, "1")
    dump = json.loads(out)
    for s in dump["shapes"]:
        if s["id"] == sid and "text" in s:
            para = s["text"][0]
            assert para["text"] == "Header body"
            assert "runs" in para
            assert para["runs"][0]["text"] == "Header"
            assert para["runs"][0].get("bold") is True
            assert para["runs"][1].get("bold") is None
            return
    raise AssertionError("shape not found in dump")


def test_set_text_markdown_italic(cli, deck_with_slide):
    path, info = deck_with_slide
    sid = _title_shape_id(info)
    rc, out, _ = cli("set-text", path, "1", "--shape-id", str(sid),
                      "normal *emphasis* normal")
    assert rc == 0

    rc, out, _ = cli("dump", path, "1")
    dump = json.loads(out)
    for s in dump["shapes"]:
        if s["id"] == sid and "text" in s:
            para = s["text"][0]
            assert "runs" in para
            assert para["runs"][1]["text"] == "emphasis"
            assert para["runs"][1].get("italic") is True
            assert para["runs"][0].get("italic") is None
            return
    raise AssertionError("shape not found in dump")


def test_set_text_markdown_bold_italic(cli, deck_with_slide):
    path, info = deck_with_slide
    sid = _title_shape_id(info)
    rc, out, _ = cli("set-text", path, "1", "--shape-id", str(sid),
                      "***bold italic***")
    assert rc == 0

    rc, out, _ = cli("dump", path, "1")
    dump = json.loads(out)
    for s in dump["shapes"]:
        if s["id"] == sid and "text" in s:
            para = s["text"][0]
            assert para["text"] == "bold italic"
            assert para.get("bold") is True
            assert para.get("italic") is True
            return
    raise AssertionError("shape not found in dump")


def test_set_text_no_markdown_preserves_props(cli, deck_with_slide):
    """Plain text (no markdown) preserves original font properties."""
    path, info = deck_with_slide
    sid = _title_shape_id(info)
    # Set initial bold text
    rc, _, _ = cli("set-text", path, "1", "--shape-id", str(sid), "Bold")
    assert rc == 0
    # Make it bold via set-font
    cli("set-font", path, "1", "--shape-id", str(sid), "--bold")
    # Replace with plain text — should preserve bold
    rc, _, _ = cli("set-text", path, "1", "--shape-id", str(sid), "Still Bold")
    assert rc == 0

    rc, out, _ = cli("dump", path, "1")
    dump = json.loads(out)
    for s in dump["shapes"]:
        if s["id"] == sid and "text" in s:
            assert s["text"][0].get("bold") is True
            return
    raise AssertionError("shape not found in dump")


def test_replace_text_markdown_bold(cli, deck_with_slide):
    path, info = deck_with_slide
    sid = _title_shape_id(info)
    cli("set-text", path, "1", "--shape-id", str(sid), "Hello World")

    rc, out, err = cli("replace-text", path, "World", "**World**")
    assert rc == 0
    assert "replacements" in err

    rc, out, _ = cli("dump", path, "1")
    dump = json.loads(out)
    for s in dump["shapes"]:
        if s["id"] == sid and "text" in s:
            para = s["text"][0]
            assert para["text"] == "Hello World"
            assert "runs" in para
            # "Hello " is plain, "World" is bold
            bold_runs = [r for r in para["runs"] if r.get("bold")]
            assert len(bold_runs) == 1
            assert bold_runs[0]["text"] == "World"
            return
    raise AssertionError("shape not found in dump")


def test_replace_text_cross_run(cli, deck_with_slide):
    """replace-text finds text that spans multiple runs (e.g. from markdown)."""
    path, _ = deck_with_slide
    # Create a textbox with mixed formatting → multiple runs
    rc, out, _ = cli("add-textbox", path, "1", "lorem *ipsum* dolor")
    assert rc == 0
    sid = json.loads(out)["shape_id"]

    # Replace the full text which spans 3 runs
    rc, _, err = cli("replace-text", path, "lorem ipsum dolor", "replaced")
    assert rc == 0
    assert "replacements" in err

    rc, out, _ = cli("dump", path, "1")
    dump = json.loads(out)
    for s in dump["shapes"]:
        if s["id"] == sid and "text" in s:
            assert s["text"][0]["text"] == "replaced"
            return
    raise AssertionError("shape not found in dump")


def test_replace_text_formatted_search(cli, deck_with_slide):
    """**word** in search matches only bold runs."""
    path, _ = deck_with_slide
    # Create textbox with bold "important" and plain "important"
    rc, out, _ = cli("add-textbox", path, "1",
                      "**important** and also important")
    assert rc == 0
    sid = json.loads(out)["shape_id"]

    # Replace only the bold "important" → plain "critical"
    rc, _, err = cli("replace-text", path, "**important**", "critical")
    assert rc == 0

    rc, out, _ = cli("dump", path, "1")
    dump = json.loads(out)
    for s in dump["shapes"]:
        if s["id"] == sid and "text" in s:
            text = s["text"][0]["text"]
            assert text == "critical and also important"
            return
    raise AssertionError("shape not found in dump")
