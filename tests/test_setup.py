"""Tests for the first-run setup and skill installation flow."""

import hashlib
import json
import os
import stat
import subprocess
import sys

import pytest

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


@pytest.fixture
def setup_env(tmp_path):
    """Provide an isolated setup environment.

    Returns (run_fn, env_dict, paths_dict) where:
    - run_fn(*args, stdin=None) calls ppt-cli with isolated env
    - env_dict is the env passed to subprocesses (mutable)
    - paths_dict has install_json, skill_dir, skill_md, fake_bin
    """
    install_json = str(tmp_path / "install.json")
    skill_dir = str(tmp_path / "skill")
    skill_md = os.path.join(skill_dir, "SKILL.md")
    fake_bin = str(tmp_path / "bin")

    # Create skill dir with a dummy SKILL.md
    os.makedirs(skill_dir)
    with open(skill_md, "w") as f:
        f.write("---\nname: ppt-cli\ndescription: test\n---\n# ppt-cli\n")

    # Create fake npx that exits 0
    os.makedirs(fake_bin)
    npx_path = os.path.join(fake_bin, "npx")
    with open(npx_path, "w") as f:
        f.write("#!/bin/sh\nexit 0\n")
    os.chmod(npx_path, stat.S_IRWXU)

    env = {
        **os.environ,
        "PYTHONPATH": PROJECT_DIR,
        "PPT_CLI_INSTALL_JSON": install_json,
        "PPT_CLI_SKILL_DIR": skill_dir,
        "PATH": fake_bin + os.pathsep + os.environ.get("PATH", ""),
    }

    paths = {
        "install_json": install_json,
        "skill_dir": skill_dir,
        "skill_md": skill_md,
        "fake_bin": fake_bin,
    }

    def run(*args, stdin=None):
        result = subprocess.run(
            [sys.executable, "-m", "ppt_cli", *args],
            capture_output=True,
            text=True,
            cwd=str(tmp_path),
            env=env,
            input=stdin,
        )
        return result.returncode, result.stdout, result.stderr

    return run, env, paths


def _read_json(path):
    with open(path) as f:
        return json.load(f)


def _write_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f)


def _hash_file(path):
    with open(path) as f:
        return hashlib.sha256(f.read().encode()).hexdigest()


# ── Test 1: First run as human (interactive, TTY) ──────────────────────

def test_first_run_human(setup_env):
    """First run with a TTY runs npx and writes install.json."""
    run, env, paths = setup_env
    env["PPT_CLI_FORCE_TTY"] = "1"

    # Use 'create' as the actual command — it should succeed after setup
    pptx = os.path.join(os.path.dirname(paths["install_json"]), "deck.pptx")
    rc, out, err = run("create", pptx)

    assert rc == 0
    assert "Welcome to ppt-cli" in out

    # install.json should exist now
    data = _read_json(paths["install_json"])
    assert data["skill_installed"] is True
    assert data["skill_hash"] == _hash_file(paths["skill_md"])
    assert "ppt_cli_version" in data


# ── Test 2: First run as agent (no TTY, piped stdin) ───────────────────

def test_first_run_agent(setup_env):
    """First run without TTY prints guidance and exits non-zero."""
    run, env, paths = setup_env

    # Passing stdin="" makes isatty() return False
    rc, out, err = run("create", "deck.pptx", stdin="")

    assert rc != 0
    assert "ppt-cli setup" in err
    assert not os.path.exists(paths["install_json"])


# ── Test 3: Silent auto-update when SKILL.md hash changed ─────────────

def test_auto_update_hash_changed(setup_env):
    """Version mismatch + changed hash triggers silent auto-update."""
    run, env, paths = setup_env

    old_hash = _hash_file(paths["skill_md"])

    # Simulate a previous install with old version
    _write_json(paths["install_json"], {
        "ppt_cli_version": "0.0.1",
        "skill_installed": True,
        "skill_hash": "stale_hash_that_does_not_match",
        "installed_at": "2026-01-01T00:00:00+00:00",
    })

    pptx = os.path.join(os.path.dirname(paths["install_json"]), "deck.pptx")
    rc, out, err = run("create", pptx)

    assert rc == 0
    # install.json should be updated with new hash and version
    data = _read_json(paths["install_json"])
    assert data["skill_hash"] == old_hash
    assert data["ppt_cli_version"] != "0.0.1"


# ── Test 4: Version bump with unchanged SKILL.md ──────────────────────

def test_version_bump_hash_unchanged(setup_env):
    """Version mismatch + same hash just bumps version, no npx call."""
    run, env, paths = setup_env

    current_hash = _hash_file(paths["skill_md"])

    _write_json(paths["install_json"], {
        "ppt_cli_version": "0.0.1",
        "skill_installed": True,
        "skill_hash": current_hash,
        "installed_at": "2026-01-01T00:00:00+00:00",
    })

    # Remove fake npx to prove it's not called
    os.remove(os.path.join(paths["fake_bin"], "npx"))

    pptx = os.path.join(os.path.dirname(paths["install_json"]), "deck.pptx")
    rc, out, err = run("create", pptx)

    assert rc == 0
    data = _read_json(paths["install_json"])
    assert data["ppt_cli_version"] != "0.0.1"
    assert data["skill_hash"] == current_hash


# ── Test 5: Version bump with skill_installed=false ────────────────────

def test_version_bump_skill_not_installed(setup_env):
    """Version mismatch + skill_installed=false just bumps version, no nag."""
    run, env, paths = setup_env

    _write_json(paths["install_json"], {
        "ppt_cli_version": "0.0.1",
        "skill_installed": False,
        "skill_hash": "",
        "installed_at": "2026-01-01T00:00:00+00:00",
    })

    # Remove fake npx to prove it's not called
    os.remove(os.path.join(paths["fake_bin"], "npx"))

    pptx = os.path.join(os.path.dirname(paths["install_json"]), "deck.pptx")
    rc, out, err = run("create", pptx)

    assert rc == 0
    data = _read_json(paths["install_json"])
    assert data["ppt_cli_version"] != "0.0.1"
    assert data["skill_installed"] is False


# ── Test 6: ppt-cli setup re-run ──────────────────────────────────────

def test_setup_rerun(setup_env):
    """ppt-cli setup overwrites install.json with fresh data."""
    run, env, paths = setup_env
    env["PPT_CLI_FORCE_TTY"] = "1"

    # Pre-existing install.json with skill_installed=false
    _write_json(paths["install_json"], {
        "ppt_cli_version": "0.0.1",
        "skill_installed": False,
        "skill_hash": "",
        "installed_at": "2026-01-01T00:00:00+00:00",
    })

    rc, out, err = run("setup")

    assert rc == 0
    data = _read_json(paths["install_json"])
    assert data["skill_installed"] is True
    assert data["skill_hash"] == _hash_file(paths["skill_md"])


# ── Test 7: setup requires TTY ────────────────────────────────────────

def test_setup_no_tty(setup_env):
    """ppt-cli setup without TTY fails with an error."""
    run, env, paths = setup_env

    rc, out, err = run("setup", stdin="")

    assert rc != 0
    assert "interactive terminal" in err


# ── Test 8: Version matches — no work done ────────────────────────────

def test_version_matches_skips(setup_env):
    """When version matches, no install.json update occurs."""
    run, env, paths = setup_env

    from ppt_cli import __version__
    version = env.get("PPT_CLI_VERSION_OVERRIDE", __version__)

    original_data = {
        "ppt_cli_version": version,
        "skill_installed": True,
        "skill_hash": "whatever",
        "installed_at": "2026-01-01T00:00:00+00:00",
    }
    _write_json(paths["install_json"], original_data)

    # Remove fake npx to prove it's not called
    os.remove(os.path.join(paths["fake_bin"], "npx"))

    pptx = os.path.join(os.path.dirname(paths["install_json"]), "deck.pptx")
    rc, out, err = run("create", pptx)

    assert rc == 0
    data = _read_json(paths["install_json"])
    assert data["installed_at"] == "2026-01-01T00:00:00+00:00"  # untouched


# ── Test 9: --help shows setup hint when skill not installed ───────────

def test_help_shows_setup_hint(setup_env):
    """--help includes setup tip when skill_installed is false."""
    run, env, paths = setup_env

    _write_json(paths["install_json"], {
        "ppt_cli_version": "0.1.0",
        "skill_installed": False,
        "skill_hash": "",
        "installed_at": "2026-01-01T00:00:00+00:00",
    })

    rc, out, err = run("--help")

    assert "ppt-cli setup" in out


def test_help_no_hint_when_installed(setup_env):
    """--help does not include setup tip when skill is installed."""
    run, env, paths = setup_env

    _write_json(paths["install_json"], {
        "ppt_cli_version": "0.1.0",
        "skill_installed": True,
        "skill_hash": "abc",
        "installed_at": "2026-01-01T00:00:00+00:00",
    })

    rc, out, err = run("--help")

    assert "ppt-cli setup" not in out
