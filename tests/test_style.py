"""Tests for styling commands: set-font, set-fill, set-position."""

import json


def test_set_font(cli, deck_with_slide):
    path, _ = deck_with_slide
    # Add a textbox to style
    rc, out, _ = cli("add-textbox", path, "1", "Style me")
    data = json.loads(out)
    sid = data["shape_id"]

    rc, out, _ = cli("set-font", path, "1", "--shape-id", str(sid),
                      "--bold", "--size", "24", "--color", "#FF0000", "--name", "Arial")
    assert rc == 0

    # Verify via dump
    rc, out, _ = cli("dump", path, "1")
    dump = json.loads(out)
    shape = next(s for s in dump["shapes"] if s["id"] == sid)
    para = shape["text"][0]
    assert para["bold"] is True
    assert para["size"] == 24.0
    assert para["color"] == "#FF0000"


def test_set_fill(cli, deck_with_slide):
    path, _ = deck_with_slide
    rc, out, _ = cli("add-textbox", path, "1", "Fill me")
    data = json.loads(out)
    sid = data["shape_id"]

    rc, out, _ = cli("set-fill", path, "1", "--shape-id", str(sid),
                      "--color", "#00FF00")
    assert rc == 0
    assert json.loads(out)["saved"] == path


def test_set_position(cli, deck_with_slide):
    path, _ = deck_with_slide
    rc, out, _ = cli("add-textbox", path, "1", "Move me")
    data = json.loads(out)
    sid = data["shape_id"]

    rc, out, _ = cli("set-position", path, "1", "--shape-id", str(sid),
                      "--x", "2in", "--y", "3in", "--w", "5in", "--h", "2in")
    assert rc == 0

    # Verify new position via dump
    rc, out, _ = cli("dump", path, "1")
    dump = json.loads(out)
    shape = next(s for s in dump["shapes"] if s["id"] == sid)
    assert shape["position"]["x"] == "2.00in"
    assert shape["position"]["y"] == "3.00in"
    assert shape["position"]["w"] == "5.00in"
    assert shape["position"]["h"] == "2.00in"
