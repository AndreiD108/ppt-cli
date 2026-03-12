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
