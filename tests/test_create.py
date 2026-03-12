"""Tests for the 'create' command."""

import json
import os


def test_create_basic(cli, tmp_pptx):
    rc, out, err = cli("create", tmp_pptx)
    assert rc == 0
    assert os.path.isfile(tmp_pptx)
    data = json.loads(out)
    assert data["created"] == tmp_pptx
    assert "width" in data
    assert "height" in data
    assert isinstance(data["layouts"], list)


def test_create_widescreen(cli, tmp_pptx):
    rc, out, _ = cli("create", tmp_pptx, "--widescreen")
    assert rc == 0
    data = json.loads(out)
    assert data["width"] == "13.33in"
    assert data["height"] == "7.50in"


def test_create_custom_dimensions(cli, tmp_pptx):
    rc, out, _ = cli("create", tmp_pptx, "--width", "10in", "--height", "5in")
    assert rc == 0
    data = json.loads(out)
    assert data["width"] == "10.00in"
    assert data["height"] == "5.00in"


def test_create_refuses_overwrite(cli, tmp_pptx):
    cli("create", tmp_pptx)
    rc, _, err = cli("create", tmp_pptx)
    assert rc != 0
    assert "already exists" in err


def test_create_force_overwrite(cli, tmp_pptx):
    cli("create", tmp_pptx)
    rc, out, _ = cli("create", tmp_pptx, "--force")
    assert rc == 0
    data = json.loads(out)
    assert data["created"] == tmp_pptx
