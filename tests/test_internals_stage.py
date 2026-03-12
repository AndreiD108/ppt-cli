"""Tests for internals stage, build, analyze, fingerprint commands."""

import json
import os


def test_stage(cli, tmp_pptx):
    """Stage extracts a .pptx into a directory."""
    cli("create", tmp_pptx)
    rc, out, _ = cli("internals", "stage", tmp_pptx)
    assert rc == 0
    data = json.loads(out)
    assert "staged" in data
    assert os.path.isdir(data["staged"])
    # Should contain [Content_Types].xml
    assert os.path.isfile(os.path.join(data["staged"], "[Content_Types].xml"))


def test_stage_contains_pptx_structure(cli, tmp_pptx):
    """Staged directory has standard OOXML structure."""
    cli("create", tmp_pptx)
    cli("add-slide", tmp_pptx, "--layout", "Title Slide")
    rc, out, _ = cli("internals", "stage", tmp_pptx)
    assert rc == 0
    staged = json.loads(out)["staged"]
    assert os.path.isfile(os.path.join(staged, "ppt", "presentation.xml"))
    assert os.path.isdir(os.path.join(staged, "ppt", "slides"))
    assert os.path.isdir(os.path.join(staged, "ppt", "slideLayouts"))
    assert os.path.isdir(os.path.join(staged, "ppt", "slideMasters"))


def test_build_roundtrip(cli, tmp_pptx, tmp_path):
    """Stage then build produces a valid .pptx with same content."""
    cli("create", tmp_pptx)
    cli("add-slide", tmp_pptx, "--layout", "Title Slide")
    cli("set-title", tmp_pptx, "1", "Hello Roundtrip")

    # Get info before
    rc, orig_info, _ = cli("info", tmp_pptx)
    assert rc == 0
    orig = json.loads(orig_info)

    # Stage
    rc, out, _ = cli("internals", "stage", tmp_pptx)
    assert rc == 0
    staged = json.loads(out)["staged"]

    # Build
    rebuilt = str(tmp_path / "rebuilt.pptx")
    rc, out, _ = cli("internals", "build", staged, rebuilt)
    assert rc == 0
    build_data = json.loads(out)
    assert build_data["built"] == rebuilt
    assert os.path.isfile(rebuilt)

    # Verify rebuilt file has same slide count and layouts
    rc, new_info, _ = cli("info", rebuilt)
    assert rc == 0
    new = json.loads(new_info)
    assert new["slides"] == orig["slides"]
    assert new["layouts"] == orig["layouts"]

    # Verify title preserved
    rc, peek, _ = cli("peek", rebuilt, "1")
    assert rc == 0
    assert "Hello Roundtrip" in peek


def test_build_clean(cli, tmp_pptx, tmp_path):
    """Build with --clean prunes unused layouts."""
    cli("create", tmp_pptx)
    cli("add-slide", tmp_pptx, "--layout", "Title Slide")

    rc, out, _ = cli("internals", "stage", tmp_pptx)
    staged = json.loads(out)["staged"]

    rebuilt = str(tmp_path / "clean.pptx")
    rc, out, stderr = cli("internals", "build", staged, rebuilt, "--clean")
    assert rc == 0
    assert os.path.isfile(rebuilt)


def test_analyze(cli, tmp_pptx):
    """Analyze shows layouts, masters, and slides."""
    cli("create", tmp_pptx)
    cli("add-slide", tmp_pptx, "--layout", "Title Slide")

    rc, out, _ = cli("internals", "analyze", tmp_pptx)
    assert rc == 0
    assert "Slides:" in out
    assert "Masters:" in out
    assert "Layouts:" in out


def test_analyze_json(cli, tmp_pptx):
    """Analyze --json produces structured output."""
    cli("create", tmp_pptx)
    cli("add-slide", tmp_pptx, "--layout", "Title Slide")

    rc, out, _ = cli("internals", "analyze", tmp_pptx, "--json")
    assert rc == 0
    data = json.loads(out)
    assert "slides" in data
    assert "layouts" in data
    assert "masters" in data
    assert "media" in data
    assert len(data["slides"]) == 1
    assert len(data["masters"]) >= 1
    assert len(data["layouts"]) >= 1


def test_fingerprint(cli, tmp_pptx):
    """Fingerprint shows shape details per slide."""
    cli("create", tmp_pptx)
    cli("add-slide", tmp_pptx, "--layout", "Title Slide")

    rc, out, _ = cli("internals", "fingerprint", tmp_pptx)
    assert rc == 0
    assert "Slide 1:" in out


def test_fingerprint_json(cli, tmp_pptx):
    """Fingerprint --json produces structured output."""
    cli("create", tmp_pptx)
    cli("add-slide", tmp_pptx, "--layout", "Title Slide")

    rc, out, _ = cli("internals", "fingerprint", tmp_pptx, "--json")
    assert rc == 0
    data = json.loads(out)
    assert len(data) == 1
    assert data[0]["slide"] == 1
    assert "shapes" in data[0]
    assert len(data[0]["shapes"]) > 0


def test_fingerprint_specific_slide(cli, tmp_pptx):
    """Fingerprint --slide N shows only that slide."""
    cli("create", tmp_pptx)
    cli("add-slide", tmp_pptx, "--layout", "Title Slide")
    cli("add-slide", tmp_pptx, "--layout", "Blank")

    rc, out, _ = cli("internals", "fingerprint", tmp_pptx, "--slide", "2", "--json")
    assert rc == 0
    data = json.loads(out)
    assert len(data) == 1
    assert data[0]["slide"] == 2
