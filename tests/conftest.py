"""Shared fixtures for ppt-cli tests."""

import json
import os
import subprocess
import sys

import pytest

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


@pytest.fixture
def cli(tmp_path):
    """Return a helper that runs ppt_cli and returns (returncode, stdout, stderr)."""

    def run(*args):
        result = subprocess.run(
            [sys.executable, "-m", "ppt_cli", *args],
            capture_output=True,
            text=True,
            cwd=str(tmp_path),
            env={**os.environ, "PYTHONPATH": PROJECT_DIR},
        )
        return result.returncode, result.stdout, result.stderr

    return run


@pytest.fixture
def tmp_pptx(tmp_path):
    """Return a path to a fresh .pptx inside tmp_path (not yet created)."""
    return str(tmp_path / "test.pptx")


@pytest.fixture
def deck_with_slide(cli, tmp_pptx):
    """Create a deck with one 'Title Slide' and return (path, slide1_info).

    slide1_info is the parsed JSON from the add-slide command.
    """
    cli("create", tmp_pptx)
    rc, out, _ = cli("add-slide", tmp_pptx, "--layout", "Title Slide")
    assert rc == 0, f"add-slide failed: {out}"
    info = json.loads(out)
    return tmp_pptx, info


@pytest.fixture
def deck_with_hidden_slide(cli, tmp_pptx):
    """Create a deck with 2 slides, slide 2 hidden. Returns path."""
    from pptx import Presentation
    cli("create", tmp_pptx)
    cli("add-slide", tmp_pptx, "--layout", "Title Slide")
    cli("add-slide", tmp_pptx)
    prs = Presentation(tmp_pptx)
    prs.slides[1]._element.attrib["show"] = "0"
    prs.save(tmp_pptx)
    return tmp_pptx


@pytest.fixture
def staged_deck(cli, tmp_pptx):
    """Create, add a slide, and stage a deck. Returns (pptx_path, staged_dir)."""
    cli("create", tmp_pptx)
    cli("add-slide", tmp_pptx, "--layout", "Title Slide")
    rc, out, _ = cli("internals", "stage", tmp_pptx)
    assert rc == 0, f"stage failed: {out}"
    data = json.loads(out)
    return tmp_pptx, data["staged"]


@pytest.fixture
def cli_with_template_dir(tmp_path):
    """CLI fixture with isolated template directory. Returns (run_fn, template_dir)."""
    tmpl_dir = str(tmp_path / "templates")

    def run(*args):
        result = subprocess.run(
            [sys.executable, "-m", "ppt_cli", *args],
            capture_output=True,
            text=True,
            cwd=str(tmp_path),
            env={**os.environ, "PYTHONPATH": PROJECT_DIR, "PPT_CLI_TEMPLATE_DIR": tmpl_dir},
        )
        return result.returncode, result.stdout, result.stderr

    return run, tmpl_dir
