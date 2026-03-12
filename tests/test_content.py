"""Tests for content commands: add-textbox, add-table, add-image, delete-shape."""

import json
import os


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
    # Create a minimal 1x1 PNG
    img_path = str(tmp_path / "pixel.png")
    import struct
    import zlib

    def _minimal_png():
        sig = b'\x89PNG\r\n\x1a\n'
        # IHDR
        ihdr_data = struct.pack('>IIBBBBB', 1, 1, 8, 2, 0, 0, 0)
        ihdr_crc = zlib.crc32(b'IHDR' + ihdr_data) & 0xFFFFFFFF
        ihdr = struct.pack('>I', 13) + b'IHDR' + ihdr_data + struct.pack('>I', ihdr_crc)
        # IDAT
        raw = zlib.compress(b'\x00\xff\x00\x00')
        idat_crc = zlib.crc32(b'IDAT' + raw) & 0xFFFFFFFF
        idat = struct.pack('>I', len(raw)) + b'IDAT' + raw + struct.pack('>I', idat_crc)
        # IEND
        iend_crc = zlib.crc32(b'IEND') & 0xFFFFFFFF
        iend = struct.pack('>I', 0) + b'IEND' + struct.pack('>I', iend_crc)
        return sig + ihdr + idat + iend

    with open(img_path, "wb") as f:
        f.write(_minimal_png())

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
