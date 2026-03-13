"""Validation tests for image-gen command (no API calls)."""

import os
import subprocess
import sys

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _cli_no_api_key(tmp_path):
    """Return a CLI runner with GEMINI_API_KEY explicitly removed."""
    env = {**os.environ, "PYTHONPATH": PROJECT_DIR}
    env.pop("GEMINI_API_KEY", None)

    def run(*args):
        result = subprocess.run(
            [sys.executable, "-m", "ppt_cli", *args],
            capture_output=True, text=True, cwd=str(tmp_path), env=env,
        )
        return result.returncode, result.stdout, result.stderr

    return run


def test_image_gen_missing_prompt(cli):
    """Error when no prompt is given (positional arg)."""
    rc, out, err = cli("image-gen")
    assert rc != 0
    assert "required" in err.lower() or "arguments" in err.lower()


def test_image_gen_invalid_ratio(cli):
    """Error on unsupported --ratio value."""
    rc, out, err = cli("image-gen", "a cat", "--ratio", "99:1")
    assert rc != 0
    assert "unsupported aspect ratio" in err.lower()


def test_image_gen_missing_api_key(tmp_path):
    """Error when GEMINI_API_KEY is not set."""
    run = _cli_no_api_key(tmp_path)
    rc, out, err = run("image-gen", "a cat")
    assert rc != 0
    assert "GEMINI_API_KEY" in err


def test_image_gen_invalid_resolution(cli):
    """Error on invalid --resolution value."""
    rc, out, err = cli("image-gen", "a cat", "--resolution", "4k")
    assert rc != 0


def test_image_gen_count_zero(cli):
    """Error when --count is 0."""
    rc, out, err = cli("image-gen", "a cat", "--count", "0")
    assert rc != 0
    assert "count" in err.lower()


def test_image_gen_count_negative(cli):
    """Error when --count is negative."""
    rc, out, err = cli("image-gen", "a cat", "--count", "-1")
    assert rc != 0
    assert "count" in err.lower()
