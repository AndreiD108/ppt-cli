"""Tests for content commands: add-textbox, add-table, add-image, delete-shape."""

import json
import os
import struct
import subprocess
import sys
import zlib

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _write_minimal_png(path):
    """Write a minimal 1x1 PNG file."""
    sig = b'\x89PNG\r\n\x1a\n'
    ihdr_data = struct.pack('>IIBBBBB', 1, 1, 8, 2, 0, 0, 0)
    ihdr_crc = zlib.crc32(b'IHDR' + ihdr_data) & 0xFFFFFFFF
    ihdr = struct.pack('>I', 13) + b'IHDR' + ihdr_data + struct.pack('>I', ihdr_crc)
    raw = zlib.compress(b'\x00\xff\x00\x00')
    idat_crc = zlib.crc32(b'IDAT' + raw) & 0xFFFFFFFF
    idat = struct.pack('>I', len(raw)) + b'IDAT' + raw + struct.pack('>I', idat_crc)
    iend_crc = zlib.crc32(b'IEND') & 0xFFFFFFFF
    iend = struct.pack('>I', 0) + b'IEND' + struct.pack('>I', iend_crc)
    with open(path, "wb") as f:
        f.write(sig + ihdr + idat + iend)


def _cli_no_api_key(tmp_path):
    """Return a CLI runner with GEMINI_API_KEY explicitly removed."""
    from conftest import _setup_install_json
    env = {**os.environ, "PYTHONPATH": PROJECT_DIR,
           "PPT_CLI_INSTALL_JSON": _setup_install_json(tmp_path)}
    env.pop("GEMINI_API_KEY", None)

    def run(*args):
        result = subprocess.run(
            [sys.executable, "-m", "ppt_cli", *args],
            capture_output=True, text=True, cwd=str(tmp_path), env=env,
        )
        return result.returncode, result.stdout, result.stderr

    return run


def test_add_textbox(cli, deck_with_slide):
    path, _ = deck_with_slide
    rc, out, _ = cli("add-textbox", path, "1", "Hello textbox",
                      "--x", "1in", "--y", "2in", "--w", "4in", "--h", "1in")
    assert rc == 0
    data = json.loads(out)
    assert "shape_id" in data
    assert "name" in data

    # Verify text via dump
    rc, out, _ = cli("dump", path, "1")
    dump = json.loads(out)
    all_texts = []
    for s in dump["shapes"]:
        if "text" in s:
            for p in s["text"]:
                all_texts.append(p["text"])
    assert "Hello textbox" in all_texts


def test_add_textbox_with_style(cli, deck_with_slide):
    path, _ = deck_with_slide
    rc, out, _ = cli("add-textbox", path, "1", "Styled text",
                      "--font-size", "24", "--font-color", "#FF0000", "--bold")
    assert rc == 0
    data = json.loads(out)
    assert "shape_id" in data


def test_add_textbox_markdown_bold(cli, deck_with_slide):
    path, _ = deck_with_slide
    rc, out, _ = cli("add-textbox", path, "1", "**Header** body text")
    assert rc == 0
    data = json.loads(out)
    sid = data["shape_id"]

    rc, out, _ = cli("dump", path, "1")
    dump = json.loads(out)
    for s in dump["shapes"]:
        if s["id"] == sid:
            para = s["text"][0]
            assert para["text"] == "Header body text"
            assert "runs" in para
            assert para["runs"][0]["text"] == "Header"
            assert para["runs"][0].get("bold") is True
            assert para["runs"][1]["text"] == " body text"
            assert para["runs"][1].get("bold") is None
            return
    raise AssertionError("shape not found in dump")


def test_add_textbox_markdown_with_bold_flag(cli, deck_with_slide):
    """--bold flag makes everything bold; markdown bold stacks (both bold)."""
    path, _ = deck_with_slide
    rc, out, _ = cli("add-textbox", path, "1", "**Header** body",
                      "--bold")
    assert rc == 0
    data = json.loads(out)
    sid = data["shape_id"]

    rc, out, _ = cli("dump", path, "1")
    dump = json.loads(out)
    for s in dump["shapes"]:
        if s["id"] == sid:
            para = s["text"][0]
            # Both runs should be bold (--bold makes all bold)
            for r in para["runs"]:
                assert r.get("bold") is True
            return
    raise AssertionError("shape not found in dump")


def test_add_textbox_escaped_asterisk(cli, deck_with_slide):
    path, _ = deck_with_slide
    rc, out, _ = cli("add-textbox", path, "1", r"Price is \*not\* final")
    assert rc == 0
    data = json.loads(out)
    sid = data["shape_id"]

    rc, out, _ = cli("dump", path, "1")
    dump = json.loads(out)
    for s in dump["shapes"]:
        if s["id"] == sid:
            assert s["text"][0]["text"] == "Price is *not* final"
            return
    raise AssertionError("shape not found in dump")


def test_add_table(cli, deck_with_slide, tmp_path):
    path, _ = deck_with_slide
    csv_file = str(tmp_path / "data.csv")
    with open(csv_file, "w") as f:
        f.write("Name,Age\nAlice,30\nBob,25\n")

    rc, out, _ = cli("add-table", path, "1", csv_file)
    assert rc == 0
    data = json.loads(out)
    assert data["rows"] == 3
    assert data["cols"] == 2


def test_add_image(cli, deck_with_slide, tmp_path):
    path, _ = deck_with_slide
    img_path = str(tmp_path / "pixel.png")
    _write_minimal_png(img_path)

    rc, out, _ = cli("add-image", path, "1", img_path, "--x", "1in", "--y", "1in")
    assert rc == 0
    data = json.loads(out)
    assert "shape_id" in data


def test_delete_shape(cli, deck_with_slide):
    path, _ = deck_with_slide
    # Add a textbox, then delete it
    rc, out, _ = cli("add-textbox", path, "1", "To be deleted")
    data = json.loads(out)
    shape_id = data["shape_id"]

    rc, out, _ = cli("delete-shape", path, "1", "--shape-id", str(shape_id))
    assert rc == 0

    # Verify shape is gone
    rc, out, _ = cli("dump", path, "1")
    dump = json.loads(out)
    shape_ids = [s["id"] for s in dump["shapes"]]
    assert shape_id not in shape_ids


# ── add-image --prompt validation tests (no API calls) ──


def test_add_image_both_image_and_prompt(cli, deck_with_slide, tmp_path):
    """Error when both image path and --prompt are given."""
    path, _ = deck_with_slide
    img_path = str(tmp_path / "pixel.png")
    _write_minimal_png(img_path)
    rc, out, err = cli("add-image", path, "1", img_path, "--prompt", "a sunset")
    assert rc != 0
    assert "not both" in err.lower()


def test_add_image_neither_image_nor_prompt(cli, deck_with_slide):
    """Error when neither image path nor --prompt is given."""
    path, _ = deck_with_slide
    rc, out, err = cli("add-image", path, "1")
    assert rc != 0
    assert "image path or --prompt" in err.lower()


def test_add_image_resolution_without_prompt(cli, deck_with_slide, tmp_path):
    """Error when --resolution is used without --prompt."""
    path, _ = deck_with_slide
    img_path = str(tmp_path / "pixel.png")
    _write_minimal_png(img_path)
    rc, out, err = cli("add-image", path, "1", img_path, "--resolution", "2k")
    assert rc != 0
    assert "--prompt" in err


def test_add_image_ratio_without_prompt(cli, deck_with_slide, tmp_path):
    """Error when --ratio is used without --prompt."""
    path, _ = deck_with_slide
    img_path = str(tmp_path / "pixel.png")
    _write_minimal_png(img_path)
    rc, out, err = cli("add-image", path, "1", img_path, "--ratio", "16:9")
    assert rc != 0
    assert "--prompt" in err


def test_add_image_invalid_ratio(cli, deck_with_slide):
    """Error on unsupported --ratio value with --prompt."""
    path, _ = deck_with_slide
    rc, out, err = cli("add-image", path, "1", "--prompt", "a cat", "--ratio", "99:1")
    assert rc != 0
    assert "unsupported aspect ratio" in err.lower()


def test_add_image_prompt_without_api_key(tmp_path):
    """Error when --prompt is used without GEMINI_API_KEY."""
    run = _cli_no_api_key(tmp_path)
    pptx = str(tmp_path / "deck.pptx")
    run("create", pptx)
    run("add-slide", pptx, "--layout", "Title Slide")
    rc, out, err = run("add-image", pptx, "1", "--prompt", "a cat")
    assert rc != 0
    assert "GEMINI_API_KEY" in err


def test_add_image_ref_without_prompt(cli, deck_with_slide, tmp_path):
    """Error when --ref is used without --prompt."""
    path, _ = deck_with_slide
    img_path = str(tmp_path / "pixel.png")
    _write_minimal_png(img_path)
    rc, out, err = cli("add-image", path, "1", img_path, "--ref", img_path)
    assert rc != 0
    assert "--prompt" in err


def test_add_image_ref_too_many(cli, deck_with_slide, tmp_path):
    """Error when more than 14 reference images are passed."""
    path, _ = deck_with_slide
    paths = []
    for i in range(15):
        p = str(tmp_path / f"ref{i}.png")
        _write_minimal_png(p)
        paths.append(p)
    rc, out, err = cli("add-image", path, "1", "--prompt", "a cat", "--ref", *paths)
    assert rc != 0
    assert "14" in err


def test_add_image_ref_file_not_found(cli, deck_with_slide):
    """Error when a reference image does not exist."""
    path, _ = deck_with_slide
    rc, out, err = cli("add-image", path, "1", "--prompt", "a cat",
                       "--ref", "/nonexistent/img.png")
    assert rc != 0
    assert "not found" in err.lower()
