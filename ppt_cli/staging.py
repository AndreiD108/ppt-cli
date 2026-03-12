"""Staging directory management for extracted .pptx files."""

import hashlib
import os
import shutil
import sys
import zipfile


def _staging_root():
    return "/tmp/ppt-cli"


def _staging_dir(filepath):
    """Return the staging directory path for a given .pptx file."""
    abspath = os.path.abspath(filepath)
    h = hashlib.sha256(abspath.encode()).hexdigest()[:16]
    return os.path.join(_staging_root(), h)


def _stage(filepath):
    """Extract a .pptx into its staging directory. Returns the directory path."""
    if not os.path.isfile(filepath):
        raise FileNotFoundError(f"file not found: {filepath}")
    staged = _staging_dir(filepath)
    if os.path.isdir(staged):
        shutil.rmtree(staged)
    os.makedirs(staged, exist_ok=True)
    with zipfile.ZipFile(filepath, "r") as zf:
        zf.extractall(staged)
    return staged


def _ensure_staged(filepath):
    """Auto-stage if the staging directory is missing. Returns the directory path."""
    staged = _staging_dir(filepath)
    if not os.path.isdir(staged):
        print(f"staging {filepath} ...", file=sys.stderr)
        return _stage(filepath)
    return staged


def _resolve_staged_or_file(path):
    """If path is a directory, return it as-is (assumed staged). Otherwise auto-stage."""
    if os.path.isdir(path):
        return path
    return _ensure_staged(path)
